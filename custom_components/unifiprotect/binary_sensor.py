"""This component provides binary sensors for Unifi Protect."""
import logging

try:
    from homeassistant.components.binary_sensor import (
        BinarySensorEntity as BinarySensorDevice,
    )
except ImportError:
    # Prior to HA v0.110
    from homeassistant.components.binary_sensor import BinarySensorDevice

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LAST_TRIP_TIME
from homeassistant.helpers.typing import HomeAssistantType


from .const import (
    ATTR_EVENT_LENGTH,
    ATTR_EVENT_OBJECT,
    ATTR_EVENT_SCORE,
    DEFAULT_ATTRIBUTION,
    DEVICE_TYPE_MOTION,
    DEVICE_TYPE_DOORBELL,
    DOMAIN,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

PROTECT_TO_HASS_DEVICE_CLASS = {
    DEVICE_TYPE_DOORBELL: DEVICE_CLASS_OCCUPANCY,
    DEVICE_TYPE_MOTION: DEVICE_CLASS_MOTION,
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up binary sensors for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    if not protect_data.data:
        return

    sensors = []
    for camera_id in protect_data.data:
        camera_data = protect_data.data[camera_id]
        if camera_data["type"] == DEVICE_TYPE_DOORBELL:
            sensors.append(
                UnifiProtectBinarySensor(
                    upv_object, protect_data, camera_id, DEVICE_TYPE_DOORBELL
                )
            )
            _LOGGER.debug(
                "UNIFIPROTECT DOORBELL SENSOR CREATED: %s",
                camera_data["name"],
            )

        sensors.append(
            UnifiProtectBinarySensor(
                upv_object, protect_data, camera_id, DEVICE_TYPE_MOTION
            )
        )
        _LOGGER.debug("UNIFIPROTECT MOTION SENSOR CREATED: %s", camera_data["name"])

    async_add_entities(sensors)

    return True


class UnifiProtectBinarySensor(UnifiProtectEntity, BinarySensorDevice):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, upv_object, protect_data, camera_id, sensor_type):
        """Initialize the Binary Sensor."""
        super().__init__(upv_object, protect_data, camera_id, sensor_type)
        self._name = f"{sensor_type.capitalize()} {self._camera_data['name']}"
        self._device_class = PROTECT_TO_HASS_DEVICE_CLASS.get(sensor_type)

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._sensor_type == DEVICE_TYPE_DOORBELL:
            _LOGGER.debug(
                f"RING {self._camera_data['event_ring_on']} - TYPE: {self._camera_data['event_type']}"
            )
            return self._camera_data["event_ring_on"]
        # _LOGGER.debug(f"MOTION {self._camera_data['event_on']}: {self._name}")
        return self._camera_data["event_on"]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def icon(self):
        """Select icon to display in Frontend."""
        if self._sensor_type == DEVICE_TYPE_DOORBELL:
            if self._camera_data["event_ring_on"]:
                return "mdi:bell-ring-outline"
            return "mdi:doorbell-video"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if self._sensor_type == DEVICE_TYPE_DOORBELL:
            return {
                ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
                ATTR_LAST_TRIP_TIME: self._camera_data["last_ring"],
            }
        if (
            self._camera_data["event_object"] is not None
            and len(self._camera_data["event_object"]) > 0
        ):
            detected_object = self._camera_data["event_object"][0]
            _LOGGER.debug(
                f"OBJECTS: {self._camera_data['event_object']} on {self._name}"
            )
        else:
            detected_object = "None Identified"
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_LAST_TRIP_TIME: self._camera_data["last_motion"],
            ATTR_EVENT_SCORE: self._camera_data["event_score"],
            ATTR_EVENT_LENGTH: self._camera_data["event_length"],
            ATTR_EVENT_OBJECT: detected_object,
        }
