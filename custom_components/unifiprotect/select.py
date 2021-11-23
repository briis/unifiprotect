"""This component provides select entities for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from pyunifiprotect import UpvServer

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
from .data import UnifiProtectData
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

INFRARED_MODES_NAME_TO_ID = {row["name"]: row["id"] for row in INFRARED_MODES}
INFRARED_MODES_ID_TO_NAME = {row["id"]: row["name"] for row in INFRARED_MODES}


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

DEVICE_RECORDING_MODES = {mode.lower(): mode for mode in RECORDING_MODES}


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[str]
    ufp_options: dict[Any, Any]
    ufp_device_data_key: str


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
        ufp_options=DEVICE_RECORDING_MODES,
        ufp_device_data_key="recording_mode",
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_VIEWER,
        name="Viewer",
        icon="mdi:view-dashboard",
        ufp_device_types={DEVICE_TYPE_VIEWPORT},
        ufp_options=None,
        ufp_device_data_key="liveview",
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_LIGHT_MOTION,
        name="Lightning",
        icon="mdi:spotlight",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={DEVICE_TYPE_LIGHT},
        ufp_options=MOTION_MODE_TO_LIGHT_MODE,
        ufp_device_data_key="motion_mode",
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_IR,
        name="Infrared",
        icon="mdi:circle-opacity",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_options=INFRARED_MODES_ID_TO_NAME,
        ufp_device_data_key="ir_mode",
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_DOORBELL_TEXT,
        name="Doorbell Text",
        icon="mdi:card-text",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={DEVICE_TYPE_DOORBELL},
        ufp_options=None,
        ufp_device_data_key="doorbell_text",
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
    doorbell_options = {item["id"]: item["value"] for item in doorbell_texts}

    # Get Current Views
    liveviews = await upv_object.get_live_views()
    liveview_options = {item["id"]: item["name"] for item in liveviews}

    entities = []
    for description in SELECT_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            options = description.ufp_options
            if description.key == _SELECT_ENTITY_DOORBELL_TEXT:
                options = doorbell_options
            if description.key == _SELECT_ENTITY_VIEWER:
                options = liveview_options
            entities.append(
                UnifiProtectSelects(
                    upv_object,
                    protect_data,
                    server_info,
                    device.device_id,
                    description,
                    options,
                    description.ufp_device_data_key,
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
        upv_object: UpvServer,
        protect_data: UnifiProtectData,
        server_info: dict[str, Any],
        device_id: int,
        description: UnifiProtectSelectEntityDescription,
        options: dict[Any, Any],
        data_key: str,
    ):
        """Initialize the Viewport Media Player."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._select_entity = self.entity_description.key
        self._attr_name = f"{self.entity_description.name} {self._device_data['name']}"
        self._attr_options = list(options.values())
        self._data_key = data_key
        self._hass_to_unifi_options = {v: k for k, v in options.items()}
        self._unifi_to_hass_options = options

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        unifi_value = self._device_data[self._data_key]
        return self._unifi_to_hass_options[unifi_value]

    async def async_select_option(self, option: str) -> None:
        """Change the Select Entity Option."""
        if option not in self.options:
            raise HomeAssistantError(
                f"Cannot set the value to {option}. Allowed values are: {self.options}"
            )

        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
            lightmode, timing = LIGHT_MODE_TO_SETTINGS[option]
            _LOGGER.debug("Changing Light Mode to %s", option)
            await self.upv_object.light_settings(
                self._device_id, lightmode, enable_at=timing
            )
            return

        unifi_value = self._hass_to_unifi_options[option]
        if self._select_entity == _SELECT_ENTITY_VIEWER:
            _LOGGER.debug("Viewport View set to: %s", option)
            await self.upv_object.set_viewport_view(self._device_id, unifi_value)
        elif self._select_entity == _SELECT_ENTITY_IR:
            await self.upv_object.set_camera_ir(self._device_id, unifi_value)
        elif self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            await self.upv_object.set_doorbell_lcd_text(
                self._device_id, unifi_value, option
            )
            _LOGGER.debug("Changed Doorbell LCD Text to: %s", option)
        elif self._select_entity == _SELECT_ENTITY_REC_MODE:
            _LOGGER.debug("Changing Recording Mode to %s", option)
            await self.upv_object.set_camera_recording(self._device_id, unifi_value)
