"""This component provides binary sensors for UniFi Protect."""
from __future__ import annotations

import asyncio
from copy import copy
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any, Callable, Sequence
from urllib.parse import urlencode

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    DEVICE_CLASS_PROBLEM,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_LAST_TRIP_TIME,
    ATTR_MODEL,
    ENTITY_CATEGORY_DIAGNOSTIC,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from pyunifiprotect.data import NVR, Camera, Event, Light, Sensor
from pyunifiprotect.utils import utc_now

from .const import ATTR_EVENT_SCORE, ATTR_EVENT_THUMB, DOMAIN
from .data import ProtectData
from .entity import (
    AccessTokenMixin,
    ProtectDeviceEntity,
    ProtectNVREntity,
    async_all_device_entities,
)
from .models import ProtectRequiredKeysMixin
from .utils import get_nested_attr
from .views import ThumbnailProxyView

_LOGGER = logging.getLogger(__name__)


# Remove when 3.8 support is dropped
if TYPE_CHECKING:
    TaskClass = asyncio.Task[None]
else:
    TaskClass = asyncio.Task


@dataclass
class ProtectBinaryEntityDescription(
    ProtectRequiredKeysMixin, BinarySensorEntityDescription
):
    """Describes UniFi Protect Binary Sensor entity."""


_KEY_DOORBELL = "doorbell"
_KEY_MOTION = "motion"
_KEY_DOOR = "door"
_KEY_DARK = "dark"
_KEY_BATTERY_LOW = "battery_low"
_KEY_DISK_HEALTH = "disk_health"

CAMERA_SENSORS: tuple[ProtectBinaryEntityDescription, ...] = (
    ProtectBinaryEntityDescription(
        key=_KEY_DOORBELL,
        name="Doorbell",
        device_class=DEVICE_CLASS_OCCUPANCY,
        icon="mdi:doorbell-video",
        ufp_required_field="feature_flags.has_chime",
        ufp_value="is_ringing",
    ),
    ProtectBinaryEntityDescription(
        key=_KEY_DARK,
        name="Is Dark",
        icon="mdi:brightness-6",
        ufp_value="is_dark",
    ),
)

LIGHT_SENSORS: tuple[ProtectBinaryEntityDescription, ...] = (
    ProtectBinaryEntityDescription(
        key=_KEY_DARK,
        name="Is Dark",
        icon="mdi:brightness-6",
        ufp_value="is_dark",
    ),
    ProtectBinaryEntityDescription(
        key=_KEY_MOTION,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_value="is_pir_motion_detected",
    ),
)

SENSE_SENSORS: tuple[ProtectBinaryEntityDescription, ...] = (
    ProtectBinaryEntityDescription(
        key=_KEY_DOOR,
        name="Door",
        device_class=DEVICE_CLASS_DOOR,
        ufp_value="is_opened",
    ),
    ProtectBinaryEntityDescription(
        key=_KEY_BATTERY_LOW,
        name="Battery low",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_value="battery_status.is_low",
    ),
    ProtectBinaryEntityDescription(
        key=_KEY_MOTION,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_value="is_motion_detected",
    ),
)

MOTION_SENSORS: tuple[ProtectBinaryEntityDescription, ...] = (
    ProtectBinaryEntityDescription(
        key=_KEY_MOTION,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_value="is_motion_detected",
    ),
)

