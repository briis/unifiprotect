"""Shared Entity definition for Unifi Protect Integration."""
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.entity import Entity

from .const import DEFAULT_BRAND, DOMAIN


class UnifiProtectEntity(Entity):
    """Base class for unifi protect entities."""

    def __init__(self, upv_object, protect_data, server_info, device_id, sensor_type):
        """Initialize the entity."""
        super().__init__()
        self.upv_object = upv_object
        self.protect_data = protect_data
        self._device_id = device_id
        self._sensor_type = sensor_type

        self._device_data = self.protect_data.data[self._device_id]
        self._device_name = self._device_data["name"]
        self._mac = self._device_data["mac"]
        self._firmware_version = self._device_data["firmware_version"]
        self._server_id = server_info["server_id"]
        self._device_type = self._device_data["type"]
        self._model = self._device_data["model"]
        if self._sensor_type is None:
            self._unique_id = f"{self._device_id}_{self._mac}"
        else:
            self._unique_id = f"{self._sensor_type}_{self._mac}"

    @property
    def should_poll(self):
        """Poll Cameras to update attributes."""
        return False

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_info(self):
        """Return Device Info."""
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "name": self._device_name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._model,
            "sw_version": self._firmware_version,
            "via_device": (DOMAIN, self._server_id),
        }

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.protect_data.async_refresh()

    @property
    def available(self):
        """Return if entity is available."""
        return self.protect_data.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.protect_data.async_subscribe_device_id(
                self._device_id, self.async_write_ha_state
            )
        )
