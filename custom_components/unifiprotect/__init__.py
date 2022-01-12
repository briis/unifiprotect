"""UniFi Protect Platform."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from aiohttp import CookieJar
from aiohttp.client_exceptions import ServerDisconnectedError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from pyunifiprotect import NotAuthorized, NvrError, ProtectApiClient
from pyunifiprotect.data import ModelType

from .const import (
    CONF_ALL_UPDATES,
    CONF_DOORBELL_TEXT,
    CONF_OVERRIDE_CHOST,
    CONFIG_OPTIONS,
    DEFAULT_SCAN_INTERVAL,
    DEVICES_FOR_SUBSCRIBE,
    DEVICES_THAT_ADOPT,
    DOMAIN,
    MIN_REQUIRED_PROTECT_V,
    OUTDATED_LOG_MESSAGE,
    PLATFORMS,
)
from .data import ProtectData
from .services import async_cleanup_services, async_setup_services

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)


@callback
async def _async_migrate_data(
    hass: HomeAssistant, entry: ConfigEntry, protect: ProtectApiClient
) -> None:
    # already up to date, skip
    if CONF_ALL_UPDATES in entry.options:
        return

    _LOGGER.info("Starting entity migration...")

    # migrate entry
    options = dict(entry.options)
    data = dict(entry.data)
    options[CONF_ALL_UPDATES] = False
    if CONF_DOORBELL_TEXT in options:
        del options[CONF_DOORBELL_TEXT]
    hass.config_entries.async_update_entry(entry, data=data, options=options)

    # migrate entities
    registry = er.async_get(hass)
    mac_to_id: dict[str, str] = {}
    mac_to_channel_id: dict[str, str] = {}
    bootstrap = await protect.get_bootstrap()
    for model in DEVICES_THAT_ADOPT:
        attr = model.value + "s"
        for device in getattr(bootstrap, attr).values():
            mac_to_id[device.mac] = device.id
            if model != ModelType.CAMERA:
                continue

            for channel in device.channels:
                channel_id = str(channel.id)
                if channel.is_rtsp_enabled:
                    break
            mac_to_channel_id[device.mac] = channel_id

    count = 0
    entities = er.async_entries_for_config_entry(registry, entry.entry_id)
    for entity in entities:
        new_unique_id: str | None = None
        if entity.domain != Platform.CAMERA.value:
            parts = entity.unique_id.split("_")
            if len(parts) >= 2:
                device_or_key = "_".join(parts[:-1])
                mac = parts[-1]

                device_id = mac_to_id[mac]
                if device_or_key == device_id:
                    new_unique_id = device_id
                else:
                    new_unique_id = f"{device_id}_{device_or_key}"
        else:
            parts = entity.unique_id.split("_")
            if len(parts) == 2:
                mac = parts[1]
                device_id = mac_to_id[mac]
                channel_id = mac_to_channel_id[mac]
                new_unique_id = f"{device_id}_{channel_id}"
            else:
                device_id = parts[0]
                channel_id = parts[2]
                extra = "" if len(parts) == 3 else "_insecure"
                new_unique_id = f"{device_id}_{channel_id}{extra}"

        if new_unique_id is None:
            continue

        _LOGGER.debug(
            "Migrating entity %s (old unique_id: %s, new unique_id: %s)",
            entity.entity_id,
            entity.unique_id,
            new_unique_id,
        )
        try:
            registry.async_update_entity(entity.entity_id, new_unique_id=new_unique_id)
        except ValueError:
            _LOGGER.warning(
                "Could not migrate entity %s (old unique_id: %s, new unique_id: %s)",
                entity.entity_id,
                entity.unique_id,
                new_unique_id,
            )
        else:
            count += 1

    _LOGGER.info("Migrated %s entities", count)
    if count != len(entities):
        _LOGGER.warning("%s entities not migrated", len(entities) - count)


@callback
def _async_import_options_from_data_if_missing(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
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
    """Set up the UniFi Protect config entries."""
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
        override_connection_host=entry.options.get(CONF_OVERRIDE_CHOST, False),
        ignore_stats=not entry.options.get(CONF_ALL_UPDATES, False),
    )
    _LOGGER.debug("Connect to UniFi Protect")
    data_service = ProtectData(hass, protect, SCAN_INTERVAL, entry)

    try:
        nvr_info = await protect.get_nvr()
    except NotAuthorized as err:
        raise ConfigEntryAuthFailed(err) from err
    except (asyncio.TimeoutError, NvrError, ServerDisconnectedError) as err:
        raise ConfigEntryNotReady from err

    if nvr_info.version < MIN_REQUIRED_PROTECT_V:
        _LOGGER.error(
            OUTDATED_LOG_MESSAGE,
            nvr_info.version,
            MIN_REQUIRED_PROTECT_V,
        )
        return False

    await _async_migrate_data(hass, entry, protect)
    if entry.unique_id is None:
        hass.config_entries.async_update_entry(entry, unique_id=nvr_info.mac)

    await data_service.async_setup()
    if not data_service.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = data_service
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    async_setup_services(hass)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, data_service.async_stop)
    )

    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload UniFi Protect config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data: ProtectData = hass.data[DOMAIN][entry.entry_id]
        await data.async_stop()
        hass.data[DOMAIN].pop(entry.entry_id)
        async_cleanup_services(hass)

    return bool(unload_ok)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        # keep verify SSL false for anyone migrating to maintain backwards compatibility
        new[CONF_VERIFY_SSL] = False
        if CONF_DOORBELL_TEXT in new:
            del new[CONF_DOORBELL_TEXT]

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True
