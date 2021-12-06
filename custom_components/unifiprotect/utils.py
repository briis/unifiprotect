from __future__ import annotations

import asyncio
from enum import Enum
from io import StringIO
import json
import logging
import time
from typing import Any

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.utils import print_ws_stat_summary

from .const import DOMAIN
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)


@callback
def get_nested_attr(obj: Any, attr: str) -> Any:
    attrs = attr.split(".")

    value = obj
    for key in attrs:
        if not hasattr(value, key):
            return None
        value = getattr(value, key)

    if isinstance(value, Enum):
        value = value.value

    return value


async def profile_ws_messages(
    hass: HomeAssistant,
    protect: ProtectApiClient,
    seconds: int,
    device_entry: DeviceEntry,
) -> None:

    if protect.bootstrap.capture_ws_stats:
        raise HomeAssistantError("Profile already in progress")

    protect.bootstrap.capture_ws_stats = True

    start_time = time.time()
    name = device_entry.name_by_user or device_entry.name or device_entry.id
    nvr_id = name.replace(" ", "_").lower()
    message_id = f"ufp_ws_profiler_{nvr_id}_{start_time}"
    hass.components.persistent_notification.async_create(
        "The WS profile has started. This notification will be updated when it is complete.",
        title=f"{name}: WS Profile Started",
        notification_id=message_id,
    )
    _LOGGER.info("%s: Start WS Profile for %ss", name, seconds)
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        await asyncio.sleep(10)

    protect.bootstrap.capture_ws_stats = False

    json_data = [s.__dict__ for s in protect.bootstrap.ws_stats]
    out_path = hass.config.path(f"ws_profile.{start_time}.json")
    with open(out_path, "w", encoding="utf8") as outfile:
        json.dump(json_data, outfile, indent=4)

    stats_buffer = StringIO()
    print_ws_stat_summary(protect.bootstrap.ws_stats, output=stats_buffer.write)
    protect.bootstrap.clear_ws_stats()
    _LOGGER.info("%s: Complete WS Profile:\n%s", name, stats_buffer.getvalue())

    hass.components.persistent_notification.async_create(
        f"Wrote raw stats to {out_path}\n\n```\n{stats_buffer.getvalue()}\n```",
        title=f"{name}: WS Profile Completed",
        notification_id=message_id,
    )


def above_ha_version(major: int, minor: int) -> bool:
    if MAJOR_VERSION > major:
        return True
    if MAJOR_VERSION < major:
        return False
    return MINOR_VERSION >= minor


@callback
def get_all_ufp_instances(hass: HomeAssistant) -> list[ProtectApiClient]:
    """All active HomeKit instances."""
    return [
        data.protect
        for data in hass.data[DOMAIN].values()
        if isinstance(data, UnifiProtectEntryData)
    ]


@callback
def unifi_mac_from_hass(mac: str) -> str:
    # MAC addresses in UFP are always caps
    return mac.replace(":", "").upper()


@callback
def get_macs_for_device(device_entry: dr.DeviceEntry) -> list[str]:
    return [
        unifi_mac_from_hass(cval)
        for ctype, cval in device_entry.connections
        if ctype == dr.CONNECTION_NETWORK_MAC
    ]


@callback
def get_ufp_instance_from_device_id(
    hass: HomeAssistant, device_id: str
) -> tuple[dr.DeviceEntry, ProtectApiClient]:
    device_registry = dr.async_get(hass)
    if not (device_entry := device_registry.async_get(device_id)):
        raise HomeAssistantError(f"No device found for device id: {device_id}")

    if device_entry.via_device_id is not None:
        return get_ufp_instance_from_device_id(hass, device_entry.via_device_id)

    macs = get_macs_for_device(device_entry)
    ufp_instances = [
        i for i in get_all_ufp_instances(hass) if i.bootstrap.nvr.mac in macs
    ]

    if not ufp_instances:
        raise HomeAssistantError(
            f"No UniFi Protect NVR found for device ID: {device_id}"
        )

    return device_entry, ufp_instances[0]


@callback
def get_ufp_instance_from_entity_id(
    hass: HomeAssistant, entity_id: str
) -> tuple[dr.DeviceEntry, ProtectApiClient]:
    entity_registry = er.async_get(hass)
    if not (entity_entry := entity_registry.async_get(entity_id)):
        raise HomeAssistantError(f"No device found for entity id: {entity_id}")

    assert entity_entry.device_id is not None
    return get_ufp_instance_from_device_id(hass, entity_entry.device_id)
