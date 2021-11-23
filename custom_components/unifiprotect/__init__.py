"""Unifi Protect Platform."""
from __future__ import annotations

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
    CONF_USERNAME,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.device_registry as dr
from pyunifiprotect import NotAuthorized, NvrError, ProtectApiClient

from .const import (
    CONF_DISABLE_RTSP,
    CONF_DOORBELL_TEXT,
    CONFIG_OPTIONS,
    DEFAULT_BRAND,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_REQUIRED_PROTECT_V,
    UNIFI_PROTECT_PLATFORMS,
)
from .data import UnifiProtectData
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)


@callback
def _async_import_options_from_data_if_missing(hass: HomeAssistant, entry: ConfigEntry):
    options = dict(entry.options)
    data = dict(entry.data)
    modified = False
    for importable_option in CONFIG_OPTIONS:
        if importable_option not in entry.options and importable_option in entry.data:
            options[importable_option] = entry.data[importable_option]
            del data[importable_option]
            modified = True

    if modified:
        hass.config_entries.async_update_entry(entry, data=data, options=options)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the Unifi Protect config entries."""
    _async_import_options_from_data_if_missing(hass, entry)

    session = async_create_clientsession(hass, cookie_jar=CookieJar(unsafe=True))
    protect = ProtectApiClient(
        entry.data[CONF_HOST],
        entry.data[CONF_PORT],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        verify_ssl=True,
        session=session,
    )
    await protect.update()
    _LOGGER.debug("Connect to Unfi Protect")

    events_update_interval = DEFAULT_SCAN_INTERVAL

    protect_data = UnifiProtectData(
        hass, protect, timedelta(seconds=events_update_interval)
    )

    try:
        if protect.bootstrap.nvr.version < MIN_REQUIRED_PROTECT_V:
            _LOGGER.error(
                "You are running V%s of UniFi Protect. Minimum required version is V%s. Please upgrade UniFi Protect and then retry",
                protect.bootstrap.nvr.version,
                MIN_REQUIRED_PROTECT_V,
            )
            return False

    except NotAuthorized:
        _LOGGER.error(
            "Could not Authorize against Unifi Protect. Please reinstall the Integration"
        )
        return False
    except (asyncio.TimeoutError, NvrError, ServerDisconnectedError) as notreadyerror:
        raise ConfigEntryNotReady from notreadyerror

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(
            entry, unique_id=protect.bootstrap.nvr.id
        )

    await protect_data.async_setup()
    if not protect_data.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = UnifiProtectEntryData(
        protect_data=protect_data,
        upv=protect,
        disable_stream=entry.options.get(CONF_DISABLE_RTSP, False),
        doorbell_text=entry.options.get(CONF_DOORBELL_TEXT, None),
    )

    await _async_get_or_create_nvr_device_in_registry(hass, entry, protect)

    hass.config_entries.async_setup_platforms(entry, UNIFI_PROTECT_PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, protect_data.async_stop)
    )

    return True


async def _async_get_or_create_nvr_device_in_registry(
    hass: HomeAssistant, entry: ConfigEntry, protect
) -> None:
    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, protect.bootstrap.nvr.id)},
        identifiers={(DOMAIN, protect.bootstrap.nvr.id)},
        manufacturer=DEFAULT_BRAND,
        name=entry.data[CONF_ID],
        model=protect.bootstrap.nvr.type,
        sw_version=protect.bootstrap.nvr.version,
    )


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Unifi Protect config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, UNIFI_PROTECT_PLATFORMS
    )

    if unload_ok:
        data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
        await data.protect_data.async_stop()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
