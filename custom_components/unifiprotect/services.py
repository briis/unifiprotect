from __future__ import annotations

import asyncio

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.service import async_extract_referenced_entity_ids
from pydantic import ValidationError
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.exceptions import BadRequest

from .const import CONF_DURATION, CONF_MESSAGE
from .utils import get_ufp_instance_from_device_id, profile_ws_messages


@callback
def _async_get_protect_from_call(
    hass: HomeAssistant, call: ServiceCall
) -> list[tuple[dr.DeviceEntry, ProtectApiClient]]:
    referenced = async_extract_referenced_entity_ids(hass, call)

    instances: list[tuple[dr.DeviceEntry, ProtectApiClient]] = []
    for device_id in referenced.referenced_devices:
        instances.append(get_ufp_instance_from_device_id(hass, device_id))

    return instances


@callback
async def _async_call_nvr(
    instances: list[tuple[dr.DeviceEntry, ProtectApiClient]],
    method: str,
    *args,
    **kwargs,
):
    try:
        await asyncio.gather(
            *(getattr(i.bootstrap.nvr, method)(*args, **kwargs) for _, i in instances)
        )
    except (BadRequest, ValidationError) as err:
        raise HomeAssistantError(str(err)) from err


async def add_doorbell_text(hass: HomeAssistant, call: ServiceCall) -> None:
    message: str = call.data[CONF_MESSAGE]
    instances = _async_get_protect_from_call(hass, call)
    await _async_call_nvr(instances, "add_custom_doorbell_message", message)


async def remove_doorbell_text(hass: HomeAssistant, call: ServiceCall) -> None:
    message: str = call.data[CONF_MESSAGE]
    instances = _async_get_protect_from_call(hass, call)
    await _async_call_nvr(instances, "remove_custom_doorbell_message", message)


async def set_default_doorbell_text(hass: HomeAssistant, call: ServiceCall) -> None:
    message: str = call.data[CONF_MESSAGE]
    instances = _async_get_protect_from_call(hass, call)
    await _async_call_nvr(instances, "set_default_doorbell_message", message)


async def profile_ws(hass: HomeAssistant, call: ServiceCall) -> None:
    duration: int = call.data[CONF_DURATION]
    instances = _async_get_protect_from_call(hass, call)
    await asyncio.gather(
        *(
            profile_ws_messages(hass, i, duration, device_entry)
            for device_entry, i in instances
        )
    )