DISK_SENSORS: tuple[ProtectBinaryEntityDescription, ...] = (
    ProtectBinaryEntityDescription(
        key=_KEY_DISK_HEALTH,
        name="Disk {index} Health",
        device_class=DEVICE_CLASS_PROBLEM,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Set up binary sensors for UniFi Protect integration."""
    data: ProtectData = hass.data[DOMAIN][entry.entry_id]
    entities: list[ProtectDeviceEntity] = async_all_device_entities(
        data,
        ProtectDeviceBinarySensor,
        camera_descs=CAMERA_SENSORS,
        light_descs=LIGHT_SENSORS,
        sense_descs=SENSE_SENSORS,
    )
    entities += _async_nvr_entities(data)
    entities += _async_motion_entities(data)

    async_add_entities(entities)


@callback
def _async_motion_entities(
    data: ProtectData,
) -> list[ProtectDeviceEntity]:
    entities: list[ProtectDeviceEntity] = []
    for device in data.api.bootstrap.cameras.values():
        for description in MOTION_SENSORS:
            entities.append(ProtectAccessTokenBinarySensor(data, device, description))
            _LOGGER.debug(
                "Adding binary sensor entity %s for %s",
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
    for index, _ in enumerate(device.system_info.storage.devices):
        for description in DISK_SENSORS:
            entities.append(
                ProtectDiskBinarySensor(data, device, description, index=index)
            )
            _LOGGER.debug(
                "Adding binary sensor entity %s",
                (description.name or "{index}").format(index=index),
            )

    return entities


class ProtectDeviceBinarySensor(ProtectDeviceEntity, BinarySensorEntity):
    """A UniFi Protect Device Binary Sensor."""

    def __init__(
        self,
        data: ProtectData,
        description: ProtectBinaryEntityDescription,
        device: Camera | Light | Sensor | None = None,
    ) -> None:
        """Initialize the Binary Sensor."""

        if device and not hasattr(self, "device"):
            self.device: Camera | Light | Sensor = device
        self.entity_description: ProtectBinaryEntityDescription = description
        super().__init__(data)
        self._doorbell_callback: TaskClass | None = None

    @callback
    def _async_update_extra_attrs_from_protect(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        key = self.entity_description.key

        if key == _KEY_DARK:
            return attrs

        if key == _KEY_DOORBELL:
            assert isinstance(self.device, Camera)
            attrs[ATTR_LAST_TRIP_TIME] = self.device.last_ring
        elif isinstance(self.device, Sensor):
            if key in (_KEY_MOTION, _KEY_DOOR):
                if key == _KEY_MOTION:
                    last_trip = self.device.motion_detected_at
                else:
                    last_trip = self.device.open_status_changed_at

                attrs[ATTR_LAST_TRIP_TIME] = last_trip
        elif isinstance(self.device, Light):
            if key == _KEY_MOTION:
                attrs[ATTR_LAST_TRIP_TIME] = self.device.last_motion

        return attrs

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()

        if self.entity_description.ufp_value is None:
            return

        self._attr_is_on = get_nested_attr(
            self.device, self.entity_description.ufp_value
        )
        if self.entity_description.key == _KEY_DOORBELL:
            print(
                self.entity_description.name,
                self._attr_is_on,
                self.device.is_ringing,
                self.device.last_ring,
            )

    @callback
    async def _async_wait_for_doorbell(self, end_time: datetime) -> None:
        _LOGGER.debug("Doorbell callback started")
        while utc_now() < end_time:
            await asyncio.sleep(1)
        _LOGGER.debug("Doorbell callback ended")
        self._async_updated_event()


class ProtectDiskBinarySensor(ProtectNVREntity, BinarySensorEntity):
    """A UniFi Protect NVR Disk Binary Sensor."""

    def __init__(
        self,
        data: ProtectData,
        device: NVR,
        description: ProtectBinaryEntityDescription,
        index: int,
    ) -> None:
        """Initialize the Binary Sensor."""
        description = copy(description)
        description.key = f"{description.key}_{index}"
        description.name = (description.name or "{index}").format(index=index)
        self._index = index
        self.entity_description: ProtectBinaryEntityDescription = description
        super().__init__(data, device)

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()

        if not self.entity_description.key.startswith(_KEY_DISK_HEALTH):
            return

        disks = self.device.system_info.storage.devices
        disk_available = len(disks) > self._index
        self._attr_available = self._attr_available and disk_available
        if disk_available:
            disk = disks[self._index]
            self._attr_is_on = not disk.healthy
            self._extra_state_attributes = {ATTR_MODEL: disk.model}


class ProtectAccessTokenBinarySensor(ProtectDeviceBinarySensor, AccessTokenMixin):
    """A UniFi Protect Device Binary Sensor with access tokens."""

    def __init__(
        self,
        data: ProtectData,
        device: Camera,
        description: ProtectBinaryEntityDescription,
    ) -> None:
        """Init a binary sensor that uses access tokens."""
        self.device: Camera = device
        super().__init__(data, description=description)
        self._event: Event | None = None

    @callback
    def _async_update_device_from_protect(self) -> None:
        self._event = None
        if (
            self.device.is_smart_detected
            and self.device.last_smart_detect_event is not None
            and len(self.device.last_smart_detect_event.smart_detect_types) > 0
        ):
            self._event = self.device.last_smart_detect_event
        elif (
            self.device.is_motion_detected and self.device.last_motion_event is not None
        ):
            self._event = self.device.last_motion_event
        super()._async_update_device_from_protect()

    @callback
    def _async_update_extra_attrs_from_protect(self) -> dict[str, Any]:
        # Camera motion sensors with object detection
        attrs: dict[str, Any] = {
            **super()._async_update_extra_attrs_from_protect(),
            ATTR_EVENT_SCORE: 0,
            ATTR_EVENT_THUMB: None,
        }

        if self._event is None:
            return attrs

        if len(self.access_tokens) > 0:
            params = urlencode(
                {"entity_id": self.entity_id, "token": self.access_tokens[-1]}
            )
            attrs[ATTR_EVENT_THUMB] = (
                ThumbnailProxyView.url.format(event_id=self._event.id) + f"?{params}"
            )

        return attrs
