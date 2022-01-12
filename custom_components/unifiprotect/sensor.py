"""This component provides sensors for UniFi Protect."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DATA_BYTES,
    DATA_RATE_BYTES_PER_SECOND,
    DATA_RATE_MEGABITS_PER_SECOND,
    ELECTRIC_POTENTIAL_VOLT,
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    TEMP_CELSIUS,
    TIME_SECONDS,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from pyunifiprotect.data import NVR, Camera, Event
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel

from .const import DOMAIN
from .data import ProtectData
from .entity import (
    EventThumbnailMixin,
    ProtectDeviceEntity,
    ProtectNVREntity,
    async_all_device_entities,
)
from .models import ProtectRequiredKeysMixin

_LOGGER = logging.getLogger(__name__)
DETECTED_OBJECT_NONE = "none"
DEVICE_CLASS_DETECTION = "unifiprotect__detection"


@dataclass
class ProtectSensorEntityDescription(ProtectRequiredKeysMixin, SensorEntityDescription):
    """Describes UniFi Protect Sensor entity."""

    precision: int | None = None

    def get_ufp_value(self, obj: ProtectAdoptableDeviceModel | NVR) -> Any:
        """Return value from UniFi Protect device."""
        value = super().get_ufp_value(obj)

        if isinstance(value, float) and self.precision:
            value = round(value, self.precision)
        return value


def _get_uptime(obj: ProtectAdoptableDeviceModel | NVR) -> datetime | None:
    if obj.up_since is None:
        return None

    # up_since can vary slightly over time
    # truncate to ensure no extra state_change events fire
    return obj.up_since.replace(second=0, microsecond=0)


def _get_nvr_recording_capacity(obj: Any) -> int:
    assert isinstance(obj, NVR)

    if obj.storage_stats.capacity is None:
        return 0

    return int(obj.storage_stats.capacity.total_seconds())


def _get_nvr_memory(obj: Any) -> float | None:
    assert isinstance(obj, NVR)

    memory = obj.system_info.memory
    if memory.available is None or memory.total is None:
        return None
    return (1 - memory.available / memory.total) * 100


ALL_DEVICES_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        ufp_value_fn=_get_uptime,
    ),
    ProtectSensorEntityDescription(
        key="ble_signal",
        name="Bluetooth Signal Strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="bluetooth_connection_state.signal_strength",
        ufp_required_field="bluetooth_connection_state.signal_strength",
    ),
    ProtectSensorEntityDescription(
        key="phy_rate",
        name="Link Speed",
        native_unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="wired_connection_state.phy_rate",
        ufp_required_field="wired_connection_state.phy_rate",
    ),
    ProtectSensorEntityDescription(
        key="wifi_signal",
        name="WiFi Signal Strength",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="wifi_connection_state.signal_strength",
        ufp_required_field="wifi_connection_state.signal_strength",
    ),
)

CAMERA_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="oldest_recording",
        name="Oldest Recording",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        ufp_value="stats.video.recording_start",
    ),
    ProtectSensorEntityDescription(
        key="storage_used",
        name="Storage Used",
        native_unit_of_measurement=DATA_BYTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="stats.storage.used",
    ),
    ProtectSensorEntityDescription(
        key="write_rate",
        name="Disk Write Rate",
        native_unit_of_measurement=DATA_RATE_BYTES_PER_SECOND,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="stats.storage.rate",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="voltage",
        name="Voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="voltage",
        # no feature flag, but voltage will be null if device does not have voltage sensor
        # (i.e. is not G4 Doorbell or not on 1.20.1+)
        ufp_required_field="voltage",
        precision=2,
    ),
)

CAMERA_DISABLED_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="stats_rx",
        name="Received Data",
        native_unit_of_measurement=DATA_BYTES,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        ufp_value="stats.rx_bytes",
    ),
    ProtectSensorEntityDescription(
        key="stats_tx",
        name="Transferred Data",
        native_unit_of_measurement=DATA_BYTES,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.TOTAL_INCREASING,
        ufp_value="stats.tx_bytes",
    ),
)

SENSE_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="battery_level",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="battery_status.percentage",
    ),
    ProtectSensorEntityDescription(
        key="light_level",
        name="Light Level",
        native_unit_of_measurement=LIGHT_LUX,
        device_class=SensorDeviceClass.ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="stats.light.value",
    ),
    ProtectSensorEntityDescription(
        key="humidity_level",
        name="Humidity Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="stats.humidity.value",
    ),
    ProtectSensorEntityDescription(
        key="temperature_level",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="stats.temperature.value",
    ),
)

NVR_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="uptime",
        name="Uptime",
        icon="mdi:clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        ufp_value_fn=_get_uptime,
    ),
    ProtectSensorEntityDescription(
        key="storage_utilization",
        name="Storage Utilization",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:harddisk",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.utilization",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="record_rotating",
        name="Type: Timelapse Video",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:server",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.storage_distribution.timelapse_recordings.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="record_timelapse",
        name="Type: Continuous Video",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:server",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.storage_distribution.continuous_recordings.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="record_detections",
        name="Type: Detections Video",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:server",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.storage_distribution.detections_recordings.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="resolution_HD",
        name="Resolution: HD Video",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:cctv",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.storage_distribution.hd_usage.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="resolution_4K",
        name="Resolution: 4K Video",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:cctv",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.storage_distribution.uhd_usage.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="resolution_free",
        name="Resolution: Free Space",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:cctv",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="storage_stats.storage_distribution.free.percentage",
        precision=2,
    ),
    ProtectSensorEntityDescription(
        key="record_capacity",
        name="Recording Capacity",
        native_unit_of_measurement=TIME_SECONDS,
        icon="mdi:record-rec",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value_fn=_get_nvr_recording_capacity,
    ),
)

NVR_DISABLED_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="cpu_utilization",
        name="CPU Utilization",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:speedometer",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="system_info.cpu.average_load",
    ),
    ProtectSensorEntityDescription(
        key="cpu_temperature",
        name="CPU Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value="system_info.cpu.temperature",
    ),
    ProtectSensorEntityDescription(
        key="memory_utilization",
        name="Memory Utilization",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:memory",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        ufp_value_fn=_get_nvr_memory,
        precision=2,
    ),
)

MOTION_SENSORS: tuple[ProtectSensorEntityDescription, ...] = (
    ProtectSensorEntityDescription(
        key="detected_object",
        name="Detected Object",
        device_class=DEVICE_CLASS_DETECTION,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for UniFi Protect integration."""
    data: ProtectData = hass.data[DOMAIN][entry.entry_id]
    entities: list[ProtectDeviceEntity] = async_all_device_entities(
        data,
        ProtectDeviceSensor,
        all_descs=ALL_DEVICES_SENSORS,
        camera_descs=CAMERA_SENSORS + CAMERA_DISABLED_SENSORS,
        sense_descs=SENSE_SENSORS,
    )
    entities += _async_motion_entities(data)
    entities += _async_nvr_entities(data)

    async_add_entities(entities)


