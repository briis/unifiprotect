"""Shared Entity definition for Unifi Protect Integration."""
from __future__ import annotations

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import callback
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import ATTR_DEVICE_MODEL, DEFAULT_ATTRIBUTION, DEFAULT_BRAND, DOMAIN


class UnifiProtectEntity(Entity):
    """Base class for unifi protect entities."""

    def __init__(self, upv_object, protect_data, server_info, device_id, description):
        """Initialize the entity."""
        super().__init__()
        self._attr_should_poll = False

        if description:
            self.entity_description = description

        self.upv_object = upv_object
        self.protect_data = protect_data
        self._device_id = device_id
        self._device_data = self.protect_data.data[self._device_id]
        self._device_name = self._device_data["name"]
        self._attr_name = self._device_name
        self._mac = self._device_data["mac"]
        self._firmware_version = self._device_data["firmware_version"]
        self._server_id = server_info["server_id"]
        self._server_ip = server_info["server_ip"]
        self._device_type = self._device_data["type"]
        self._model = self._device_data["model"]
        if description is None:
            self._attr_unique_id = f"{self._device_id}_{self._mac}"
        else:
            self._attr_unique_id = f"{description.key}_{self._mac}"
        self._attr_device_info = DeviceInfo(
            name=self._device_name,
            manufacturer=DEFAULT_BRAND,
            model=self._model,
            via_device=(DOMAIN, self._server_id),
            sw_version=self._firmware_version,
            connections={(dr.CONNECTION_NETWORK_MAC, self._mac)},
            configuration_url=f"https://{self._server_ip}",
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
            ATTR_DEVICE_MODEL: self._model,
        }

    @callback
    def _async_updated_event(self):
        self._attr_available = self.protect_data.last_update_success
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.protect_data.async_subscribe_device_id(
                self._device_id, self._async_updated_event
            )
        )
