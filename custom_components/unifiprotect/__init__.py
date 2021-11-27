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
    CONF_VERIFY_SSL,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
import homeassistant.helpers.device_registry as dr
from pyunifiprotect import NotAuthorized, NvrError, ProtectApiClient
from pyunifiprotect.data.nvr import NVR

from custom_components.unifiprotect.utils import profile_ws_messages, above_ha_version

from .const import (
    CONF_DISABLE_RTSP,
    CONF_DOORBELL_TEXT,
    CONF_DURATION,
    CONF_MESSAGE,
    CONFIG_OPTIONS,
    DEFAULT_BRAND,
    DEFAULT_SCAN_INTERVAL,
    DEVICES_FOR_SUBSCRIBE,
    DOMAIN,
    DOORBELL_TEXT_SCHEMA,
    MIN_REQUIRED_PROTECT_V,
    PLATFORMS,
    PLATFORMS_NEXT,
    PROFILE_WS_SCHEMA,
    SERVICE_ADD_DOORBELL_TEXT,
    SERVICE_PROFILE_WS,
    SERVICE_REMOVE_DOORBELL_TEXT,
    SERVICE_SET_DEFAULT_DOORBELL_TEXT,
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
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        verify_ssl=entry.data[CONF_VERIFY_SSL],
        session=session,
        subscribed_models=DEVICES_FOR_SUBSCRIBE,
        ignore_stats=True,
    )
    _LOGGER.debug("Connect to UniFi Protect")
    protect_data = UnifiProtectData(hass, protect, SCAN_INTERVAL, entry)

    try:
        nvr_info = await protect.get_nvr()
    except NotAuthorized as err:
        raise ConfigEntryAuthFailed(err) from err
    except (asyncio.TimeoutError, NvrError, ServerDisconnectedError) as notreadyerror:
        raise ConfigEntryNotReady from notreadyerror

    if nvr_info.version < MIN_REQUIRED_PROTECT_V:
        _LOGGER.error(
            (
                "You are running v%s of UniFi Protect. Minimum required version is v%s. "
                "Please upgrade UniFi Protect and then retry"
            ),
            nvr_info.version,
            MIN_REQUIRED_PROTECT_V,
        )
        return False

    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=nvr_info.mac)

    await protect_data.async_setup()
    if not protect_data.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = UnifiProtectEntryData(
        protect_data=protect_data,
        protect=protect,
        disable_stream=entry.options.get(CONF_DISABLE_RTSP, False),
    )

    await _async_get_or_create_nvr_device_in_registry(hass, entry, nvr_info)

    if above_ha_version(2021, 12):
        hass.config_entries.async_setup_platforms(entry, PLATFORMS_NEXT)
    else:
        hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    async def add_doorbell_text(call: ServiceCall):
        message: str = call.data[CONF_MESSAGE]
        await protect.bootstrap.nvr.add_custom_doorbell_message(message)

    async def remove_doorbell_text(call: ServiceCall):
        message: str = call.data[CONF_MESSAGE]
        await protect.bootstrap.nvr.remove_custom_doorbell_message(message)

    async def set_default_doorbell_text(call: ServiceCall):
        message: str = call.data[CONF_MESSAGE]
        await protect.bootstrap.nvr.set_default_doorbell_message(message)

    async def profile_ws(call: ServiceCall):
        duration: int = call.data[CONF_DURATION]
        await profile_ws_messages(hass, protect, duration)

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_DOORBELL_TEXT, add_doorbell_text, DOORBELL_TEXT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_DOORBELL_TEXT,
        remove_doorbell_text,
        DOORBELL_TEXT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DEFAULT_DOORBELL_TEXT,
        set_default_doorbell_text,
        DOORBELL_TEXT_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PROFILE_WS,
        profile_ws,
        PROFILE_WS_SCHEMA,
    )

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, protect_data.async_stop)
    )

    return True


async def _async_get_or_create_nvr_device_in_registry(
    hass: HomeAssistant, entry: ConfigEntry, nvr: NVR
) -> None:
    device_registry = await dr.async_get_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        connections={(dr.CONNECTION_NETWORK_MAC, nvr.mac)},
        identifiers={(DOMAIN, nvr.mac)},
        manufacturer=DEFAULT_BRAND,
        name=entry.data[CONF_ID],
        model=nvr.type,
        sw_version=str(nvr.version),
        configuration_url=nvr.api.base_url,
    )


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Unifi Protect config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
        await data.protect_data.async_stop()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        # keep verify SSL false for anyone migrating to maintain backwards compatibility
        new[CONF_VERIFY_SSL] = False
        del new[CONF_DOORBELL_TEXT]

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True
