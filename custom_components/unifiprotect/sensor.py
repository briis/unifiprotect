"""This component provides sensors for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_ENABLED_AT,
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_SENSOR,
    DEVICES_WITH_CAMERA,
    DOMAIN,
    ENTITY_CATEGORY_DIAGNOSTIC,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[str]
    ufp_value: str


@dataclass
class UnifiProtectSensorEntityDescription(
    SensorEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Sensor entity."""


SENSOR_TYPES: tuple[UnifiProtectSensorEntityDescription, ...] = (
    UnifiProtectSensorEntityDescription(
        key="motion_recording",
        name="Motion Recording",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_value="recording_mode",
    ),
    UnifiProtectSensorEntityDescription(
        key="light_turn_on",
        name="Light Turn On",
        icon="mdi:leak",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={DEVICE_TYPE_LIGHT},
        ufp_value="motion_mode",
    ),
    UnifiProtectSensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={DEVICE_TYPE_SENSOR},
        ufp_value="battery_status",
    ),
    UnifiProtectSensorEntityDescription(
        key="light_level",
        name="Light Level",
        native_unit_of_measurement="lx",
        device_class=DEVICE_CLASS_ILLUMINANCE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={DEVICE_TYPE_SENSOR},
        ufp_value="light_value",
    ),
    UnifiProtectSensorEntityDescription(
        key="humidity_level",
        name="Humidity Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_HUMIDITY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={DEVICE_TYPE_SENSOR},
        ufp_value="humidity_value",
    ),
    UnifiProtectSensorEntityDescription(
        key="temperature_level",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={DEVICE_TYPE_SENSOR},
        ufp_value="temperature_value",
    ),
    UnifiProtectSensorEntityDescription(
        key="ble_signal",
        name="Bluetooth Signal Strength",
        native_unit_of_measurement="dB",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={DEVICE_TYPE_SENSOR},
        ufp_value="bluetooth_signal",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up sensors for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data.upv
    protect_data = entry_data.protect_data
    server_info = entry_data.server_info

    sensors = []
    for description in SENSOR_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            sensors.append(
                UnifiProtectSensor(
                    upv_object, protect_data, server_info, device.device_id, description
                )
            )
            _LOGGER.debug(
                "Adding sensor entity %s for %s",
                description.name,
                device.data.get("name"),
            )

    async_add_entities(sensors)


class UnifiProtectSensor(UnifiProtectEntity, SensorEntity):
    """A Ubiquiti Unifi Protect Sensor."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectSensorEntityDescription,
    ):
        """Initialize an Unifi Protect sensor."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._attr_name = f"{self.entity_description.name} {self._device_data['name']}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._device_data[self.entity_description.ufp_value]

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        if self._device_type == DEVICE_TYPE_LIGHT:
            return {
                **super().extra_state_attributes,
                ATTR_ENABLED_AT: self._device_data["motion_mode_enabled_at"],
            }
        return super().extra_state_attributes
