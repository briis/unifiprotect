"""This component provides sensors for Unifi Protect."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import HomeAssistantType

from .const import ATTR_CAMERA_TYPE, DEFAULT_ATTRIBUTION, DOMAIN, TYPE_RECORD_NEVER
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = {
    "motion_recording": [
        "Motion Recording",
        None,
        ["video-outline", "video-off-outline"],
    ]
}

_SENSOR_NAME = 0
_SENSOR_UNITS = 1
_SENSOR_ICONS = 2

_ICON_ON = 0
_ICON_OFF = 1


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up sensors for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]

    if not protect_data.data:
        return

    sensors = []
    for sensor in SENSOR_TYPES:
        for camera_id in protect_data.data:
            sensors.append(
                UnifiProtectSensor(
                    upv_object, protect_data, server_info, camera_id, sensor
                )
            )
            _LOGGER.debug("UNIFIPROTECT SENSOR CREATED: %s", sensor)

    async_add_entities(sensors)

    return True


class UnifiProtectSensor(UnifiProtectEntity, Entity):
    """A Ubiquiti Unifi Protect Sensor."""

    def __init__(self, upv_object, protect_data, server_info, camera_id, sensor):
        """Initialize an Unifi Protect sensor."""
        super().__init__(upv_object, protect_data, server_info, camera_id, sensor)
        sensor_type = SENSOR_TYPES[sensor]
        self._name = f"{sensor_type[_SENSOR_NAME]} {self._camera_data['name']}"
        self._units = sensor_type[_SENSOR_UNITS]
        self._icons = sensor_type[_SENSOR_ICONS]
        self._camera_type = self._camera_data["model"]

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._camera_data["recording_mode"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        icon_id = _ICON_ON if self.state != TYPE_RECORD_NEVER else _ICON_OFF
        return f"mdi:{self._icons[icon_id]}"

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
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_CAMERA_TYPE: self._camera_type,
        }
