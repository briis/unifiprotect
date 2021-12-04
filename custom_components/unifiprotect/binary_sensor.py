"""This component provides binary sensors for Unifi Protect."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
import itertools
import logging
from typing import TYPE_CHECKING, Any, Callable, Optional, Sequence

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_LAST_TRIP_TIME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel
from pyunifiprotect.data.devices import Camera, Light, Sensor
from pyunifiprotect.data.types import ModelType, SmartDetectObjectType
from pyunifiprotect.utils import utc_now

from .const import (
    ATTR_EVENT_OBJECT,
    ATTR_EVENT_SCORE,
    DOMAIN,
    ENTITY_CATEGORY_DIAGNOSTIC,
    RING_INTERVAL,
)
from .data import UnifiProtectData
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData
from .utils import get_nested_attr

_LOGGER = logging.getLogger(__name__)


# Remove when 3.8 support is dropped
if TYPE_CHECKING:
    TaskClass = asyncio.Task[None]
else:
    TaskClass = asyncio.Task


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_required_field: str | None
    ufp_value: str


@dataclass
class UnifiProtectBinaryEntityDescription(
    BinarySensorEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Binary Sensor entity."""


_KEY_DOORBELL = "doorbell"
_KEY_MOTION = "motion"
_KEY_DOOR = "door"
_KEY_DARK = "dark"
_KEY_BATTERY_LOW = "battery_low"


SENSE_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key=_KEY_DOOR,
        name="Door",
        device_class=DEVICE_CLASS_DOOR,
        ufp_required_field=None,
        ufp_value="is_opened",
    ),
    UnifiProtectBinaryEntityDescription(
        key=_KEY_BATTERY_LOW,
        name="Battery low",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_required_field=None,
        ufp_value="battery_status.is_low",
    ),
    UnifiProtectBinaryEntityDescription(
        key=_KEY_MOTION,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_required_field=None,
        ufp_value="is_motion_detected",
    ),
)

CAMERA_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key=_KEY_DOORBELL,
        name="Doorbell",
        device_class=DEVICE_CLASS_OCCUPANCY,
        icon="mdi:doorbell-video",
        ufp_required_field="feature_flags.has_chime",
        ufp_value="last_ring",
    ),
    UnifiProtectBinaryEntityDescription(
        key=_KEY_DARK,
        name="Is Dark",
        icon="mdi:brightness-6",
        ufp_required_field=None,
        ufp_value="is_dark",
    ),
    UnifiProtectBinaryEntityDescription(
        key=_KEY_MOTION,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_required_field=None,
        ufp_value="is_motion_detected",
    ),
)

LIGHT_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key=_KEY_DARK,
        name="Is Dark",
        icon="mdi:brightness-6",
        ufp_required_field=None,
        ufp_value="is_dark",
    ),
    UnifiProtectBinaryEntityDescription(
        key=_KEY_MOTION,
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_required_field=None,
        ufp_value="is_pir_motion_detected",
    ),
)


