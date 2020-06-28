"""Unifi Protect Platform."""

import asyncio
from datetime import timedelta
import logging

from aiohttp import CookieJar
from aiohttp.client_exceptions import ServerDisconnectedError

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
    CONF_SNAPSHOT_DIRECT,
    DEFAULT_BRAND,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    UNIFI_PROTECT_PLATFORMS,
)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistantType, config: ConfigType) -> bool:
    """Set up the Unifi Protect components."""

    return True


async def async_setup_entry(hass: HomeAssistantType, entry: ConfigEntry) -> bool:
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

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=protectserver.update,
        update_interval=timedelta(seconds=events_update_interval),
    )

    try:
        nvr_info = await protectserver.server_information()
    except NotAuthorized:
        _LOGGER.error(
            "Could not Authorize against Unifi Protect. Please reinstall the Integration."
        )
        return
    except (NvrError, ServerDisconnectedError):
        raise ConfigEntryNotReady

    await coordinator.async_refresh()
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "upv": protectserver,
        "snapshot_direct": entry.options.get(CONF_SNAPSHOT_DIRECT, False),
    }

    await _async_get_or_create_nvr_device_in_registry(hass, entry, nvr_info)

    for platform in UNIFI_PROTECT_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    if not entry.update_listeners:
        entry.add_update_listener(async_update_options)

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


async def async_update_options(hass: HomeAssistantType, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


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
