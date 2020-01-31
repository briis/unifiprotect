""" This component provides sensors for Unifi Protect."""
import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_FRIENDLY_NAME, CONF_MONITORED_CONDITIONS
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
from . import UPV_DATA, DEFAULT_ATTRIBUTION, DEFAULT_BRAND, TYPE_RECORD_NEVER

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["unifiprotect"]

# Update Frequently as we are only reading from Memory
SCAN_INTERVAL = timedelta(seconds=2)

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
    data = hass.data[UPV_DATA]
    if not data:
        return

    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        for camera in data.devices:
            sensors.append(UnifiProtectSensor(data, camera, sensor_type))

    async_add_entities(sensors, True)


class UnifiProtectSensor(Entity):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, data, camera, sensor_type):
        """Initialize an Unifi Protect sensor."""
        self.data = data
        self._camera_id = camera
        self._camera = self.data.devices[camera]
        self._name = "{0} {1}".format(SENSOR_TYPES[sensor_type][0], self._camera["name"])
        self._unique_id = self._name.lower().replace(" ", "_")
        self._sensor_type = sensor_type
        self._icon = "mdi:{}".format(SENSOR_TYPES.get(self._sensor_type)[2])
        self._state = None
        self._camera_type = self._camera["type"]
        self._attr = SENSOR_TYPES.get(self._sensor_type)[3]
        _LOGGER.debug("UnifiProtectSensor: %s created", self._name)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

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

    def update(self):
        """ Updates Motions State."""

        self._state = self._camera["recording_mode"]
        self._icon = "mdi:camcorder" if self._state != TYPE_RECORD_NEVER else "mdi:camcorder-off"
