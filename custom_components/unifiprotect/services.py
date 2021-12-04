import asyncio

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.service import async_extract_referenced_entity_ids
from pyunifiprotect.api import ProtectApiClient

from .const import CONF_DURATION, CONF_MESSAGE, DOMAIN
from .models import UnifiProtectEntryData
from .utils import profile_ws_messages


def _async_all_ufp_instances(hass: HomeAssistant) -> list[ProtectApiClient]:
    """All active HomeKit instances."""
    return [
        data.protect
        for data in hass.data[DOMAIN].values()
        if isinstance(data, UnifiProtectEntryData)
    ]


def _async_get_protect_from_call(hass, call) -> list[tuple[str, ProtectApiClient]]:
    referenced = async_extract_referenced_entity_ids(hass, call)
    device_registry = dr.async_get(hass)

    instances: list[tuple[str, ProtectApiClient]] = []
    for device_id in referenced.referenced_devices:
        if not (device_entry := device_registry.async_get(device_id)):
            raise HomeAssistantError(f"No device found for device id: {device_id}")

        name = device_entry.name_by_user or device_entry.name
        macs = [
            # MAC addresses in UFP are always caps
            cval.replace(":", "").upper()
            for ctype, cval in device_entry.connections
            if ctype == dr.CONNECTION_NETWORK_MAC
        ]
        ufp_instances = [
            (name, i)
            for i in _async_all_ufp_instances(hass)
            if i.bootstrap.nvr.mac in macs
        ]
        if not ufp_instances:
            raise HomeAssistantError(
                f"No UniFi Protect NVR found for device ID: {device_id}"
            )
        instances += ufp_instances

    return instances


async def add_doorbell_text(hass: HomeAssistant, call: ServiceCall) -> None:
    message: str = call.data[CONF_MESSAGE]
    instances = _async_get_protect_from_call(hass, call)
    await asyncio.gather(
        *(i.bootstrap.nvr.add_custom_doorbell_message(message) for _, i in instances)
    )


async def remove_doorbell_text(hass: HomeAssistant, call: ServiceCall) -> None:
    message: str = call.data[CONF_MESSAGE]
    instances = _async_get_protect_from_call(hass, call)
    await asyncio.gather(
        *(i.bootstrap.nvr.remove_custom_doorbell_message(message) for _, i in instances)
    )


async def set_default_doorbell_text(hass: HomeAssistant, call: ServiceCall) -> None:
    message: str = call.data[CONF_MESSAGE]
    instances = _async_get_protect_from_call(hass, call)
    await asyncio.gather(
        *(i.bootstrap.nvr.set_default_doorbell_message(message) for _, i in instances)
    )


async def profile_ws(hass: HomeAssistant, call: ServiceCall) -> None:
    duration: int = call.data[CONF_DURATION]
    instances = _async_get_protect_from_call(hass, call)
    await asyncio.gather(
        *(profile_ws_messages(hass, i, duration, name) for name, i in instances)
    )
