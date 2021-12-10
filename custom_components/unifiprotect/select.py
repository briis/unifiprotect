"""This component provides select entities for UniFi Protect."""
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
from pyunifiprotect.data import (
    Camera,
    DoorbellMessageType,
    IRLEDMode,
    Light,
    LightModeEnableType,
    LightModeType,
    Liveview,
    RecordingMode,
    Viewer,
)
from pyunifiprotect.data.devices import LCDMessage

from .const import DOMAIN, TYPE_EMPTY_VALUE
from .data import ProtectData
from .entity import ProtectDeviceEntity, async_all_device_entities
from .models import ProtectRequiredKeysMixin
from .utils import get_nested_attr

_LOGGER = logging.getLogger(__name__)

_KEY_IR = "infrared"
_KEY_REC_MODE = "recording_mode"
_KEY_VIEWER = "viewer"
_KEY_LIGHT_MOTION = "light_motion"
_KEY_DOORBELL_TEXT = "doorbell_text"
_KEY_PAIRED_CAMERA = "paired_camera"

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
class ProtectSelectEntityDescription(ProtectRequiredKeysMixin, SelectEntityDescription):
    """Describes UniFi Protect Sensor entity."""

    ufp_options: list[dict[str, Any]] | None = None
    ufp_enum_type: type[Enum] | None = None
    ufp_set_function: str | None = None


CAMERA_SELECTS: tuple[ProtectSelectEntityDescription, ...] = (
    ProtectSelectEntityDescription(
        key=_KEY_REC_MODE,
        name="Recording Mode",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_options=DEVICE_RECORDING_MODES,
        ufp_enum_type=RecordingMode,
        ufp_value="recording_settings.mode",
        ufp_set_function="set_recording_mode",
    ),
    ProtectSelectEntityDescription(
        key=_KEY_IR,
        name="Infrared",
        icon="mdi:circle-opacity",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="feature_flags.has_led_ir",
        ufp_options=INFRARED_MODES,
        ufp_enum_type=IRLEDMode,
        ufp_value="isp_settings.ir_led_mode",
        ufp_set_function="set_ir_led_model",
    ),
    ProtectSelectEntityDescription(
        key=_KEY_DOORBELL_TEXT,
        name="Doorbell Text",
        icon="mdi:card-text",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="feature_flags.has_lcd_screen",
        ufp_value="lcd_message",
    ),
)

LIGHT_SELECTS: tuple[ProtectSelectEntityDescription, ...] = (
    ProtectSelectEntityDescription(
        key=_KEY_LIGHT_MOTION,
        name="Lighting",
        icon="mdi:spotlight",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_options=MOTION_MODE_TO_LIGHT_MODE,
        ufp_value="light_mode_settings.mode",
    ),
    ProtectSelectEntityDescription(
        key=_KEY_PAIRED_CAMERA,
        name="Paired Camera",
        icon="mdi:cctv",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_value="camera_id",
    ),
)

VIEWPORT_SELECTS: tuple[ProtectSelectEntityDescription, ...] = (
    ProtectSelectEntityDescription(
        key=_KEY_VIEWER,
        name="Viewer",
        icon="mdi:view-dashboard",
        ufp_value="liveview",
        ufp_set_function="set_liveview",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Set up number entities for UniFi Protect integration."""
    data: ProtectData = hass.data[DOMAIN][entry.entry_id]
    entities: list[ProtectDeviceEntity] = async_all_device_entities(
        data,
        ProtectSelects,
        camera_descs=CAMERA_SELECTS,
        light_descs=LIGHT_SELECTS,
        viewport_descs=VIEWPORT_SELECTS,
    )

    async_add_entities(entities)


class ProtectSelects(ProtectDeviceEntity, SelectEntity):
    """A UniFi Protect Select Entity."""

    def __init__(
        self,
        data: ProtectData,
        device: Camera | Light | Viewer,
        description: ProtectSelectEntityDescription,
    ):
        """Initialize the unifi protect select entity."""
        assert description.ufp_value is not None

        self.device: Camera | Light | Viewer = device
        self.entity_description: ProtectSelectEntityDescription = description
        super().__init__(data)
        self._attr_name = f"{self.device.name} {self.entity_description.name}"
        self._data_key = description.ufp_value

        options = description.ufp_options
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
        if self.entity_description.ufp_options is not None:
            return

        if self.entity_description.key == _KEY_VIEWER:
            options = [
                {"id": item.id, "name": item.name}
                for item in self.data.api.bootstrap.liveviews.values()
            ]
        elif self.entity_description.key == _KEY_DOORBELL_TEXT:
            default_message = (
                self.data.api.bootstrap.nvr.doorbell_settings.default_message_text
            )
            messages = self.data.api.bootstrap.nvr.doorbell_settings.all_messages
            built_messages = (
                {"id": item.type.value, "name": item.text} for item in messages
            )

            options = [
                {"id": "", "name": f"Default Message ({default_message})"},
                *built_messages,
            ]
        elif self.entity_description.key == _KEY_PAIRED_CAMERA:
            options = []
            for camera in self.data.api.bootstrap.cameras.values():
                options.append({"id": camera.id, "name": camera.name})

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
                assert isinstance(unifi_value, LCDMessage)
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

        if self.entity_description.key == _KEY_PAIRED_CAMERA:
            camera = self.data.api.bootstrap.cameras.get(unifi_value)
            await self.device.set_paired_camera(camera)
            _LOGGER.debug("Changed Paired Camera to to: %s", option)
            return
        elif self.entity_description.ufp_enum_type is not None:
            unifi_value = self.entity_description.ufp_enum_type(unifi_value)
        elif self.entity_description.key == _KEY_VIEWER:
            unifi_value = self.data.api.bootstrap.liveviews[unifi_value]

        _LOGGER.debug("%s set to: %s", self.entity_description.key, option)
        assert self.entity_description.ufp_set_function
        coro = getattr(self.device, self.entity_description.ufp_set_function)
        await coro(unifi_value)
