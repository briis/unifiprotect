from __future__ import annotations

import asyncio
from enum import Enum
from io import StringIO
import json
import logging
import time
from typing import Any

from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceEntry
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.utils import print_ws_stat_summary

_LOGGER = logging.getLogger(__name__)


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
    """Checks if current Home Assistant version if above a specificed one

    CORE: Remove this before merging to core.
    """
    if MAJOR_VERSION > major:
        return True
    if MAJOR_VERSION < major:
        return False
    return MINOR_VERSION >= minor
