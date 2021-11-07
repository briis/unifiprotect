"""This component provides sensors for Unifi Protect."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)

# from homeassistant.const import ATTR_ATTRIBUTION, ENTITY_CATEGORY_DIAGNOSTIC
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_DEVICE_MODEL,
    ATTR_ENABLED_AT,
    DEFAULT_ATTRIBUTION,
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_SENSOR,
    DEVICES_WITH_CAMERA,
    DOMAIN,
    ENTITY_CATEGORY_DIAGNOSTIC,
    TYPE_RECORD_NEVER,
    TYPE_RECORD_OFF,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: list[dict[str, Any]] = {
    "motion_recording": [
        "Motion Recording",
        None,
        ["video-outline", "video-off-outline"],
        DEVICES_WITH_CAMERA,
        None,
    ],
    "light_turn_on": [
        "Light Turn On",
        None,
        ["leak", "leak-off"],
        DEVICE_TYPE_LIGHT,
        None,
    ],
    "battery_level": [
        "Battery Level",
        "%",
        None,
        DEVICE_TYPE_SENSOR,
        DEVICE_CLASS_BATTERY,
    ],
    "light_level": [
        "Light Level",
        "lx",
        None,
        DEVICE_TYPE_SENSOR,
        DEVICE_CLASS_ILLUMINANCE,
    ],
    "humidity_level": [
        "Humidity Level",
        "%",
        None,
        DEVICE_TYPE_SENSOR,
        DEVICE_CLASS_HUMIDITY,
    ],
    "temperature_level": [
        "Temperature",
        TEMP_CELSIUS,
        None,
        DEVICE_TYPE_SENSOR,
        DEVICE_CLASS_TEMPERATURE,
    ],
    "ble_signal": [
        "Bluetooth Signal Strength",
        "dB",
        None,
        DEVICE_TYPE_SENSOR,
        DEVICE_CLASS_SIGNAL_STRENGTH,
    ],
}

_SENSOR_NAME = 0
_SENSOR_UNITS = 1
_SENSOR_ICONS = 2
_SENSOR_MODEL = 3
_SENSOR_DEVICE_CLASS = 4

_ICON_ON = 0
_ICON_OFF = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up sensors for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]

    if not protect_data.data:
        return

    sensors = []
    for sensor, sensor_type in SENSOR_TYPES.items():
        for device_id in protect_data.data:
            if protect_data.data[device_id].get("type") in sensor_type[_SENSOR_MODEL]:
                sensors.append(
                    UnifiProtectSensor(
                        upv_object, protect_data, server_info, device_id, sensor
                    )
                )
                _LOGGER.debug("UNIFIPROTECT SENSOR CREATED: %s", sensor)

    async_add_entities(sensors)


class UnifiProtectSensor(UnifiProtectEntity, SensorEntity):
    """A Ubiquiti Unifi Protect Sensor."""

    def __init__(self, upv_object, protect_data, server_info, device_id, sensor):
        """Initialize an Unifi Protect sensor."""
        super().__init__(upv_object, protect_data, server_info, device_id, sensor)
        sensor_type = SENSOR_TYPES[sensor]
        self._name = f"{sensor_type[_SENSOR_NAME]} {self._device_data['name']}"
        self._units = sensor_type[_SENSOR_UNITS]
        self._icons = sensor_type[_SENSOR_ICONS]
        self._device_class = sensor_type[_SENSOR_DEVICE_CLASS]
        self._attr_entity_category = ENTITY_CATEGORY_DIAGNOSTIC

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self._device_type == DEVICE_TYPE_LIGHT:
            return self._device_data["motion_mode"]

        if self._device_type == DEVICE_TYPE_SENSOR:
            if self._device_class == DEVICE_CLASS_BATTERY:
                return self._device_data["battery_status"]
            if self._device_class == DEVICE_CLASS_HUMIDITY:
                return self._device_data["humidity_value"]
            if self._device_class == DEVICE_CLASS_ILLUMINANCE:
                return self._device_data["light_value"]
            if self._device_class == DEVICE_CLASS_SIGNAL_STRENGTH:
                return self._device_data["bluetooth_signal"]
            if self._device_class == DEVICE_CLASS_TEMPERATURE:
                return self._device_data["temperature_value"]
        return self._device_data["recording_mode"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        if self._device_class is not None:
            return

        if self._device_type == DEVICE_TYPE_LIGHT:
            icon_id = _ICON_ON if self.state != TYPE_RECORD_OFF else _ICON_OFF
            return f"mdi:{self._icons[icon_id]}"
        icon_id = _ICON_ON if self.state != TYPE_RECORD_NEVER else _ICON_OFF
        return f"mdi:{self._icons[icon_id]}"

    @property
    def native_unit_of_measurement(self):
        """Return the units of measurement."""
        return self._units

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attr = {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
        }
        if self._device_type == DEVICE_TYPE_LIGHT:
            attr[ATTR_ENABLED_AT] = self._device_data["motion_mode_enabled_at"]
        return attr