DEVICE_TYPE_TO_DESCRIPTION = {
    ModelType.CAMERA: CAMERA_SENSORS,
    ModelType.SENSOR: SENSE_SENSORS,
    ModelType.LIGHT: LIGHT_SENSORS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Set up binary sensors for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    wanted_types = set()
    for device_type in DEVICE_TYPE_TO_DESCRIPTION:
        wanted_types.add(device_type)

    entities = []
    for device in protect_data.get_by_types(wanted_types):
        entity_descs = itertools.chain.from_iterable(
            descriptions
            for device_match, descriptions in DEVICE_TYPE_TO_DESCRIPTION.items()
            if device.model is not None and device.model in device_match
        )

        for description in entity_descs:
            if description.ufp_required_field:
                required_field = get_nested_attr(device, description.ufp_required_field)
                if not required_field:
                    continue

            entities.append(
                UnifiProtectBinarySensor(
                    protect,
                    protect_data,
                    device,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding binary sensor entity %s for %s",
                description.name,
                device.name,
            )

    async_add_entities(entities)


class UnifiProtectBinarySensor(UnifiProtectEntity, BinarySensorEntity):
    """A Unifi Protect Binary Sensor."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: UnifiProtectData,
        device: ProtectAdoptableDeviceModel,
        description: UnifiProtectBinaryEntityDescription,
    ) -> None:
        """Initialize the Binary Sensor."""
        assert isinstance(device, (Camera, Light, Sensor))
        self.device: Camera | Light | Sensor = device
        self.entity_description: UnifiProtectBinaryEntityDescription = description
        super().__init__(protect, protect_data, device, description)
        self._attr_name = f"{self.device.name} {description.name.title()}"
        self._async_update_device_from_protect()
        self._doorbell_callback: Optional[TaskClass] = None

    @callback
    def _async_get_extra_attrs(self) -> dict[str, Any]:
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

        if not isinstance(self.device, Camera):
            return attrs

        # Camera motion sensors with object detection
        score = 0
        if (
            self.device.is_smart_detected
            and self.device.last_smart_detect_event is not None
            and len(self.device.last_smart_detect_event.smart_detect_types) > 0
        ):
            score = self.device.last_smart_detect_event.score
            detected_object: SmartDetectObjectType | None = (
                self.device.last_smart_detect_event.smart_detect_types[0]
            )
            _LOGGER.debug(
                "OBJECTS: %s on %s",
                self.device.last_smart_detect_event.smart_detect_types,
                self._attr_name,
            )
        else:
            if (
                self.device.is_motion_detected
                and self.device.last_motion_event is not None
            ):
                score = self.device.last_motion_event.score
            detected_object = None

        attrs.update(
            {
                ATTR_LAST_TRIP_TIME: self.device.last_motion,
                ATTR_EVENT_SCORE: score,
                ATTR_EVENT_OBJECT: detected_object,
            }
        )

        return attrs

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()

        if self.entity_description.key == _KEY_DOORBELL:
            last_ring = get_nested_attr(self.device, self.entity_description.ufp_value)
            now = utc_now()

            self._attr_is_on = (now - last_ring) < RING_INTERVAL

            if self._attr_is_on:
                if self._doorbell_callback is not None:
                    self._doorbell_callback.cancel()
                self._doorbell_callback = asyncio.ensure_future(
                    self._async_wait_for_doorbell(last_ring + RING_INTERVAL)
                )
        else:
            self._attr_is_on = get_nested_attr(
                self.device, self.entity_description.ufp_value
            )

        self._extra_state_attributes = self._async_get_extra_attrs()

    @callback
    async def _async_wait_for_doorbell(self, end_time: datetime) -> None:
        _LOGGER.debug("Doorbell callback started")
        while utc_now() < end_time:
            await asyncio.sleep(1)
        _LOGGER.debug("Doorbell callback ended")
        self._async_updated_event()

    @callback
    def _async_updated_event(self) -> None:
        self._async_fire_events()
        super()._async_updated_event()

    @callback
    def _async_fire_events(self) -> None:
        """Fire events on ring or motion.

        CORE: Remove this before merging to core.
        """

        key = self.entity_description.key
        if key == _KEY_DOORBELL:
            self._async_fire_doorbell_event()
        if key == _KEY_MOTION:
            self._async_fire_motion_event()

    @callback
    def _async_fire_doorbell_event(self) -> None:
        """Fire events on ring.

        CORE: Remove this before merging to core.
        """

        assert isinstance(self.device, Camera)
        if self._attr_is_on:
            self.hass.bus.async_fire(
                f"{DOMAIN}_doorbell",
                {
                    "ring": self._attr_is_on,
                    "entity_id": self.entity_id,
                },
            )

    @callback
    def _async_fire_motion_event(self) -> None:
        """Fire events on motion.

        Remove this before merging to core.
        """

        assert isinstance(self.device, (Camera, Light))

        obj: list[str] | None = None
        if isinstance(self.device, Camera):
            is_on = self.device.is_motion_detected
            if (
                self.device.is_smart_detected
                and self.device.last_smart_detect_event is not None
            ):
                obj = [
                    t.value
                    for t in self.device.last_smart_detect_event.smart_detect_types
                ]
        else:
            is_on = self.device.is_pir_motion_detected

        self.hass.bus.async_fire(
            f"{DOMAIN}_motion",
            {
                "entity_id": self.entity_id,
                "smart_detect": obj,
                "motion_on": is_on,
            },
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the extra state attributes."""
        return {**super().extra_state_attributes, **self._extra_state_attributes}