@callback
def _async_motion_entities(
    data: ProtectData,
) -> list[ProtectDeviceEntity]:
    entities: list[ProtectDeviceEntity] = []
    for device in data.api.bootstrap.cameras.values():
        if not device.feature_flags.has_smart_detect:
            continue

        for description in MOTION_SENSORS:
            entities.append(ProtectEventSensor(data, device, description))
            _LOGGER.debug(
                "Adding sensor entity %s for %s",
                description.name,
                device.name,
            )

    return entities


@callback
def _async_nvr_entities(
    data: ProtectData,
) -> list[ProtectDeviceEntity]:
    entities: list[ProtectDeviceEntity] = []
    device = data.api.bootstrap.nvr
    for description in NVR_SENSORS + NVR_DISABLED_SENSORS:
        entities.append(ProtectNVRSensor(data, device, description))
        _LOGGER.debug("Adding NVR sensor entity %s", description.name)

    return entities


class ProtectDeviceSensor(ProtectDeviceEntity, SensorEntity):
    """A Ubiquiti UniFi Protect Sensor."""

    entity_description: ProtectSensorEntityDescription

    def __init__(
        self,
        data: ProtectData,
        device: ProtectAdoptableDeviceModel,
        description: ProtectSensorEntityDescription,
    ) -> None:
        """Initialize an UniFi Protect sensor."""
        super().__init__(data, device, description)

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()
        self._attr_native_value = self.entity_description.get_ufp_value(self.device)


class ProtectNVRSensor(ProtectNVREntity, SensorEntity):
    """A Ubiquiti UniFi Protect Sensor."""

    entity_description: ProtectSensorEntityDescription

    def __init__(
        self,
        data: ProtectData,
        device: NVR,
        description: ProtectSensorEntityDescription,
    ) -> None:
        """Initialize an UniFi Protect sensor."""
        super().__init__(data, device, description)

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()
        self._attr_native_value = self.entity_description.get_ufp_value(self.device)


class ProtectEventSensor(ProtectDeviceSensor, EventThumbnailMixin):
    """A UniFi Protect Device Sensor with access tokens."""

    device: Camera

    @callback
    def _async_get_event(self) -> Event | None:
        """Get event from Protect device."""

        event: Event | None = None
        if (
            self.device.is_smart_detected
            and self.device.last_smart_detect_event is not None
            and len(self.device.last_smart_detect_event.smart_detect_types) > 0
        ):
            event = self.device.last_smart_detect_event

        return event

    @callback
    def _async_update_device_from_protect(self) -> None:
        # do not call ProtectDeviceSensor method since we want event to get value here
        EventThumbnailMixin._async_update_device_from_protect(self)
        if self._event is None:
            self._attr_native_value = DETECTED_OBJECT_NONE
        else:
            self._attr_native_value = self._event.smart_detect_types[0].value
