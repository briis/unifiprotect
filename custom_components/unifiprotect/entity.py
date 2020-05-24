from homeassistant.helpers.entity import Entity

from .const import DOMAIN, DEFAULT_BRAND


class UnifiProtectEntity(Entity):
    """Base class for unifi protect entities."""

    def __init__(self, upv_object, coordinator, camera_id):
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
        self._unique_id = f"{DOMAIN}_{self._camera_id}_{self._mac}"

    @property
    def should_poll(self):
        """Poll Cameras to update attributes."""
        return False

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id
