"""This component provides number entities for Unifi Protect."""
import logging
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import (
    DEVICES_WITH_CAMERA,
    DOMAIN,
    ENTITY_CATEGORY_CONFIG,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

_ENTITY_WDR = "wdr_value"
_ENTITY_MIC_LEVEL = "mic_level"
_ENTITY_ZOOM_POS = "zoom_position"


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_max: int
    ufp_min: int
    ufp_step: int
    ufp_device_type: str
    ufp_required_field: str


@dataclass
class UnifiProtectNumberEntityDescription(
    NumberEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Number entity."""


NUMBER_TYPES: tuple[UnifiProtectNumberEntityDescription, ...] = (
    UnifiProtectNumberEntityDescription(
        key=_ENTITY_WDR,
        name="Wide Dynamic Range",
        icon="mdi:state-machine",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=3,
        ufp_step=1,
        ufp_device_type=DEVICES_WITH_CAMERA,
        ufp_required_field=None,
    ),
    UnifiProtectNumberEntityDescription(
        key=_ENTITY_MIC_LEVEL,
        name="Microphone Level",
        icon="mdi:microphone",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_type=DEVICES_WITH_CAMERA,
        ufp_required_field=None,
    ),
    UnifiProtectNumberEntityDescription(
        key=_ENTITY_ZOOM_POS,
        name="Zoom Position",
        icon="mdi:magnify-plus-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_min=0,
        ufp_max=100,
        ufp_step=1,
        ufp_device_type=DEVICES_WITH_CAMERA,
        ufp_required_field="has_opticalzoom",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    if not protect_data.data:
        return

    entities = []

    for description in NUMBER_TYPES:
        for device_id in protect_data.data:
            if protect_data.data[device_id].get("type") in description.ufp_device_type:
                if description.ufp_required_field and not protect_data.data[
                    device_id
                ].get(description.ufp_required_field):
                    continue
                entities.append(
                    UnifiProtectNumbers(
                        upv_object,
                        protect_data,
                        server_info,
                        device_id,
                        description,
                    )
                )
                _LOGGER.debug(
                    "Adding number entity %s for %s",
                    description.name,
                    protect_data.data[device_id].get("name"),
                )

    if not entities:
        return

    async_add_entities(entities)


class UnifiProtectNumbers(UnifiProtectEntity, NumberEntity):
    """A Unifi Protect Number Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectNumberEntityDescription,
    ):
        """Initialize the Number Entities."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self.entity_description = description
        self._name = f"{self.entity_description.name} {self._device_data['name']}"
        self._icon = self.entity_description.icon
        self._device_type = self.entity_description.ufp_device_type
        self._attr_max_value = self.entity_description.ufp_max
        self._attr_min_value = self.entity_description.ufp_min
        self._attr_step = self.entity_description.ufp_step
        self._attr_entity_category = self.entity_description.entity_category

    @property
    def name(self):
        """Return name of the entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.entity_description.key == _ENTITY_WDR:
            return self._device_data["wdr"]

        if self.entity_description.key == _ENTITY_MIC_LEVEL:
            return self._device_data["mic_volume"]

        return self._device_data["zoom_position"]

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    async def async_set_value(self, value: float) -> None:
        """Set new value."""
        if self.entity_description.key == _ENTITY_WDR:
            _LOGGER.debug(
                "Setting WDR Value to %s for Camera %s",
                value,
                self._device_data["name"],
            )
            await self.upv_object.set_camera_wdr(self._device_id, value)
        if self.entity_description.key == _ENTITY_MIC_LEVEL:
            _LOGGER.debug(
                "Setting Microphone Level to %s for Camera %s",
                value,
                self._device_data["name"],
            )
            await self.upv_object.set_mic_volume(self._device_id, value)
        if self.entity_description.key == _ENTITY_ZOOM_POS:
            _LOGGER.debug(
                "Setting Zoom Position to %s for Camera %s",
                value,
                self._device_data["name"],
            )
            await self.upv_object.set_camera_zoom_position(self._device_id, value)
