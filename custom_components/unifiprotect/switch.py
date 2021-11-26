"""This component provides Switches for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from pyunifiprotect.data import Camera, VideoMode, Light, ModelType
from pyunifiprotect.data.types import RecordingMode

from custom_components.unifiprotect.utils import get_nested_attr

from .const import (
    DEVICES_WITH_CAMERA,
    DEVICES_WITH_STATUS_LIGHT,
    DOMAIN,
    ENTITY_CATEGORY_CONFIG,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[ModelType]
    ufp_required_field: str
    ufp_value: str


@dataclass
class UnifiProtectSwitchEntityDescription(
    SwitchEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Switch entity."""


_KEY_STATUS_LIGHT = "status_light"
_KEY_HDR_MODE = "hdr_mode"
_KEY_HIGH_FPS = "high_fps"
_KEY_PRIVACY_MODE = "privacy_mode"

SWITCH_TYPES: tuple[UnifiProtectSwitchEntityDescription, ...] = (
    UnifiProtectSwitchEntityDescription(
        key=_KEY_STATUS_LIGHT,
        name="Status Light On",
        icon="mdi:led-on",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_led_status",
        ufp_value="led_settings.is_enabled",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_STATUS_LIGHT,
        name="Status Light On",
        icon="mdi:led-on",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={ModelType.LIGHT},
        ufp_required_field=None,
        ufp_value="light_device_settings.is_indicator_enabled",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_HDR_MODE,
        name="HDR Mode",
        icon="mdi:brightness-7",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_hdr",
        ufp_value="hdr_mode",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_HIGH_FPS,
        name="High FPS",
        icon="mdi:video-high-definition",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_highfps",
        ufp_value="video_mode",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_PRIVACY_MODE,
        name="Privacy Mode",
        icon="mdi:eye-settings",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_privacy_mask",
        ufp_value="is_privacy_on",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up switches for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    switches = []
    for description in SWITCH_TYPES:
        for device in protect_data.get_by_types(description.ufp_device_types):
            if description.ufp_required_field:
                required_field = get_nested_attr(device, description.ufp_required_field)
                if not required_field:
                    continue

            switches.append(
                UnifiProtectSwitch(
                    protect,
                    protect_data,
                    device,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding switch entity %s for %s",
                description.name,
                device.name,
            )

    async_add_entities(switches)


class UnifiProtectSwitch(UnifiProtectEntity, SwitchEntity):
    """A Unifi Protect Switch."""

    def __init__(
        self,
        protect,
        protect_data,
        device,
        description: UnifiProtectSwitchEntityDescription,
    ):
        """Initialize an Unifi Protect Switch."""
        super().__init__(protect, protect_data, device, description)
        self.device: Camera | Light = device
        self._attr_name = f"{self.entity_description.name} {self.device.name}"
        self._switch_type = self.entity_description.key
        if isinstance(self.device, Camera):
            if self.device.is_privacy_on:
                self._previous_mic_level = 100
                self._previous_record_mode = RecordingMode.ALWAYS
            else:
                self._previous_mic_level = self.device.mic_volume
                self._previous_record_mode = self.device.recording_settings.mode

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        ufp_value = get_nested_attr(self.device, self.entity_description.ufp_value)
        if self._switch_type == _KEY_HIGH_FPS:
            return ufp_value == VideoMode.HIGH_FPS
        return ufp_value is True

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""

        if isinstance(self.device, Camera):
            if self._switch_type == _KEY_HDR_MODE:
                _LOGGER.debug("Turning on HDR mode")
                await self.device.set_hdr(True)
            elif self._switch_type == _KEY_HIGH_FPS:
                _LOGGER.debug("Turning on High FPS mode")
                await self.device.set_video_mode(VideoMode.HIGH_FPS)
            elif self._switch_type == _KEY_PRIVACY_MODE:
                _LOGGER.debug("Turning Privacy Mode on for %s", self.device.name)
                self._previous_mic_level = self.device.mic_volume
                self._previous_record_mode = self.device.recording_settings.mode
                await self.device.set_privacy(True, 0, RecordingMode.NEVER)

        if self._switch_type == _KEY_STATUS_LIGHT:
            _LOGGER.debug("Changing Status Light to On")
            await self.device.set_status_light(True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""

        if isinstance(self.device, Camera):
            if self._switch_type == _KEY_HDR_MODE:
                _LOGGER.debug("Turning off HDR mode")
                await self.device.set_hdr(False)
            elif self._switch_type == _KEY_HIGH_FPS:
                _LOGGER.debug("Turning off High FPS mode")
                await self.device.set_video_mode(VideoMode.DEFAULT)
            elif self._switch_type == _KEY_PRIVACY_MODE:
                _LOGGER.debug("Turning Privacy Mode off for %s", self.device.name)
                await self.device.set_privacy(
                    False, self._previous_mic_level, self._previous_record_mode
                )

        if self._switch_type == _KEY_STATUS_LIGHT:
            _LOGGER.debug("Changing Status Light to Off")
            await self.device.set_status_light(False)
