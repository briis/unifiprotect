"""This component provides binary sensors for Unifi Protect."""
import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_DOOR,
    DEVICE_CLASS_MOTION,
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_LAST_TRIP_TIME,
)
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import (
    ATTR_EVENT_LENGTH,
    ATTR_EVENT_OBJECT,
    ATTR_EVENT_SCORE,
    DEVICE_TYPE_DARK,
    DEVICE_TYPE_DOORBELL,
    DEVICE_TYPE_MOTION,
    DEVICE_TYPE_SENSOR,
    DEVICES_WITH_CAMERA,
    ENTITY_CATEGORY_DIAGNOSTIC,
    DOMAIN,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

PROTECT_TO_HASS_DEVICE_CLASS = {
    DEVICE_TYPE_DOORBELL: DEVICE_CLASS_OCCUPANCY,
    DEVICE_TYPE_MOTION: DEVICE_CLASS_MOTION,
    DEVICE_TYPE_DARK: None,
}


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_type: str


@dataclass
class UnifiProtectBinaryEntityDescription(
    BinarySensorEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Binary Sensor entity."""


SENSE_SENSORS: tuple[UnifiProtectBinaryEntityDescription, ...] = (
    UnifiProtectBinaryEntityDescription(
        key="motion",
        name="Motion",
        device_class=DEVICE_CLASS_MOTION,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_type=DEVICE_TYPE_SENSOR,
    ),
    UnifiProtectBinaryEntityDescription(
        key="door",
        name="Door",
        device_class=DEVICE_CLASS_DOOR,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_type=DEVICE_TYPE_SENSOR,
    ),
    UnifiProtectBinaryEntityDescription(
        key="battery_low",
        name="Battery low",
        device_class=DEVICE_CLASS_BATTERY,
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        ufp_device_type=DEVICE_TYPE_SENSOR,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up binary sensors for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    if not protect_data.data:
        return

    entities = []
    for device_id in protect_data.data:
        device_data = protect_data.data[device_id]
        if device_data["type"] == DEVICE_TYPE_DOORBELL:

            entities.append(
                UnifiProtectBinarySensor(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    UnifiProtectBinaryEntityDescription(
                        key=DEVICE_TYPE_DOORBELL,
                        name=DEVICE_TYPE_DOORBELL,
                        device_class=DEVICE_CLASS_OCCUPANCY,
                        icon="mdi:doorbell-video",
                        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
                        ufp_device_type=DEVICE_TYPE_DOORBELL,
                    ),
                )
            )
            _LOGGER.debug(
                "Adding Doorbel Binary Sensor entity for %s",
                device_data["name"],
            )

        if device_data["type"] in DEVICES_WITH_CAMERA:
            entities.append(
                UnifiProtectBinarySensor(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    UnifiProtectBinaryEntityDescription(
                        key=DEVICE_TYPE_MOTION,
                        name=DEVICE_TYPE_MOTION,
                        device_class=DEVICE_CLASS_MOTION,
                        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
                        ufp_device_type=DEVICE_TYPE_MOTION,
                    ),
                )
            )
            _LOGGER.debug(
                "Adding Motion Binary Sensor entity for %s",
                device_data["name"],
            )

            entities.append(
                UnifiProtectBinarySensor(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    UnifiProtectBinaryEntityDescription(
                        key=DEVICE_TYPE_DARK,
                        name=DEVICE_TYPE_DARK,
                        icon="mdi:brightness-6",
                        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
                        ufp_device_type=DEVICE_TYPE_DARK,
                    ),
                )
            )
            _LOGGER.debug(
                "Adding Is Dark Binary Sensor entity for %s",
                device_data["name"],
            )

        if device_data["type"] == DEVICE_TYPE_SENSOR:
            for description in SENSE_SENSORS:
                entities.append(
                    UnifiProtectBinarySensor(
                        upv_object,
                        protect_data,
                        server_info,
                        device_id,
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
        self.entity_description = description
        self._name = (
            f"{self.entity_description.name.capitalize()} {self._device_data['name']}"
        )
        self._sensor_type = self.entity_description.ufp_device_type

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        if self._sensor_type == DEVICE_TYPE_SENSOR:
            if self.entity_description.device_class == DEVICE_CLASS_DOOR:
                return self._device_data["event_open_on"]
            if self.entity_description.device_class == DEVICE_CLASS_BATTERY:
                return self._device_data["battery_low"]
            return self._device_data["event_on"]

        if self._sensor_type == DEVICE_TYPE_DARK:
            return self._device_data["is_dark"]

        if self._sensor_type != DEVICE_TYPE_DOORBELL:
            if self._device_data["event_on"]:
                self.hass.bus.fire(
                    f"{DOMAIN}_motion",
                    {
                        "entity_id": f"camera.{slugify(self._device_data['name'])}",
                        "smart_detect": self._device_data["event_object"],
                        "motion_on": self._device_data["event_on"],
                    },
                )
            return self._device_data["event_on"]

        if self._device_data["event_ring_on"]:
            self.hass.bus.fire(
                f"{DOMAIN}_doorbell",
                {
                    "ring": self._device_data["event_ring_on"],
                    "entity_id": f"binary_sensor.{slugify(self._name)}",
                },
            )
        return self._device_data["event_ring_on"]

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        if self._sensor_type == DEVICE_TYPE_DOORBELL:
            return {
                **super().extra_state_attributes,
                ATTR_LAST_TRIP_TIME: self._device_data["last_ring"],
            }
        if self._device_data["type"] == DEVICE_TYPE_SENSOR:
            attr = {
                **super().extra_state_attributes,
            }
            if self.entity_description.device_class == DEVICE_CLASS_MOTION:
                attr[ATTR_LAST_TRIP_TIME] = self._device_data["last_motion"]
                attr[ATTR_EVENT_LENGTH] = self._device_data["event_length"]
            if self.entity_description.device_class == DEVICE_CLASS_DOOR:
                attr[ATTR_LAST_TRIP_TIME] = self._device_data["last_openchange"]
                attr[ATTR_EVENT_LENGTH] = self._device_data["event_length"]
            return attr

        if self._sensor_type == DEVICE_TYPE_DARK:
            return {**super().extra_state_attributes}

        if (
            self._device_data["event_object"] is not None
            and len(self._device_data["event_object"]) > 0
        ):
            detected_object = self._device_data["event_object"][0]
            _LOGGER.debug(
                "OBJECTS: %s on %s", self._device_data["event_object"], self._name
            )
        else:
            detected_object = "None Identified"
        return {
            **super().extra_state_attributes,
            ATTR_LAST_TRIP_TIME: self._device_data["last_motion"],
            ATTR_EVENT_SCORE: self._device_data["event_score"],
            ATTR_EVENT_LENGTH: self._device_data["event_length"],
            ATTR_EVENT_OBJECT: detected_object,
        }
