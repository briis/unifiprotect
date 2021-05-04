"""Unifi Protect Platform."""

import asyncio
from datetime import timedelta
import logging

from aiohttp import CookieJar
from aiohttp.client_exceptions import ServerDisconnectedError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.typing import ConfigType
from pyunifiprotect import NotAuthorized, NvrError, UpvServer
from pyunifiprotect.const import SERVER_ID

from .const import (
    CONF_DISABLE_RTSP,
    CONF_SNAPSHOT_DIRECT,
    DEFAULT_BRAND,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    UNIFI_PROTECT_PLATFORMS,
)
from .data import UnifiProtectData

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Unifi Protect components."""

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Unifi Protect config entries."""

    if not entry.options:
        hass.config_entries.async_update_entry(
            entry,
            options={
                CONF_SCAN_INTERVAL: entry.data.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
                CONF_SNAPSHOT_DIRECT: entry.data.get(CONF_SNAPSHOT_DIRECT, False),
            },
        )
    if not entry.options.get(CONF_DISABLE_RTSP):
        hass.config_entries.async_update_entry(
            entry, options={CONF_DISABLE_RTSP: entry.data.get(CONF_DISABLE_RTSP, False)}
        )

    session = async_create_clientsession(hass, cookie_jar=CookieJar(unsafe=True))
    protectserver = UpvServer(
        session,
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = protectserver
    _LOGGER.debug("Connect to Unfi Protect")

    events_update_interval = entry.options.get(
        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
    )

    protect_data = UnifiProtectData(
        hass, protectserver, timedelta(seconds=events_update_interval)
    )

    try:
        nvr_info = await protectserver.server_information()
    except NotAuthorized:
        _LOGGER.error(
            "Could not Authorize against Unifi Protect. Please reinstall the Integration."
        )
        return False
    except (NvrError, ServerDisconnectedError) as notreadyerror:
        raise ConfigEntryNotReady from notreadyerror

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=nvr_info[SERVER_ID])

    await protect_data.async_setup()
    if not protect_data.last_update_success:
        raise ConfigEntryNotReady

    update_listener = entry.add_update_listener(_async_options_updated)

    data = hass.data[DOMAIN][entry.entry_id] = {
        "protect_data": protect_data,
        "upv": protectserver,
        "snapshot_direct": entry.options.get(CONF_SNAPSHOT_DIRECT, False),
        "server_info": nvr_info,
        "update_listener": update_listener,
        "disable_stream": entry.options[CONF_DISABLE_RTSP],
    }

    async def _async_stop_protect_data(event):
        """Stop updates."""
        await protect_data.async_stop()

    data["stop_event_listener"] = hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STOP, _async_stop_protect_data
    )

    await _async_get_or_create_nvr_device_in_registry(hass, entry, nvr_info)

    for platform in UNIFI_PROTECT_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def _async_get_or_create_nvr_device_in_registry(
    hass: HomeAssistant, entry: ConfigEntry, nvr
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


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
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
        data = hass.data[DOMAIN][entry.entry_id]
        data["update_listener"]()
        data["stop_event_listener"]()
        await data["protect_data"].async_stop()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
