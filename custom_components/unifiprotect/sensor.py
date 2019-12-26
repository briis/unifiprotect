""" This component provides sensors for Unifi Protect."""
import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 CONF_MONITORED_CONDITIONS
                                 )
from homeassistant.core import callback
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from homeassistant.helpers.entity import (Entity)
from . import ATTRIBUTION, DATA_UFP, DEFAULT_BRAND

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['unifiprotect']

SCAN_INTERVAL = timedelta(seconds=5)

SENSOR_TYPES = {
    'motion_recording': ['Motion Recording', None, 'motion-sensor', 'motion_recording']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Unifi Protect sensor."""
    cameradata = hass.data.get(DATA_UFP)
    if not cameradata:
        return

    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        for camera in cameradata.cameras:
            name = '{0} {1}'.format(SENSOR_TYPES[sensor_type][0], camera['name'])
            sensors.append(UnifiProtectSensor(name, camera, sensor_type, cameradata))

    async_add_entities(sensors, True)

class UnifiProtectSensor(Entity):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, name, device, sensor_type, nvrdata):
        """Initialize an Arlo sensor."""
        self._name = name
        self._unique_id = self._name.lower().replace(' ', '_')
        self._device = device
        self._sensor_type = sensor_type
        self._nvrdata = nvrdata
        self._icon = 'mdi:{}'.format(SENSOR_TYPES.get(self._sensor_type)[2])
        self._state = device['recording_mode']
        self._attr = SENSOR_TYPES.get(self._sensor_type)[3]
        _LOGGER.info('UnifiProtectSensor: %s created', self._name)

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

        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        attrs['brand'] = DEFAULT_BRAND
        attrs['friendly_name'] = self._name

        return attrs

    def update(self):
        """ Updates Motions State."""

        recstate = None
        caminfo = self._nvrdata.cameras
        for camera in caminfo:
            if (self._device['id'] == camera['id']):
                recstate = camera['recording_mode']
                break

        self._state = recstate



