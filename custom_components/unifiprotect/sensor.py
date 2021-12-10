"""This component provides sensors for UniFi Protect."""
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
from pyunifiprotect.data import Light
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel
from pyunifiprotect.data.nvr import NVR

from .const import ATTR_ENABLED_AT, DOMAIN
from .data import ProtectData
from .entity import ProtectDeviceEntity, ProtectNVREntity, async_all_device_entities
from .models import ProtectRequiredKeysMixin
from .utils import above_ha_version, get_nested_attr

_LOGGER = logging.getLogger(__name__)


@dataclass
class ProtectSensorEntityDescription(ProtectRequiredKeysMixin, SensorEntityDescription):
    """Describes UniFi Protect Sensor entity."""

    precision: int | None = None


_KEY_MEMORY = "memory_utilization"
_KEY_DISK = "storage_utilization"
_KEY_RECORD_ROTATE = "record_rotating"
_KEY_RECORD_TIMELAPSE = "record_timelapse"
_KEY_RECORD_DETECTIONS = "record_detections"
_KEY_RES_HD = "resolution_HD"
_KEY_RES_4K = "resolution_4K"
_KEY_RES_FREE = "resolution_free"
_KEY_CAPACITY = "record_capacity"

ALL_DEVICES_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        device_class=DEVICE_CLASS_TIMESTAMP,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        ufp_value="up_since",
    ),
    ProtectSensorEntityDescription(
        key="ble_signal",
        name="Bluetooth Signal Strength",
        native_unit_of_measurement="dB",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="bluetooth_connection_state.signal_strength",
        ufp_required_field="bluetooth_connection_state.signal_strength",
    ),
    ProtectSensorEntityDescription(
        key="phy_rate",
        name="Link Speed",
        native_unit_of_measurement="Mbps",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="wired_connection_state.phy_rate",
        ufp_required_field="wired_connection_state.phy_rate",
    ),
    ProtectSensorEntityDescription(
        key="wifi_signal",
        name="WiFi Signal Strength",
        native_unit_of_measurement="dB",
        device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="wifi_connection_state.signal_strength",
        ufp_required_field="wifi_connection_state.signal_strength",
    ),
)

CAMERA_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="motion_recording",
        name="Motion Recording",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="recording_settings.mode",
    ),
)

LIGHT_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="light_turn_on",
        name="Light Turn On",
        icon="mdi:leak",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="light_mode_settings.mode",
    ),
)

SENSE_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="battery_status.percentage",
    ),
    ProtectSensorEntityDescription(
        key="light_level",
        name="Light Level",
        native_unit_of_measurement="lx",
        device_class=DEVICE_CLASS_ILLUMINANCE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="stats.light.value",
    ),
    ProtectSensorEntityDescription(
        key="humidity_level",
        name="Humidity Level",
        native_unit_of_measurement="%",
        device_class=DEVICE_CLASS_HUMIDITY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="stats.humidity.value",
    ),
    ProtectSensorEntityDescription(
        key="temperature_level",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="stats.temperature.value",
    ),
)

