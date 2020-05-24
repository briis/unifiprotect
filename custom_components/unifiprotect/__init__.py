"""Unifi Protect Platform."""

import asyncio
from datetime import timedelta
import logging
from typing import Optional

import voluptuous as vol
from aiohttp import CookieJar

from pyunifiprotect import UpvServer, NotAuthorized, NvrError

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_ID,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FILENAME,
    CONF_SCAN_INTERVAL,
    ATTR_ENTITY_ID,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import config_validation as cv
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
    TYPE_IR_AUTO,
    TYPE_RECORD_MOTION,
    UNIFI_PROTECT_PLATFORMS,
)

SCAN_INTERVAL = timedelta(seconds=2)

_LOGGER = logging.getLogger(__name__)

SERVICE_SAVE_THUMBNAIL = "save_thumbnail_image"
SERVICE_SET_RECORDING_MODE = "set_recording_mode"
SERVICE_SET_IR_MODE = "set_ir_mode"

SAVE_THUMBNAIL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_FILENAME): cv.string,
        vol.Optional(CONF_THUMB_WIDTH, default=DEFAULT_THUMB_WIDTH): cv.string,
    }
)

SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=TYPE_RECORD_MOTION): cv.string,
    }
)

SET_IR_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_IR_MODE, default=TYPE_IR_AUTO): cv.string,
    }
)


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

    unique_id = entry.data[CONF_ID]

    hass.data.setdefault(DOMAIN, {})[unique_id] = protectserver

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=protectserver.update,
        update_interval=SCAN_INTERVAL,
    )
    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()
    hass.data[DOMAIN][entry.data[CONF_ID]] = {
        "coordinator": coordinator,
        "upv": protectserver,
    }

    nvr_info = await protectserver.server_information()
    await _async_get_or_create_nvr_device_in_registry(hass, entry, nvr_info)

    async def async_set_recording_mode(call):
        """Call Set Recording Mode."""
        await async_handle_set_recording_mode(
            hass, call, hass.data[DOMAIN][entry.data[CONF_ID]]
        )

    async def async_save_thumbnail(call):
        """Call save video service handler."""
        await async_handle_save_thumbnail_service(
            hass, call, hass.data[DOMAIN][entry.data[CONF_ID]]
        )

    async def async_set_ir_mode(call):
        """Call Set Infrared Mode."""
        await async_handle_set_ir_mode(
            hass, call, hass.data[DOMAIN][entry.data[CONF_ID]]
        )

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
    _LOGGER.debug(f"ENTRY ID: {entry.entry_id}")
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
        _LOGGER.error("Can't write %s, no access to path!", filename)
        return

    async def _write_thumbnail(camera_id, filename, image_width, server):
        """Call thumbnail write."""
        image_data = await server["upv"].get_thumbnail(camera_id, image_width)
        if image_data is None:
            _LOGGER.warning(
                "Last recording not found for Camera %s",
                entity_state.attributes["friendly_name"],
            )
            return False
        # We got an image, now write the image to disk
        with open(filename, "wb") as img_file:
            img_file.write(image_data)
            _LOGGER.debug("Thumbnail Image written to %s", filename)

    try:
        await _write_thumbnail(camera_id, filename, image_width, server)
    except OSError as err:
        _LOGGER.error("Can't write image to file: %s", err)


async def async_unload_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
    """Unload Unifi Protect config entry."""
    for platform in UNIFI_PROTECT_PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, platform)

    del hass.data[DOMAIN][entry.data[CONF_ID]]

    return True
