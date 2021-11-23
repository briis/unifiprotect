"""This component provides select entities for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CUSTOM_MESSAGE,
    DEVICE_TYPE_DOORBELL,
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_VIEWPORT,
    DEVICES_WITH_CAMERA,
    DOMAIN,
    ENTITY_CATEGORY_CONFIG,
    TYPE_INFRARED_AUTO,
    TYPE_INFRARED_AUTOFILTER,
    TYPE_INFRARED_OFF,
    TYPE_INFRARED_ON,
    TYPE_LIGHT_RECORD_MOTION,
    TYPE_RECORD_ALWAYS,
    TYPE_RECORD_OFF,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

ATTR_VIEWS = "views"

_LOGGER = logging.getLogger(__name__)

_SELECT_ENTITY_IR = "infrared"
_SELECT_ENTITY_REC_MODE = "recording_mode"
_SELECT_ENTITY_VIEWER = "viewer"
_SELECT_ENTITY_LIGHT_MOTION = "light_motion"
_SELECT_ENTITY_DOORBELL_TEXT = "doorbell_text"


DOORBELL_BASE_TEXT = [
    {"id": "LEAVE_PACKAGE_AT_DOOR", "value": "LEAVE PACKAGE AT DOOR"},
    {"id": "DO_NOT_DISTURB", "value": "DO NOT DISTURB"},
]

INFRARED_MODES = [
    {"id": TYPE_INFRARED_AUTO, "name": "Auto"},
    {"id": TYPE_INFRARED_ON, "name": "Always Enable"},
    {"id": TYPE_INFRARED_AUTOFILTER, "name": "Auto (Filter Only, no LED's)"},
    {"id": TYPE_INFRARED_OFF, "name": "Always Disable"},
]


LIGHT_MODE_MOTION = "On Motion"
LIGHT_MODE_DARK = "When Dark"
LIGHT_MODE_OFF = "Manual"
LIGHT_MODES = [LIGHT_MODE_MOTION, LIGHT_MODE_DARK, LIGHT_MODE_OFF]

LIGHT_MODE_TO_SETTINGS = {
    LIGHT_MODE_MOTION: (TYPE_LIGHT_RECORD_MOTION, "fulltime"),
    LIGHT_MODE_DARK: (TYPE_RECORD_ALWAYS, "dark"),
    LIGHT_MODE_OFF: (TYPE_RECORD_OFF, None),
}

MOTION_MODE_TO_LIGHT_MODE = {
    TYPE_LIGHT_RECORD_MOTION: LIGHT_MODE_MOTION,
    TYPE_RECORD_ALWAYS: LIGHT_MODE_DARK,
    TYPE_RECORD_OFF: LIGHT_MODE_OFF,
}

RECORDING_MODES = ["Always", "Never", "Detections"]


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[str]


@dataclass
class UnifiProtectSelectEntityDescription(
    SelectEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Sensor entity."""


SELECT_TYPES: tuple[UnifiProtectSelectEntityDescription, ...] = (
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_REC_MODE,
        name="Recording Mode",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_VIEWER,
        name="Viewer",
        icon="mdi:view-dashboard",
        ufp_device_types={DEVICE_TYPE_VIEWPORT},
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_LIGHT_MOTION,
        name="Lightning",
        icon="mdi:spotlight",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={DEVICE_TYPE_LIGHT},
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_IR,
        name="Infrared",
        icon="mdi:circle-opacity",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_DOORBELL_TEXT,
        name="Doorbell Text",
        icon="mdi:card-text",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={DEVICE_TYPE_DOORBELL},
    ),
)


def _build_doorbell_texts(doorbell_text):
    """Create a list of available doorbell texts from the defaults and configured."""
    texts = [{"id": item["id"], "value": item["value"]} for item in DOORBELL_BASE_TEXT]
    if doorbell_text is not None:
        _local_text = doorbell_text.split(",")
        for item in _local_text:
            if len(item.strip()) == 0:
                continue
            texts.append({"id": CUSTOM_MESSAGE, "value": item.strip()})
    return texts


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data.upv
    protect_data = entry_data.protect_data
    server_info = entry_data.server_info
    doorbell_text = entry_data.doorbell_text
    doorbell_texts = _build_doorbell_texts(doorbell_text)

    # Get Current Views
    liveviews = await upv_object.get_live_views()

    entities = []
    for description in SELECT_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            entities.append(
                UnifiProtectSelects(
                    upv_object,
                    protect_data,
                    server_info,
                    device.id,
                    description,
                    liveviews,
                    doorbell_texts,
                )
            )
            _LOGGER.debug(
                "Adding select entity %s for %s",
                description.name,
                device.data.get("name"),
            )

    if not entities:
        return

    async_add_entities(entities)