NVR_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        device_class=DEVICE_CLASS_TIMESTAMP,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
        ufp_value="up_since",
    ),
    ProtectSensorEntityDescription(
        key="cpu_utilization",
        name="CPU Utilization",
        native_unit_of_measurement="%",
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="system_info.cpu.average_load",
    ),
    ProtectSensorEntityDescription(
        key="cpu_temperature",
        name="CPU Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=DEVICE_CLASS_TEMPERATURE,
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="system_info.cpu.temperature",
    ),
    ProtectSensorEntityDescription(
        key=_KEY_MEMORY,
        name="Memory Utilization",
        native_unit_of_measurement="%",
        icon="mdi:memory",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_DISK,
        name="Storage Utilization",
        native_unit_of_measurement="%",
        icon="mdi:harddisk",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.utilization",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_RECORD_TIMELAPSE,
        name="Type: Timelapse Video",
        native_unit_of_measurement="%",
        icon="mdi:server",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.storage_distribution.timelapse_recordings.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_RECORD_ROTATE,
        name="Type: Continuous Video",
        native_unit_of_measurement="%",
        icon="mdi:server",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.storage_distribution.continuous_recordings.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_RECORD_DETECTIONS,
        name="Type: Detections Video",
        native_unit_of_measurement="%",
        icon="mdi:server",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.storage_distribution.detections_recordings.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_RES_HD,
        name="Resolution: HD Video",
        native_unit_of_measurement="%",
        icon="mdi:cctv",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.storage_distribution.hd_usage.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_RES_4K,
        name="Resolution: 4K Video",
        native_unit_of_measurement="%",
        icon="mdi:cctv",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.storage_distribution.uhd_usage.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_RES_FREE,
        name="Resolution: Free Space",
        native_unit_of_measurement="%",
        icon="mdi:cctv",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.storage_distribution.free.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key=_KEY_CAPACITY,
        name="Recording Capcity",
        native_unit_of_measurement="s",
        icon="mdi:record-rec",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="storage_stats.capacity",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Set up sensors for UniFi Protect integration."""
    data: ProtectData = hass.data[DOMAIN][entry.entry_id]
    entities: list[ProtectDeviceEntity] = async_all_device_entities(
        data,
        ProtectDeviceSensor,
        all_descs=ALL_DEVICES_SENSORS,
        camera_descs=CAMERA_SENSORS,
        light_descs=LIGHT_SENSORS,
        sense_descs=SENSE_SENSORS,
    )
    entities += _async_nvr_entities(data)

    async_add_entities(entities)


@callback
def _async_nvr_entities(
    data: ProtectData,
) -> list[ProtectDeviceEntity]:
    entities: list[ProtectDeviceEntity] = []
    device = data.api.bootstrap.nvr
    for description in NVR_SENSORS:
        entities.append(ProtectNVRSensor(data, device, description))
        _LOGGER.debug("Adding NVR sensor entity %s", description.name)

    return entities


class SensorValueMixin(Entity):
    @callback
    def _clean_sensor_value(self, value: Any) -> Any:
        if isinstance(value, timedelta):
            value = int(value.total_seconds())
        elif isinstance(value, datetime):
            # UniFi Protect value can vary slightly over time
            # truncate to ensure no extra state_change events fire
            value = value.replace(second=0, microsecond=0)
            if not above_ha_version(2021, 12):
                value = value.isoformat()

        assert isinstance(self.entity_description, ProtectSensorEntityDescription)
        if isinstance(value, float) and self.entity_description.precision:
            value = round(value, self.entity_description.precision)

        return value


class ProtectDeviceSensor(SensorValueMixin, ProtectDeviceEntity, SensorEntity):
    """A Ubiquiti UniFi Protect Sensor."""

    def __init__(
        self,
        data: ProtectData,
        device: ProtectAdoptableDeviceModel,
        description: ProtectSensorEntityDescription,
    ):
        """Initialize an UniFi Protect sensor."""
        self.entity_description: ProtectSensorEntityDescription = description
        super().__init__(data, device)

    @callback
    def _async_update_extra_attrs_from_protect(self) -> dict[str, Any]:
        if isinstance(self.device, Light):
            return {
                ATTR_ENABLED_AT: self.device.light_mode_settings.enable_at.value,
            }
        return {}

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()

        if self.entity_description.ufp_value is None:
            return

        value = get_nested_attr(self.device, self.entity_description.ufp_value)
        self._attr_native_value = self._clean_sensor_value(value)


class ProtectNVRSensor(SensorValueMixin, ProtectNVREntity, SensorEntity):
    """A Ubiquiti UniFi Protect Sensor."""

    def __init__(
        self,
        data: ProtectData,
        device: NVR,
        description: ProtectSensorEntityDescription,
    ):
        """Initialize an UniFi Protect sensor."""
        self.entity_description: ProtectSensorEntityDescription = description
        super().__init__(data, device)

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()

        if self.entity_description.ufp_value is None:
            memory = self.device.system_info.memory
            value = (1 - memory.available / memory.total) * 100
        else:
            value = get_nested_attr(self.device, self.entity_description.ufp_value)

        self._attr_native_value = self._clean_sensor_value(value)
