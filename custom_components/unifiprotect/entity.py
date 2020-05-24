from homeassistant.helpers.entity import Entity
import homeassistant.helpers.device_registry as dr

from .const import DOMAIN, DEFAULT_BRAND


class UnifiProtectEntity(Entity):
    """Base class for unifi protect entities."""

    def __init__(self, upv_object, coordinator, camera_id, sensor_type):
        """Initialize the entity."""
        super().__init__()
        self.upv_object = upv_object
        self.coordinator = coordinator
        self._camera_id = camera_id

        self._camera_data = self.coordinator.data[self._camera_id]
        self._name = self._camera_data["name"]
        self._mac = self._camera_data["mac"]
        self._firmware_version = self._camera_data["firmware_version"]
        self._server_id = self._camera_data["server_id"]
        self._device_type = self._camera_data["type"]
        self._model = self._camera_data["model"]
        self._unique_id = (
            f"{DOMAIN}_{self._camera_id}_{self._mac}"
            if sensor_type is None
            else f"{DOMAIN}_{sensor_type}_{self._mac}"
        )

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
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "name": self.name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._device_type,
            "sw_version": self._firmware_version,
            "via_device": (DOMAIN, self._server_id),
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
