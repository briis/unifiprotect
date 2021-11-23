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

_LOGGER = logging.getLogger(__name__)

_KEY_IR = "infrared"
_KEY_REC_MODE = "recording_mode"
_KEY_VIEWER = "viewer"
_KEY_LIGHT_MOTION = "light_motion"
_KEY_DOORBELL_TEXT = "doorbell_text"


DOORBELL_BASE_TEXT = [
    {"id": "LEAVE_PACKAGE_AT_DOOR", "name": "LEAVE PACKAGE AT DOOR"},
    {"id": "DO_NOT_DISTURB", "name": "DO NOT DISTURB"},
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

MOTION_MODE_TO_LIGHT_MODE = [
    {"id": TYPE_LIGHT_RECORD_MOTION, "name": LIGHT_MODE_MOTION},
    {"id": TYPE_RECORD_ALWAYS, "name": LIGHT_MODE_DARK},
    {"id": TYPE_RECORD_OFF, "name": LIGHT_MODE_OFF},
]

RECORDING_MODES = ["Always", "Never", "Detections"]

DEVICE_RECORDING_MODES = [
    {"id": mode.lower(), "name": mode} for mode in RECORDING_MODES
]


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[str]
    ufp_options: list[dict[str, Any]]
    ufp_device_data_key: str
    ufp_set_function: str


@dataclass
class UnifiProtectSelectEntityDescription(
    SelectEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Sensor entity."""


SELECT_TYPES: tuple[UnifiProtectSelectEntityDescription, ...] = (
    UnifiProtectSelectEntityDescription(
        key=_KEY_REC_MODE,
        name="Recording Mode",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_options=DEVICE_RECORDING_MODES,
        ufp_device_data_key="recording_mode",
        ufp_set_function="set_camera_recording",
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_VIEWER,
        name="Viewer",
        icon="mdi:view-dashboard",
        ufp_device_types={DEVICE_TYPE_VIEWPORT},
        ufp_options=None,
        ufp_device_data_key="liveview",
        ufp_set_function="set_viewport_view",
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_LIGHT_MOTION,
        name="Lightning",
        icon="mdi:spotlight",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={DEVICE_TYPE_LIGHT},
        ufp_options=MOTION_MODE_TO_LIGHT_MODE,
        ufp_device_data_key="motion_mode",
        ufp_set_function=None,
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_IR,
        name="Infrared",
        icon="mdi:circle-opacity",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_options=INFRARED_MODES,
        ufp_device_data_key="ir_mode",
        ufp_set_function="set_camera_ir",
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_DOORBELL_TEXT,
        name="Doorbell Text",
        icon="mdi:card-text",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={DEVICE_TYPE_DOORBELL},
        ufp_options=None,
        ufp_device_data_key="doorbell_text",
        ufp_set_function=None,
    ),
)


def _build_doorbell_texts(doorbell_text) -> list[dict[str, str]]:
    """Create a list of available doorbell texts from the defaults and configured."""
    return [
        *DOORBELL_BASE_TEXT,
        *(
            {"id": CUSTOM_MESSAGE, "name": item.strip()}
            for item in (doorbell_text or "").split(",")
            if len(item.strip()) != 0
        ),
    ]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data.upv
    protect_data = entry_data.protect_data
    server_info = entry_data.server_info
    doorbell_texts = _build_doorbell_texts(entry_data.doorbell_text)
    liveviews: list[dict[str, Any]] = await upv_object.get_live_views()

    entities = []
    for description in SELECT_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            options = description.ufp_options
            if description.key == _KEY_DOORBELL_TEXT:
                options = doorbell_texts
            if description.key == _KEY_VIEWER:
                options = liveviews

            entities.append(
                UnifiProtectSelects(
                    upv_object,
                    protect_data,
                    server_info,
                    device.device_id,
                    description,
                    options,
                )
            )
            _LOGGER.debug(
                "Adding select entity %s for %s with options %s",
                description.name,
                device.data.get("name"),
                options,
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
        options: list[dict[str, Any]],
    ):
        """Initialize the unifi protect select entity."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._attr_name = f"{self.entity_description.name} {self._device_data['name']}"
        self._attr_options = [item["name"] for item in options]
        self._data_key = description.ufp_device_data_key
        self._hass_to_unifi_options = {item["name"]: item["id"] for item in options}
        self._unifi_to_hass_options = {item["id"]: item["name"] for item in options}

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        unifi_value = self._device_data[self._data_key]
        if self.entity_description.key == _KEY_DOORBELL_TEXT:
            return unifi_value
        return self._unifi_to_hass_options[unifi_value]

    async def async_select_option(self, option: str) -> None:
        """Change the Select Entity Option."""
        if option not in self.options:
            raise HomeAssistantError(
                f"Cannot set the value to {option}; Allowed values are: {self.options}"
            )

        if self.entity_description.key == _KEY_LIGHT_MOTION:
            lightmode, timing = LIGHT_MODE_TO_SETTINGS[option]
            _LOGGER.debug("Changing Light Mode to %s", option)
            await self.upv_object.light_settings(
                self._device_id, lightmode, enable_at=timing
            )
            return

        unifi_value = self._hass_to_unifi_options[option]
        if self.entity_description.key == _KEY_DOORBELL_TEXT:
            await self.upv_object.set_doorbell_lcd_text(
                self._device_id, unifi_value, option
            )
            _LOGGER.debug("Changed Doorbell LCD Text to: %s", option)
            return

        _LOGGER.debug("%s set to: %s", self.entity_description.key, option)
        coro = getattr(self.upv_object, self.entity_description.ufp_set_function)
        await coro(self._device_id, unifi_value)
