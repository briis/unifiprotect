"""This component provides select entities for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Any, Callable, Sequence

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_CONFIG
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import Entity
from pyunifiprotect import ProtectApiClient
from pyunifiprotect.data import (
    DoorbellMessageType,
    IRLEDMode,
    LightModeEnableType,
    LightModeType,
    ModelType,
    RecordingMode,
)
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel
from pyunifiprotect.data.devices import Camera, Light, Viewer
from pyunifiprotect.data.nvr import DoorbellMessage, Liveview

from .const import DEVICES_WITH_CAMERA, DOMAIN, TYPE_EMPTY_VALUE
from .data import UnifiProtectData
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData
from .utils import get_nested_attr

_LOGGER = logging.getLogger(__name__)

_KEY_IR = "infrared"
_KEY_REC_MODE = "recording_mode"
_KEY_VIEWER = "viewer"
_KEY_LIGHT_MOTION = "light_motion"
_KEY_DOORBELL_TEXT = "doorbell_text"

INFRARED_MODES = [
    {"id": IRLEDMode.AUTO.value, "name": "Auto"},
    {"id": IRLEDMode.ON.value, "name": "Always Enable"},
    {"id": IRLEDMode.AUTO_NO_LED.value, "name": "Auto (Filter Only, no LED's)"},
    {"id": IRLEDMode.OFF.value, "name": "Always Disable"},
]


LIGHT_MODE_MOTION = "On Motion - Always"
LIGHT_MODE_MOTION_DARK = "On Motion - When Dark"
LIGHT_MODE_DARK = "When Dark"
LIGHT_MODE_OFF = "Manual"
LIGHT_MODES = [LIGHT_MODE_MOTION, LIGHT_MODE_DARK, LIGHT_MODE_OFF]

LIGHT_MODE_TO_SETTINGS = {
    LIGHT_MODE_MOTION: (LightModeType.MOTION.value, LightModeEnableType.ALWAYS.value),
    LIGHT_MODE_MOTION_DARK: (
        LightModeType.MOTION.value,
        LightModeEnableType.DARK.value,
    ),
    LIGHT_MODE_DARK: (LightModeType.WHEN_DARK.value, LightModeEnableType.DARK.value),
    LIGHT_MODE_OFF: (LightModeType.MANUAL.value, None),
}

MOTION_MODE_TO_LIGHT_MODE = [
    {"id": LightModeType.MOTION.value, "name": LIGHT_MODE_MOTION},
    {"id": f"{LightModeType.MOTION.value}Dark", "name": LIGHT_MODE_MOTION_DARK},
    {"id": LightModeType.WHEN_DARK.value, "name": LIGHT_MODE_DARK},
    {"id": LightModeType.MANUAL.value, "name": LIGHT_MODE_OFF},
]

DEVICE_RECORDING_MODES = [
    {"id": mode.value, "name": mode.value.title()} for mode in list(RecordingMode)
]


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[ModelType]
    ufp_required_field: str | None
    ufp_options: list[dict[str, Any]] | None
    ufp_enum_type: type[Enum] | None
    ufp_value: str
    ufp_set_function: str | None


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
        ufp_required_field=None,
        ufp_options=DEVICE_RECORDING_MODES,
        ufp_enum_type=RecordingMode,
        ufp_value="recording_settings.mode",
        ufp_set_function="set_recording_mode",
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_VIEWER,
        name="Viewer",
        icon="mdi:view-dashboard",
        ufp_device_types={ModelType.VIEWPORT},
        ufp_required_field=None,
        ufp_options=None,
        ufp_enum_type=None,
        ufp_value="liveview",
        ufp_set_function="set_liveview",
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_LIGHT_MOTION,
        name="Lighting",
        icon="mdi:spotlight",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field=None,
        ufp_device_types={ModelType.LIGHT},
        ufp_options=MOTION_MODE_TO_LIGHT_MODE,
        ufp_enum_type=None,
        ufp_value="light_mode_settings.mode",
        ufp_set_function=None,
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_IR,
        name="Infrared",
        icon="mdi:circle-opacity",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="feature_flags.has_led_ir",
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_options=INFRARED_MODES,
        ufp_enum_type=IRLEDMode,
        ufp_value="isp_settings.ir_led_mode",
        ufp_set_function="set_ir_led_model",
    ),
    UnifiProtectSelectEntityDescription(
        key=_KEY_DOORBELL_TEXT,
        name="Doorbell Text",
        icon="mdi:card-text",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="feature_flags.has_lcd_screen",
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_options=None,
        ufp_enum_type=None,
        ufp_value="lcd_message",
        ufp_set_function=None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    entities = []
    for description in SELECT_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            if description.ufp_required_field:
                required_field = get_nested_attr(device, description.ufp_required_field)
                if not required_field:
                    continue

            entities.append(
                UnifiProtectSelects(
                    protect,
                    protect_data,
                    device,
                    description,
                    description.ufp_options,
                )
            )
            _LOGGER.debug(
                "Adding select entity %s for %s with options %s",
                description.name,
                device.name,
                description.ufp_options,
            )

    if not entities:
        return

    async_add_entities(entities)


class UnifiProtectSelects(UnifiProtectEntity, SelectEntity):
    """A Unifi Protect Select Entity."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: UnifiProtectData,
        device: ProtectAdoptableDeviceModel,
        description: UnifiProtectSelectEntityDescription,
        options: list[dict[str, Any]] | None,
    ):
        """Initialize the unifi protect select entity."""
        assert isinstance(device, (Camera, Viewer, Light))
        self.device: Camera | Viewer | Light = device
        self.entity_description: UnifiProtectSelectEntityDescription = description
        super().__init__(protect, protect_data, device, description)
        self._attr_name = f"{self.device.name} {self.entity_description.name}"
        self._data_key = description.ufp_value

        if options is not None:
            self._attr_options = [item["name"] for item in options]
            self._hass_to_unifi_options: dict[str, Any] = {
                item["name"]: item["id"] for item in options
            }
            self._unifi_to_hass_options: dict[Any, str] = {
                item["id"]: item["name"] for item in options
            }
        self._async_set_dynamic_options()

    @callback
    def _async_set_dynamic_options(self) -> None:
        """These options do not actually update dynamically.

        This is due to possible downstream platforms dependencies on these options.
        """
        if self.entity_description.key not in (_KEY_VIEWER, _KEY_DOORBELL_TEXT):
            return

        if self.entity_description.key == _KEY_VIEWER:
            options = [
                {"id": item.id, "name": item.name}
                for item in self.protect.bootstrap.liveviews.values()
            ]
        elif self.entity_description.key == _KEY_DOORBELL_TEXT:
            default_message = (
                self.protect.bootstrap.nvr.doorbell_settings.default_message_text
            )
            messages = self.protect.bootstrap.nvr.doorbell_settings.all_messages
            built_messages = (
                {"id": item.type.value, "name": item.text} for item in messages
            )

            options = [
                {"id": "", "name": f"Default Message ({default_message})"},
                *built_messages,
            ]

        self._attr_options = [item["name"] for item in options]
        self._hass_to_unifi_options = {item["name"]: item["id"] for item in options}
        self._unifi_to_hass_options = {item["id"]: item["name"] for item in options}

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        unifi_value = get_nested_attr(self.device, self._data_key)

        if isinstance(unifi_value, Enum):
            unifi_value = unifi_value.value
        elif isinstance(unifi_value, Liveview):
            unifi_value = unifi_value.id
        elif self.entity_description.key == _KEY_LIGHT_MOTION:
            assert isinstance(self.device, Light)

            # a bit of extra to allow On Motion Always/Dark
            if (
                self.device.light_mode_settings.mode == LightModeType.MOTION
                and self.device.light_mode_settings.enable_at
                == LightModeEnableType.DARK
            ):
                unifi_value = f"{LightModeType.MOTION.value}Dark"
        elif self.entity_description.key == _KEY_DOORBELL_TEXT:
            if unifi_value is None:
                unifi_value = TYPE_EMPTY_VALUE
            else:
                assert isinstance(unifi_value, DoorbellMessage)
                return unifi_value.text
        return self._unifi_to_hass_options[unifi_value]

    async def async_select_option(self, option: str) -> None:
        """Change the Select Entity Option."""
        if option not in self.options:
            raise HomeAssistantError(
                f"Cannot set the value to {option}; Allowed values are: {self.options}"
            )

        if isinstance(self.device, Light):
            if self.entity_description.key == _KEY_LIGHT_MOTION:
                lightmode, timing = LIGHT_MODE_TO_SETTINGS[option]
                _LOGGER.debug("Changing Light Mode to %s", option)
                await self.device.set_light_settings(
                    LightModeType(lightmode),
                    enable_at=None if timing is None else LightModeEnableType(timing),
                )
                return

        unifi_value = self._hass_to_unifi_options[option]
        if isinstance(self.device, Camera):
            if self.entity_description.key == _KEY_DOORBELL_TEXT:
                if unifi_value.startswith(DoorbellMessageType.CUSTOM_MESSAGE.value):
                    await self.device.set_lcd_text(
                        DoorbellMessageType.CUSTOM_MESSAGE, text=option
                    )
                elif unifi_value == TYPE_EMPTY_VALUE:
                    await self.device.set_lcd_text(None)
                else:
                    await self.device.set_lcd_text(DoorbellMessageType(unifi_value))

                _LOGGER.debug("Changed Doorbell LCD Text to: %s", option)
                return

        if self.entity_description.ufp_enum_type is not None:
            unifi_value = self.entity_description.ufp_enum_type(unifi_value)
        elif self.entity_description.key == _KEY_VIEWER:
            unifi_value = self.protect.bootstrap.liveviews[unifi_value]

        _LOGGER.debug("%s set to: %s", self.entity_description.key, option)
        assert self.entity_description.ufp_set_function
        coro = getattr(self.device, self.entity_description.ufp_set_function)
        await coro(unifi_value)
