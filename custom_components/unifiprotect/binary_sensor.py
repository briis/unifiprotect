""" This component provides binary sensors for Unifi Protect."""
import logging

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
    ATTR_LAST_TRIP_TIME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from .const import (
    ATTR_EVENT_SCORE,
    ATTR_EVENT_LENGTH,
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEVICE_CLASS_DOORBELL,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A Ubiquiti Unifi Protect Binary Sensor."""
    upv_object = hass.data[DOMAIN][entry.entry_id]["upv"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    if not coordinator.data:
        return

    sensors = []
    for camera in coordinator.data:
        if coordinator.data[camera]["type"] == DEVICE_CLASS_DOORBELL:
            sensors.append(
                UnifiProtectBinarySensor(
                    upv_object, coordinator, camera, DEVICE_CLASS_DOORBELL
                )
            )
            _LOGGER.debug(
                "UNIFIPROTECT DOORBELL SENSOR CREATED: %s",
                coordinator.data[camera]["name"],
            )

        sensors.append(
            UnifiProtectBinarySensor(
                upv_object, coordinator, camera, DEVICE_CLASS_MOTION
            )
        )
        _LOGGER.debug(
            "UNIFIPROTECT MOTION SENSOR CREATED: %s", coordinator.data[camera]["name"]
        )

    async_add_entities(sensors, True)

    return True


class UnifiProtectBinarySensor(UnifiProtectEntity, BinarySensorDevice):
    """A Unifi Protect Binary Sensor."""

    def __init__(self, upv_object, coordinator, camera_id, sensor_type):
        """Initialize the Binary Sensor."""
        super().__init__(upv_object, coordinator, camera_id, sensor_type)
        self._name = f"{sensor_type.capitalize()} {self._camera_data['name']}"
        self._device_class = sensor_type

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            return self._camera_data["event_ring_on"]
        else:
            return self._camera_data["event_on"]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def icon(self):
        """Select icon to display in Frontend."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            if self._camera_data["event_ring_on"]:
                return "mdi:bell-ring-outline"
            else:
                return "mdi:doorbell-video"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        if self._device_class == DEVICE_CLASS_DOORBELL:
            return {
                ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
                ATTR_LAST_TRIP_TIME: self._camera_data["last_ring"],
            }
        else:
            return {
                ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
                ATTR_LAST_TRIP_TIME: self._camera_data["last_motion"],
                ATTR_EVENT_SCORE: self._camera_data["event_score"],
                ATTR_EVENT_LENGTH: self._camera_data["event_length"],
            }
