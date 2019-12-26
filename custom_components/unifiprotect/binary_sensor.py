""" This component provides binary sensors for Unifi Protect."""
import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.components.binary_sensor import (BinarySensorDevice)
from homeassistant.const import (ATTR_ATTRIBUTION,
                                 CONF_MONITORED_CONDITIONS)
from homeassistant.core import callback
from homeassistant.helpers.config_validation import (PLATFORM_SCHEMA)
from . import ATTRIBUTION, DATA_UFP, DEFAULT_BRAND

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['unifiprotect']

SCAN_INTERVAL = timedelta(seconds=5)

# sensor_type [ description, unit, icon ]
SENSOR_TYPES = {
    'motion': ['Motion', 'motion', 'motionDetected']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Unifi Protect binary sensor."""
    cameradata = hass.data.get(DATA_UFP)
    if not cameradata:
        return

    sensors = []
    for sensor_type in config.get(CONF_MONITORED_CONDITIONS):
        for camera in cameradata.cameras:
            sensors.append(UfpBinarySensor(camera, sensor_type, cameradata))

    async_add_entities(sensors, True)

class UfpBinarySensor(BinarySensorDevice):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, device, sensor_type, nvrdata):
        """Initialize an Arlo sensor."""
        self._name = '{0} {1}'.format(SENSOR_TYPES[sensor_type][0], device['name'])
        self._unique_id = self._name.lower().replace(' ', '_')
        self._device = device
        self._sensor_type = sensor_type
        self._nvrdata = nvrdata
        self._state = False
        self._class = SENSOR_TYPES.get(self._sensor_type)[1]
        self._attr = SENSOR_TYPES.get(self._sensor_type)[2]
        self.remove_timer = None
        _LOGGER.info('UfpBinarySensor: %s created', self._name)

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = ATTRIBUTION
        attrs['brand'] = DEFAULT_BRAND
        attrs['friendly_name'] = self._name

        return attrs

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state is True

    def update(self):
        """ Updates Motions State."""

        event_list_sorted = sorted(self._nvrdata.events, key=lambda k: k['start'], reverse=True)        
        is_motion = None

        for event in event_list_sorted:
            if (self._device['id'] == event['camera']):
                if (event['end'] is None):
                    is_motion = True
                else:
                    is_motion = False

                break
        self._state = is_motion




