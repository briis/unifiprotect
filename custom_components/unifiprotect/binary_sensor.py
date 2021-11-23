"""This component provides binary sensors for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import itertools
import logging

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

from .const import (
    ATTR_EVENT_LENGTH,
    ATTR_EVENT_OBJECT,
    ATTR_EVENT_SCORE,
    DEVICE_TYPE_DARK,
    DEVICE_TYPE_DOORBELL,
    DEVICE_TYPE_MOTION,
    DEVICE_TYPE_SENSOR,
    DEVICES_WITH_CAMERA,
    DEVICES_WITH_DOORBELL,
    DEVICES_WITH_MOTION,
    DEVICES_WITH_SENSE,
    DOMAIN,
    ENTITY_CATEGORY_DIAGNOSTIC,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_type: str
    ufp_device_key: str


@dataclass
class UnifiProtectBinaryEntityDescription(
    BinarySensorEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Binary Sensor entity."""


SENSE_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key="door",
        name="Door",
        device_class=DEVICE_CLASS_DOOR,
        ufp_device_type=DEVICE_TYPE_SENSOR,
        ufp_device_key="event_open_on",
    ),
    UnifiProtectBinaryEntityDescription(
        key="battery_low",
        name="Battery low",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_type=DEVICE_TYPE_SENSOR,
        ufp_device_key="battery_low",
    ),
)

DOORBELL_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key="doorbell",
        name="Doorbell",
        device_class=DEVICE_CLASS_OCCUPANCY,
        icon="mdi:doorbell-video",
        ufp_device_type=DEVICE_TYPE_DOORBELL,
        ufp_device_key="event_ring_on",
    ),
)

CAMERA_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key="dark",
        name="Is Dark",
        icon="mdi:brightness-6",
        ufp_device_type=DEVICE_TYPE_DARK,
        ufp_device_key="is_dark",
    ),
)

MOTION_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key="motion",
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        ufp_device_type=DEVICE_TYPE_MOTION,
        ufp_device_key="event_on",
    ),
)

DEVICE_TYPE_TO_DESCRIPTION = {
    DEVICES_WITH_DOORBELL: DOORBELL_SENSORS,
    DEVICES_WITH_CAMERA: CAMERA_SENSORS,
    DEVICES_WITH_SENSE: SENSE_SENSORS,
    DEVICES_WITH_MOTION: MOTION_SENSORS,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up binary sensors for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data.upv
    protect_data = entry_data.protect_data
    server_info = entry_data.server_info

    wanted_types = set()
    for device_types in DEVICE_TYPE_TO_DESCRIPTION:
        wanted_types |= set(device_types)

    entities = []
    for device in protect_data.get_by_types(wanted_types):
        device_data = device.data
        device_type = device.type
        entity_descs = itertools.chain.from_iterable(
            descriptions
            for device_match, descriptions in DEVICE_TYPE_TO_DESCRIPTION.items()
            if device_type in device_match
        )

        for description in entity_descs:
            entities.append(
                UnifiProtectBinarySensor(
                    upv_object,
                    protect_data,
                    server_info,
                    device.device_id,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding binary sensor entity %s for %s",
                description.name,
                device_data["name"],
            )

    async_add_entities(entities)


class UnifiProtectBinarySensor(UnifiProtectEntity, BinarySensorEntity):
    """A Unifi Protect Binary Sensor."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectBinaryEntityDescription,
    ):
        """Initialize the Binary Sensor."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._attr_name = f"{description.name.title()} {self._device_data['name']}"
        self._attr_is_on = self._device_data[description.ufp_device_key]

    @callback
    def _async_updated_event(self):
        self._async_fire_events()
        self._attr_is_on = self._device_data[self.entity_description.ufp_device_key]
        super()._async_updated_event()

    @callback
    def _async_fire_events(self):
        """Fire events on ring or motion.

        Remove this before merging to core.
        """
        key = self.entity_description.key
        if key == DEVICE_TYPE_DOORBELL and self._device_data["event_ring_on"]:
            self.hass.bus.async_fire(
                f"{DOMAIN}_doorbell",
                {
                    "ring": self._device_data["event_ring_on"],
                    "entity_id": self.entity_id,
                },
            )
        if key == DEVICE_TYPE_MOTION and self._device_data["event_on"]:
            self.hass.bus.async_fire(
                f"{DOMAIN}_motion",
                {
                    "entity_id": self.entity_id,
                    "smart_detect": self._device_data["event_object"],
                    "motion_on": self._device_data["event_on"],
                },
            )

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        key = self.entity_description.key
        attr = {
            **super().extra_state_attributes,
        }
        if key == DEVICE_TYPE_DARK:
            return attr
        if key == DEVICE_TYPE_DOORBELL:
            attr[ATTR_LAST_TRIP_TIME] = self._device_data["last_ring"]
            return attr

        if self._device_data["type"] == DEVICE_TYPE_SENSOR:
            if key == DEVICE_TYPE_MOTION:
                attr[ATTR_LAST_TRIP_TIME] = self._device_data["last_motion"]
                attr[ATTR_EVENT_LENGTH] = self._device_data["event_length"]
            if key == "door":
                attr[ATTR_LAST_TRIP_TIME] = self._device_data["last_openchange"]
                attr[ATTR_EVENT_LENGTH] = self._device_data["event_length"]
            return attr

        # Camera motion sensors with object detection
        if (
            self._device_data["event_object"] is not None
            and len(self._device_data["event_object"]) > 0
        ):
            detected_object = self._device_data["event_object"][0]
            _LOGGER.debug(
                "OBJECTS: %s on %s", self._device_data["event_object"], self._attr_name
            )
        else:
            detected_object = "None Identified"

        attr.update(
            {
                ATTR_LAST_TRIP_TIME: self._device_data["last_motion"],
                ATTR_EVENT_SCORE: self._device_data["event_score"],
                ATTR_EVENT_LENGTH: self._device_data["event_length"],
                ATTR_EVENT_OBJECT: detected_object,
            }
        )
        return attr
