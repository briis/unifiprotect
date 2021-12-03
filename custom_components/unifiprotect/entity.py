"""Shared Entity definition for Unifi Protect Integration."""
from __future__ import annotations

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity
from pyunifiprotect import ProtectApiClient
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel

from .const import ATTR_DEVICE_MODEL, DEFAULT_ATTRIBUTION, DEFAULT_BRAND, DOMAIN
from .data import UnifiProtectData


class UnifiProtectEntity(Entity):
    """Base class for unifi protect entities."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: UnifiProtectData,
        device: ProtectAdoptableDeviceModel,
        description,
    ):
        """Initialize the entity."""
        super().__init__()
        self._attr_should_poll = False

        if description:
            self.entity_description = description

        if not hasattr(self, "device"):
            self.device: ProtectAdoptableDeviceModel = device
        self.protect: ProtectApiClient = protect
        self.protect_data: UnifiProtectData = protect_data
        if description is None:
            self._attr_unique_id = f"{self.device.id}"
        else:
            self._attr_unique_id = f"{self.device.id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            name=self.device.name,
            manufacturer=DEFAULT_BRAND,
            model=self.device.type,
            via_device=(DOMAIN, self.protect.bootstrap.nvr.mac),
            sw_version=self.device.firmware_version,
            connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac)},
            configuration_url=self.device.protect_url,
        )

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.protect_data.async_refresh()

    @property
    def extra_state_attributes(self):
        """Return common attributes"""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self.device.type,
        }

    @callback
    def _async_update_device_from_protect(self):
        if self.protect_data.last_update_success:
            devices = getattr(self.protect.bootstrap, f"{self.device.model.value}s")
            self.device = devices[self.device.id]

        self._attr_available = (
            self.protect_data.last_update_success and self.device.is_connected
        )

    @callback
    def _async_updated_event(self):
        self._async_update_device_from_protect()
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.protect_data.async_subscribe_device_id(
                self.device.id, self._async_updated_event
            )
        )
