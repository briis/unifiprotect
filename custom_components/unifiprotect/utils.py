from __future__ import annotations

import asyncio
from datetime import datetime
from enum import Enum
from io import StringIO
import json
import logging
import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.exceptions import HomeAssistantError
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.utils import print_ws_stat_summary


_LOGGER = logging.getLogger(__name__)


def get_nested_attr(obj: Any, attr: str) -> Any:
    attrs = attr.split(".")

    value = obj
    for attr in attrs:
        if not hasattr(value, attr):
            return None
        value = getattr(value, attr)

    if isinstance(value, Enum):
        value = value.value

    return value


def get_datetime_attr(dt: datetime | None) -> str | None:
    return None if dt is None else dt


async def profile_ws_messages(
    hass: HomeAssistant, protect: ProtectApiClient, seconds: int, name: str
) -> None:

    if protect.bootstrap.capture_ws_stats:
        raise HomeAssistantError("Profile already in progress")

    protect.bootstrap.capture_ws_stats = True

    start_time = time.time()
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
    out_file = hass.config.path(f"ws_profile.{start_time}.json")
    with open(out_file, "w", encoding="utf8") as f:
        json.dump(json_data, f, indent=4)

    stats_buffer = StringIO()
    print_ws_stat_summary(protect.bootstrap.ws_stats, output=stats_buffer.write)
    protect.bootstrap.clear_ws_stats()
    _LOGGER.info("%s: Complete WS Profile:\n%s", name, stats_buffer.getvalue())

    hass.components.persistent_notification.async_create(
        f"Wrote raw stats to {out_file}\n\n```\n{stats_buffer.getvalue()}\n```",
        title=f"{name}: WS Profile Completed",
        notification_id=message_id,
    )


def above_ha_version(major, minor) -> bool:
    if MAJOR_VERSION > major:
        return True
    elif MAJOR_VERSION < major:
        return False
    return MINOR_VERSION >= minor
