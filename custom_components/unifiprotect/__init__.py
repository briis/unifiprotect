"""Unifi Protect Platform."""

import asyncio
from datetime import timedelta
import logging

from aiohttp import CookieJar

from pyunifiprotect import UpvServer, NotAuthorized, NvrError

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_ID,
    CONF_HOST,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FILENAME,
    CONF_SCAN_INTERVAL,
    ATTR_ENTITY_ID,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import homeassistant.helpers.device_registry as dr

from .const import (
    ATTR_CAMERA_ID,
    CONF_THUMB_WIDTH,
    CONF_RECORDING_MODE,
    CONF_IR_MODE,
    DEFAULT_THUMB_WIDTH,
    DEFAULT_BRAND,
    DOMAIN,
    SERVICE_SAVE_THUMBNAIL,
    SERVICE_SET_RECORDING_MODE,
    SERVICE_SET_IR_MODE,
    SAVE_THUMBNAIL_SCHEMA,
    SET_RECORDING_MODE_SCHEMA,
    SET_IR_MODE_SCHEMA,
    TYPE_IR_AUTO,
    TYPE_RECORD_MOTION,
    UNIFI_PROTECT_PLATFORMS,
)

SCAN_INTERVAL = timedelta(seconds=2)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up the Unifi Protect components."""

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Set up the Unifi Protect config entries."""

    session = async_create_clientsession(hass, cookie_jar=CookieJar(unsafe=True))
    protectserver = UpvServer(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = protectserver

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=protectserver.update,
        update_interval=SCAN_INTERVAL,
    )

    try:
        nvr_info = await protectserver.server_information()
    except NotAuthorized:
        _LOGGER.error(
            "Could not Authorize against Unifi Protect. Please reinstall the Integration."
        )
        return
    except NvrError:
        raise ConfigEntryNotReady

    await coordinator.async_refresh()
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "upv": protectserver,
    }

    await _async_get_or_create_nvr_device_in_registry(hass, entry, nvr_info)

    async def async_set_recording_mode(call):
        """Call Set Recording Mode."""
        await async_handle_set_recording_mode(
            hass, call, hass.data[DOMAIN][entry.entry_id]
        )

    async def async_save_thumbnail(call):
        """Call save video service handler."""
        await async_handle_save_thumbnail_service(
            hass, call, hass.data[DOMAIN][entry.entry_id]
        )

    async def async_set_ir_mode(call):
        """Call Set Infrared Mode."""
        await async_handle_set_ir_mode(hass, call, hass.data[DOMAIN][entry.entry_id])

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_RECORDING_MODE,
        async_set_recording_mode,
        schema=SET_RECORDING_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SAVE_THUMBNAIL,
        async_save_thumbnail,
        schema=SAVE_THUMBNAIL_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_IR_MODE, async_set_ir_mode, schema=SET_IR_MODE_SCHEMA,
    )

    for platform in UNIFI_PROTECT_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    return True


async def _async_get_or_create_nvr_device_in_registry(
    hass: HomeAssistantType, entry: ConfigEntry, nvr
) -> None:
    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, nvr["server_id"])},
        identifiers={(DOMAIN, nvr["server_id"])},
        manufacturer=DEFAULT_BRAND,
        name=entry.data[CONF_ID],
        model=nvr["server_model"],
        sw_version=nvr["server_version"],
    )


async def async_handle_set_recording_mode(hass, call, server):
    """Handle setting Recording Mode."""
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    rec_mode = call.data[CONF_RECORDING_MODE].lower()
    if rec_mode not in {"always", "motion", "never"}:
        rec_mode = "motion"

    await server["upv"].set_camera_recording(camera_id, rec_mode)


async def async_handle_set_ir_mode(hass, call, server):
    """Handle enable Always recording."""
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    ir_mode = call.data[CONF_IR_MODE].lower()
    if ir_mode not in {"always_on", "auto", "always_off", "led_off"}:
        ir_mode = "auto"

    await server["upv"].set_camera_ir(camera_id, ir_mode)


async def async_handle_save_thumbnail_service(hass, call, server):
    """Handle save thumbnail service calls."""
    # Get the Camera ID from Entity_id
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    # Get other input from the service call
    filename = call.data[CONF_FILENAME]
    image_width = call.data[CONF_THUMB_WIDTH]

    if not hass.config.is_allowed_path(filename):
        _LOGGER.error(f"Can't write {filename}, no access to path!")
        return

    async def _write_thumbnail(camera_id, filename, image_width, server):
        """Call thumbnail write."""
        image_data = await server["upv"].get_thumbnail(camera_id, image_width)
        if image_data is None:
            _LOGGER.warning(
                f"Last recording not found for Camera {entity_state.attributes['friendly_name']}"
            )
            return False
        # We got an image, now write the image to disk
        with open(filename, "wb") as img_file:
            img_file.write(image_data)
            _LOGGER.debug(f"Thumbnail Image written to {filename}")

    try:
        await _write_thumbnail(camera_id, filename, image_width, server)
    except OSError as err:
        _LOGGER.error(f"Can't write image to file: {err}")


async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Unload Unifi Protect config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in UNIFI_PROTECT_PLATFORMS
            ]
        )
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
