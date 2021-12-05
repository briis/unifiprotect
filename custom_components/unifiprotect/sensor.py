"""This component provides sensors for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from typing import Any, Callable, Sequence

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_ILLUMINANCE,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_TIMESTAMP,
    ENTITY_CATEGORY_DIAGNOSTIC,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.data import Light, ModelType
from pyunifiprotect.data.base import ProtectDeviceModel
from pyunifiprotect.data.nvr import NVR

from .const import ATTR_ENABLED_AT, DEVICES_THAT_ADOPT, DEVICES_WITH_CAMERA, DOMAIN
from .data import UnifiProtectData
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData
from .utils import above_ha_version, get_nested_attr

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[ModelType]
    ufp_value: str | None
    precision: int | None


@dataclass
class UnifiProtectSensorEntityDescription(
    SensorEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Sensor entity."""


_KEY_MEMORY = "memory_utilization"
_KEY_DISK = "storage_utilization"
_KEY_RECORD_ROTATE = "record_rotating"
_KEY_RECORD_TIMELAPSE = "record_timelapse"
_KEY_RECORD_DETECTIONS = "record_detections"
_KEY_RES_HD = "resolution_HD"
_KEY_RES_4K = "resolution_4K"
_KEY_RES_FREE = "resolution_free"
_KEY_CAPACITY = "record_capacity"

SENSOR_TYPES: tuple[UnifiProtectSensorEntityDescription, ...] = (
    UnifiProtectSensorEntityDescription(
        key="motion_recording",
        name="Motion Recording",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_value="recording_settings.mode",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        device_class=DEVICE_CLASS_TIMESTAMP,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        ufp_device_types=DEVICES_THAT_ADOPT | {ModelType.NVR},
        ufp_value="up_since",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="light_turn_on",
        name="Light Turn On",
        icon="mdi:leak",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.LIGHT},
        ufp_value="light_mode_settings.mode",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="battery_status.percentage",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="light_level",
        name="Light Level",
        native_unit_of_measurement="lx",
        device_class=DEVICE_CLASS_ILLUMINANCE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="stats.light.value",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="humidity_level",
        name="Humidity Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_HUMIDITY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="stats.humidity.value",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="temperature_level",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="stats.temperature.value",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="ble_signal",
        name="Bluetooth Signal Strength",
        native_unit_of_measurement="dB",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.SENSOR},
        ufp_value="bluetooth_connection_state.signal_strength",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="cpu_utilization",
        name="CPU Utilization",
        native_unit_of_measurement="%",
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="system_info.cpu.average_load",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key="cpu_temperature",
        name="CPU Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="system_info.cpu.temperature",
        precision=None,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_MEMORY,
        name="Memory Utilization",
        native_unit_of_measurement="%",
        icon="mdi:memory",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value=None,
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_DISK,
        name="Storage Utilization",
        native_unit_of_measurement="%",
        icon="mdi:harddisk",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.utilization",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_RECORD_TIMELAPSE,
        name="Type: Timelapse Video",
        native_unit_of_measurement="%",
        icon="mdi:server",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.storage_distribution.timelapse_recordings.percentage",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_RECORD_ROTATE,
        name="Type: Continuous Video",
        native_unit_of_measurement="%",
        icon="mdi:server",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.storage_distribution.continuous_recordings.percentage",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_RECORD_DETECTIONS,
        name="Type: Detections Video",
        native_unit_of_measurement="%",
        icon="mdi:server",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.storage_distribution.detections_recordings.percentage",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_RES_HD,
        name="Resolution: HD Video",
        native_unit_of_measurement="%",
        icon="mdi:cctv",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.storage_distribution.hd_usage.percentage",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_RES_4K,
        name="Resolution: 4K Video",
        native_unit_of_measurement="%",
        icon="mdi:cctv",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.storage_distribution.uhd_usage.percentage",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_RES_FREE,
        name="Resolution: Free Space",
        native_unit_of_measurement="%",
        icon="mdi:cctv",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.storage_distribution.free.percentage",
        precision=3,
    ),
    UnifiProtectSensorEntityDescription(
        key=_KEY_CAPACITY,
        name="Recording Capcity",
        native_unit_of_measurement="s",
        icon="mdi:record-rec",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_types={ModelType.NVR},
        ufp_value="storage_stats.capacity",
        precision=3,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
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
        protect: ProtectApiClient,
        protect_data: UnifiProtectData,
        device: ProtectDeviceModel,
        description: UnifiProtectSensorEntityDescription,
    ):
        """Initialize an Unifi Protect sensor."""
        self.entity_description: UnifiProtectSensorEntityDescription = description
        super().__init__(protect, protect_data, device, description)
        self._attr_name = f"{self.device.name} {self.entity_description.name}"

    @callback
    def _async_time_has_changed(self, new_time: datetime) -> bool:
        if not hasattr(self, "_attr_native_value") or not self._attr_native_value:
            return True

        assert isinstance(self._attr_native_value, datetime)
        return abs((self._attr_native_value - new_time).total_seconds()) > 5

    @callback
    def _async_update_device_from_protect(self) -> None:
        # protection to prevent uptime from changing if UniFi Protect changes values slightly
        super()._async_update_device_from_protect()

        if self.entity_description.ufp_value is None:
            assert isinstance(self.device, NVR)
            memory = self.device.system_info.memory
            self._attr_native_value = (1 - memory.available / memory.total) * 100
            return

        new_value = get_nested_attr(self.device, self.entity_description.ufp_value)
        if isinstance(new_value, timedelta):
            new_value = new_value.total_seconds()

        if isinstance(new_value, datetime):
            if not self._async_time_has_changed(new_value):
                return

            if not above_ha_version(2021, 12):
                new_value = new_value.isoformat()
        elif isinstance(new_value, float) and self.entity_description.precision:
            new_value = round(new_value, self.entity_description.precision)

        self._attr_native_value = new_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the device state attributes."""
        if isinstance(self.device, Light):
            return {
                **super().extra_state_attributes,
                ATTR_ENABLED_AT: self.device.light_mode_settings.enable_at.value,
            }
        return super().extra_state_attributes
