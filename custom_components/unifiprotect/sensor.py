"""This component provides sensors for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from pyunifiprotect.data import Light, ModelType

from .const import (
    ATTR_ENABLED_AT,
    DEVICES_WITH_CAMERA,
    DEVICES_WITH_ENTITIES,
    DOMAIN,
    ENTITY_CATEGORY_DIAGNOSTIC,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData
from .utils import get_nested_attr

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[ModelType]
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
        ufp_value="recording_settings.mode",
    ),
    UnifiProtectSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        device_class=DEVICE_CLASS_TIMESTAMP,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        ufp_device_types=DEVICES_WITH_ENTITIES,
        ufp_value="up_since",
    ),
    UnifiProtectSensorEntityDescription(
        key="light_turn_on",
        name="Light Turn On",
        icon="mdi:leak",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.LIGHT},
        ufp_value="light_mode_settings.mode",
    ),
    UnifiProtectSensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="battery_status.percentage",
    ),
    UnifiProtectSensorEntityDescription(
        key="light_level",
        name="Light Level",
        native_unit_of_measurement="lx",
        device_class=DEVICE_CLASS_ILLUMINANCE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="stats.light.value",
    ),
    UnifiProtectSensorEntityDescription(
        key="humidity_level",
        name="Humidity Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_HUMIDITY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="stats.humidity.value",
    ),
    UnifiProtectSensorEntityDescription(
        key="temperature_level",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="stats.temperature.value",
    ),
    UnifiProtectSensorEntityDescription(
        key="ble_signal",
        name="Bluetooth Signal Strength",
        native_unit_of_measurement="dB",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="bluetooth_connection_state.signal_strength",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up sensors for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    sensors = []
    for description in SENSOR_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            sensors.append(
                UnifiProtectSensor(protect, protect_data, device, description)
            )
            _LOGGER.debug(
                "Adding sensor entity %s for %s",
                description.name,
                device.name,
            )

    async_add_entities(sensors)


class UnifiProtectSensor(UnifiProtectEntity, SensorEntity):
    """A Ubiquiti Unifi Protect Sensor."""

    def __init__(
        self,
        protect,
        protect_data,
        device,
        description: UnifiProtectSensorEntityDescription,
    ):
        """Initialize an Unifi Protect sensor."""
        super().__init__(protect, protect_data, device, description)
        self._attr_name = f"{self.device.name} {self.entity_description.name}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = get_nested_attr(self.device, self.entity_description.ufp_value)

        if isinstance(value, datetime):
            return value.replace(microsecond=0).isoformat()

        return value

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        if isinstance(self.device, Light):
            return {
                **super().extra_state_attributes,
                ATTR_ENABLED_AT: self.device.light_mode_settings.enable_at.value,
            }
        return super().extra_state_attributes
