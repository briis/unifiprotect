""" This component provides binary sensors for Unifi Protect."""
import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv

try:
    from homeassistant.components.binary_sensor import (
        BinarySensorEntity as BinarySensorDevice,
    )
except ImportError:
    # Prior to HA v0.110
    from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.binary_sensor import DEVICE_CLASS_MOTION
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    ATTR_LAST_TRIP_TIME,
)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from . import (
    UPV_DATA,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEVICE_CLASS_DOORBELL,
)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ["unifiprotect"]

ATTR_BRAND = "brand"
ATTR_EVENT_SCORE = "event_score"


async def async_setup_platform(hass, config, async_add_entities, _discovery_info=None):
    """Set up an Unifi Protect binary sensor."""
    coordinator = hass.data[UPV_DATA]["coordinator"]
    if not coordinator.data:
        return

    sensors = []
    for camera in coordinator.data:
        if coordinator.data[camera]["type"] == "doorbell":
            sensors.append(UfpBinarySensor(coordinator, camera, DEVICE_CLASS_DOORBELL))
        sensors.append(UfpBinarySensor(coordinator, camera, DEVICE_CLASS_MOTION))

    async_add_entities(sensors, True)


class UfpBinarySensor(BinarySensorDevice):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, coordinator, camera, sensor_type):
        self.coordinator = coordinator
        self._camera_id = camera
        self._camera = coordinator.data[camera]
        self._name = f"{sensor_type.capitalize()} {self._camera['name']}"
        self._unique_id = self._name.lower().replace(" ", "_")
        self._device_class = sensor_type
        self._event_score = self._camera["event_score"]

        if self._device_class == DEVICE_CLASS_DOORBELL:
            _LOGGER.debug(f"UNIFIPROTECT DOORBELL SENSOR CREATED: {self._name}")
        else:
            _LOGGER.debug(f"UNIFIPROTECT MOTION SENSOR CREATED: {self._name}")

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            return self.coordinator.data[self._camera_id]["event_ring_on"]
        else:
            return self.coordinator.data[self._camera_id]["event_on"]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def icon(self):
        """Select icon to display in Frontend."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            if self.coordinator.data[self._camera_id]["event_ring_on"]:
                return "mdi:bell-ring-outline"
            else:
                return "mdi:doorbell-video"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}

        attrs[ATTR_ATTRIBUTION] = DEFAULT_ATTRIBUTION
        attrs[ATTR_BRAND] = DEFAULT_BRAND
        attrs[ATTR_FRIENDLY_NAME] = self._name
        if self._device_class == DEVICE_CLASS_DOORBELL:
            attrs[ATTR_LAST_TRIP_TIME] = self.coordinator.data[self._camera_id][
                "last_ring"
            ]
        else:
            attrs[ATTR_LAST_TRIP_TIME] = self.coordinator.data[self._camera_id][
                "last_motion"
            ]
            attrs[ATTR_EVENT_SCORE] = self.coordinator.data[self._camera_id][
                "event_score"
            ]
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
