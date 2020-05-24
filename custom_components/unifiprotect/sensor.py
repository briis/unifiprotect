""" This component provides sensors for Unifi Protect."""
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    CONF_ID,
)
import homeassistant.helpers.device_registry as dr
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from .const import (
    ATTR_EVENT_SCORE,
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    TYPE_RECORD_NEVER,
    ENTITY_ID_SENSOR_FORMAT,
    ENTITY_UNIQUE_ID,
    DEFAULT_BRAND,
)

_LOGGER = logging.getLogger(__name__)

ATTR_CAMERA_TYPE = "camera_type"

SENSOR_TYPES = {
    "motion_recording": ["Motion Recording", None, "camcorder", "motion_recording"]
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A Ubiquiti Unifi Protect Sensor."""
    coordinator = hass.data[DOMAIN][entry.data[CONF_ID]]["coordinator"]
    if not coordinator.data:
        return

    sensors = []
    for sensor in SENSOR_TYPES:
        for camera in coordinator.data:
            sensors.append(
                UnifiProtectSensor(coordinator, camera, sensor, entry.data[CONF_ID])
            )

    async_add_entities(sensors, True)

    return True


class UnifiProtectSensor(Entity):
    """A Ubiquiti Unifi Protect Sensor."""

    def __init__(self, coordinator, camera, sensor, instance):
        """Initialize an Unifi Protect sensor."""
        self.coordinator = coordinator
        self._camera_id = camera
        self._camera = self.coordinator.data[camera]
        self._name = f"{SENSOR_TYPES[sensor][0]} {self._camera['name']}"
        self._mac = self._camera["mac"]
        self._firmware_version = self._camera["firmware_version"]
        self._server_id = self._camera["server_id"]
        self._units = SENSOR_TYPES[sensor][1]
        self._icon = f"mdi:{SENSOR_TYPES[sensor][2]}"
        self._camera_type = self._camera["model"]

        self.entity_id = ENTITY_ID_SENSOR_FORMAT.format(
            slugify(instance), slugify(self._name).replace(" ", "_")
        )
        self._unique_id = ENTITY_UNIQUE_ID.format(sensor, self._mac)

        _LOGGER.debug(f"UNIFIPROTECT SENSOR CREATED: {self._name}")

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self._camera_id]["recording_mode"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return (
            "mdi:camcorder" if self.state != TYPE_RECORD_NEVER else "mdi:camcorder-off"
        )

    @property
    def unit_of_measurement(self):
        """Return the units of measurement."""
        return self._units

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = DEFAULT_ATTRIBUTION
        attrs[ATTR_CAMERA_TYPE] = self._camera_type
        attrs[ATTR_FRIENDLY_NAME] = self._name

        return attrs

    @property
    def should_poll(self):
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def device_info(self):
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "name": self._name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._camera_type,
            "sw_version": self._firmware_version,
            "via_device": (DOMAIN, self._server_id),
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    # async def async_will_remove_from_hass(self):
    #     """When entity will be removed from hass."""
    #     self.coordinator.async_remove_listener(self.async_write_ha_state)
