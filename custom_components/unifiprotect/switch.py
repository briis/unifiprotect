""" This component provides Switches for Unifi Protect."""

import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchDevice
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_FRIENDLY_NAME, CONF_MONITORED_CONDITIONS, STATE_OFF, STATE_ON
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

from . import UPV_DATA, DEFAULT_ATTRIBUTION, DEFAULT_BRAND, DOMAIN, TYPE_RECORD_ALLWAYS, TYPE_RECORD_MOTION, TYPE_RECORD_NEVER

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["unifiprotect"]

SCAN_INTERVAL = timedelta(seconds=3)

ATTR_CAMERA_TYPE = "camera_type"
ATTR_BRAND = "brand"

SWITCH_TYPES = {
    "record_motion": ["Record Motion", "camcorder", "record_motion"],
    "record_always": ["Record Always", "camcorder", "record_always"]
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_MONITORED_CONDITIONS, default=list(SWITCH_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SWITCH_TYPES)]
        ),
    }
)

async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Unifi Protect Switch."""
    data = hass.data[UPV_DATA]
    if not data:
        return

    switches = []
    for switch_type in config.get(CONF_MONITORED_CONDITIONS):
        for camera in data.devices:
            switches.append(UnifiProtectSwitch(data, camera, switch_type))

    async_add_entities(switches, True)

class UnifiProtectSwitch(SwitchDevice):
    """A Unifi Protect Switch."""

    def __init__(self, data, camera, switch_type):
        """Initialize an Unifi Protect Switch."""
        self.data = data
        self._camera_id = camera
        self._camera = self.data.devices[camera]
        self._name = "{0} {1} {2}".format(DOMAIN.capitalize(), SWITCH_TYPES[switch_type][0], self._camera["name"])
        self._unique_id = self._name.lower().replace(" ", "_")
        self._icon = "mdi:{}".format(SWITCH_TYPES.get(switch_type)[1])
        self._state = STATE_OFF
        self._camera_type = self._camera["type"]
        self._attr = SWITCH_TYPES.get(switch_type)[2]
        self._switch_type = SWITCH_TYPES.get(switch_type)[2]
        _LOGGER.debug("UnifiProtectSwitch: %s created", self._name)

    @property
    def should_poll(self):
        """Poll for status regularly."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def state(self):
        """Return the state of the device if any."""
        return self._state

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == STATE_ON

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = DEFAULT_ATTRIBUTION
        attrs[ATTR_BRAND] = DEFAULT_BRAND
        attrs[ATTR_CAMERA_TYPE] = self._camera_type

        return attrs

    def turn_on(self, **kwargs):
        """Turn the device on."""
        if self._switch_type == "record_motion":
            _LOGGER.debug("Turning on Motion Detection")
            self.data.set_camera_recording(self._camera_id, TYPE_RECORD_MOTION)
        else:
            _LOGGER.debug("Turning on Constant Recording")
            self.data.set_camera_recording(self._camera_id, TYPE_RECORD_ALLWAYS)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        _LOGGER.debug("Turning off Recording")
        self.data.set_camera_recording(self._camera_id, TYPE_RECORD_NEVER)

    def update(self):
        """Update Motion Detection state."""
        if self._switch_type == "record_motion":
            enabled = True if self._camera["recording_mode"] == TYPE_RECORD_MOTION else False
        else:
            enabled = True if self._camera["recording_mode"] == TYPE_RECORD_ALLWAYS else False
        _LOGGER.debug("enabled: %s", enabled)
        self._state = STATE_ON if enabled else STATE_OFF

