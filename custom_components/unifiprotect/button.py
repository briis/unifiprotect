"""Support for Ubiquiti's UniFi Protect NVR."""
from __future__ import annotations

import logging
from typing import Callable, Sequence

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from pyunifiprotect import ProtectApiClient
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel, ProtectDeviceModel

from .const import DEVICES_THAT_ADOPT, DOMAIN
from .data import ProtectData
from .entity import ProtectEntity
from .models import ProtectEntryData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Discover devices on a UniFi Protect NVR."""
    entry_data: ProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    async_add_entities(
        [
            ProtectButton(
                protect,
                protect_data,
                device,
            )
            for device in protect_data.get_by_types(DEVICES_THAT_ADOPT)
        ]
    )


class ProtectButton(ProtectEntity, ButtonEntity):
    """A Ubiquiti UniFi Protect Reboot button."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: ProtectData,
        device: ProtectDeviceModel,
    ):
        """Initialize an UniFi camera."""
        assert isinstance(device, ProtectAdoptableDeviceModel)
        self.device: ProtectAdoptableDeviceModel = device
        super().__init__(protect, protect_data, device, None)
        self._attr_name = f"{self.device.name} Reboot Device"
        self._attr_entity_registry_enabled_default = False
        self._attr_device_class = ButtonDeviceClass.RESTART

    @callback
    async def async_press(self) -> None:
        """Press the button."""

        _LOGGER.debug("Rebooting %s with id %s", self.device.model, self.device.id)
        await self.device.reboot()
