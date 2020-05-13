""" This component provides sensors for Unifi Protect."""
import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    CONF_MONITORED_CONDITIONS,
)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from . import UPV_DATA, DEFAULT_ATTRIBUTION, DEFAULT_BRAND, TYPE_RECORD_NEVER

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["unifiprotect"]

ATTR_CAMERA_TYPE = "camera_type"
ATTR_BRAND = "brand"

SENSOR_TYPES = {
    "motion_recording": ["Motion Recording", None, "camcorder", "motion_recording"]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Unifi Protect sensor."""
    coordinator = hass.data[UPV_DATA]["coordinator"]
    if not coordinator.data:
        return

    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        for camera in coordinator.data:
            sensors.append(UnifiProtectSensor(coordinator, camera, sensor_type))

    async_add_entities(sensors, True)


class UnifiProtectSensor(Entity):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, coordinator, camera, sensor_type):
        """Initialize an Unifi Protect sensor."""
        self.coordinator = coordinator
        self._camera_id = camera
        self._camera = self.coordinator.data[camera]
        self._name = "{0} {1}".format(
            SENSOR_TYPES[sensor_type][0], self._camera["name"]
        )
        self._unique_id = self._name.lower().replace(" ", "_")
        self._sensor_type = sensor_type
        self._icon = "mdi:{}".format(SENSOR_TYPES.get(self._sensor_type)[2])
        self._camera_type = self._camera["model"]
        self._attr = SENSOR_TYPES.get(self._sensor_type)[3]
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
        return SENSOR_TYPES.get(self._sensor_type)[1]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = DEFAULT_ATTRIBUTION
        attrs[ATTR_BRAND] = DEFAULT_BRAND
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

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