class UnifiProtectSelects(UnifiProtectEntity, SelectEntity):
    """A Unifi Protect Select Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectSelectEntityDescription,
        liveviews,
        doorbell_texts,
    ):
        """Initialize the Viewport Media Player."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._select_entity = self.entity_description.key
        self._attr_name = f"{self.entity_description.name} {self._device_data['name']}"
        self._liveviews = liveviews
        self._doorbell_texts = doorbell_texts

        if self._select_entity == _SELECT_ENTITY_VIEWER:
            self._attr_options = [item["name"] for item in self._liveviews]
        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
            self._attr_options = LIGHT_MODES
        if self._select_entity == _SELECT_ENTITY_IR:
            self._attr_options = [item["name"] for item in INFRARED_MODES]
        if self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            self._attr_options = [item["value"] for item in self._doorbell_texts]
        if self._select_entity == _SELECT_ENTITY_REC_MODE:
            self._attr_options = RECORDING_MODES

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        if self._select_entity == _SELECT_ENTITY_VIEWER:
            return self._get_view_name_from_id(self._device_data["liveview"])

        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
            return MOTION_MODE_TO_LIGHT_MODE[self._device_data["motion_mode"]]

        if self._select_entity == _SELECT_ENTITY_IR:
            return self._get_infrared_name_from_id()

        if self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            return self._device_data["doorbell_text"]

        return self._device_data["recording_mode"].capitalize()

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attr = {
            **super().extra_state_attributes,
        }
        if self._device_type == DEVICE_TYPE_VIEWPORT:
            attr[ATTR_VIEWS] = self._liveviews

        return attr

    def _get_view_name_from_id(self, view_id):
        """Returns the Liveview Name from the ID"""
        for item in self._liveviews:
            if view_id == item["id"]:
                return item["name"]
        return None

    def _get_view_id_from_name(self, view_name):
        """Returns the Liveview ID from the Name"""
        for item in self._liveviews:
            if view_name == item["name"]:
                return item["id"]
        return None

    def _get_infrared_name_from_id(self):
        """Returns Select Option from Infrared setting"""
        for item in INFRARED_MODES:
            if self._device_data["ir_mode"] == item["id"]:
                return item["name"]
        return None

    def _get_infrared_id_from_name(self, option):
        """Returns Infrared setting from Select Option"""
        for item in INFRARED_MODES:
            if option == item["name"]:
                return item["id"]
        return None

    def _get_doorbell_text_type_from_name(self, option):
        """Returns the Doorbell Text Type from the Option Text"""
        for item in self._doorbell_texts:
            if option == item["value"]:
                return item["id"]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the Select Entity Option."""
        if option not in self.options:
            raise HomeAssistantError(
                f"Cannot set the value to {option}. Allowed values are: {self.options}"
            )

        if self._select_entity == _SELECT_ENTITY_VIEWER:
            _LOGGER.debug("Viewport View set to: %s", option)
            view_id = self._get_view_id_from_name(option)
            await self.upv_object.set_viewport_view(self._device_id, view_id)

        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
            lightmode, timing = LIGHT_MODE_TO_SETTINGS[option]
            _LOGGER.debug("Changing Light Mode to %s", option)
            await self.upv_object.light_settings(
                self._device_id, lightmode, enable_at=timing
            )

        if self._select_entity == _SELECT_ENTITY_IR:
            infrared_id = self._get_infrared_id_from_name(option)
            await self.upv_object.set_camera_ir(self._device_id, infrared_id)

        if self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            text_type = self._get_doorbell_text_type_from_name(option)
            await self.upv_object.set_doorbell_lcd_text(
                self._device_id, text_type, option
            )
            _LOGGER.debug("Changed Doorbell LCD Text to: %s", option)

        if self._select_entity == _SELECT_ENTITY_REC_MODE:
            _LOGGER.debug("Changing Recording Mode to %s", option)
            await self.upv_object.set_camera_recording(self._device_id, option.lower())
