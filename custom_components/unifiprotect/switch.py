"""This component provides Switches for UniFi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable, Sequence

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENTITY_CATEGORY_CONFIG
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.data import Camera, Light, ModelType, RecordingMode, VideoMode
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel, ProtectDeviceModel

from .const import DEVICES_THAT_ADOPT, DEVICES_WITH_CAMERA, DOMAIN
from .data import ProtectData
from .entity import ProtectEntity
from .models import ProtectEntryData
from .utils import get_nested_attr

_LOGGER = logging.getLogger(__name__)


@dataclass
class ProtectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_types: set[ModelType]
    ufp_required_field: str | None
    ufp_value: str


@dataclass
class ProtectSwitchEntityDescription(SwitchEntityDescription, ProtectRequiredKeysMixin):
    """Describes UniFi Protect Switch entity."""


_KEY_STATUS_LIGHT = "status_light"
_KEY_HDR_MODE = "hdr_mode"
_KEY_HIGH_FPS = "high_fps"
_KEY_PRIVACY_MODE = "privacy_mode"
_KEY_SSH = "ssh"

SWITCH_TYPES: tuple[ProtectSwitchEntityDescription, ...] = (
    ProtectSwitchEntityDescription(
        key=_KEY_STATUS_LIGHT,
        name="Status Light On",
        icon="mdi:led-on",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_led_status",
        ufp_value="led_settings.is_enabled",
    ),
    ProtectSwitchEntityDescription(
        key=_KEY_STATUS_LIGHT,
        name="Status Light On",
        icon="mdi:led-on",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types={ModelType.LIGHT},
        ufp_required_field=None,
        ufp_value="light_device_settings.is_indicator_enabled",
    ),
    ProtectSwitchEntityDescription(
        key=_KEY_HDR_MODE,
        name="HDR Mode",
        icon="mdi:brightness-7",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_hdr",
        ufp_value="hdr_mode",
    ),
    ProtectSwitchEntityDescription(
        key=_KEY_HIGH_FPS,
        name="High FPS",
        icon="mdi:video-high-definition",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_highfps",
        ufp_value="video_mode",
    ),
    ProtectSwitchEntityDescription(
        key=_KEY_PRIVACY_MODE,
        name="Privacy Mode",
        icon="mdi:eye-settings",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_WITH_CAMERA,
        ufp_required_field="feature_flags.has_privacy_mask",
        ufp_value="is_privacy_on",
    ),
    ProtectSwitchEntityDescription(
        key=_KEY_SSH,
        name="SSH Enabled",
        icon="mdi:lock",
        entity_registry_enabled_default=False,
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_types=DEVICES_THAT_ADOPT,
        ufp_required_field=None,
        ufp_value="is_ssh_enabled",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Set up switches for UniFi Protect integration."""
    entry_data: ProtectEntryData = hass.data[DOMAIN][entry.entry_id]
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
                ProtectSwitch(
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


class ProtectSwitch(ProtectEntity, SwitchEntity):
    """A UniFi Protect Switch."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: ProtectData,
        device: ProtectDeviceModel,
        description: ProtectSwitchEntityDescription,
    ):
        """Initialize an UniFi Protect Switch."""
        assert isinstance(device, ProtectAdoptableDeviceModel)
        self.device: ProtectAdoptableDeviceModel = device
        self.entity_description: ProtectSwitchEntityDescription = description
        super().__init__(protect, protect_data, device, description)
        self._attr_name = f"{self.device.name} {self.entity_description.name}"
        self._switch_type = self.entity_description.key

        if not isinstance(self.device, Camera):
            return

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
            return bool(ufp_value == VideoMode.HIGH_FPS)
        return ufp_value is True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""

        if self._switch_type == _KEY_SSH:
            _LOGGER.debug("Turning on SSH")
            await self.device.set_ssh(True)

        if not isinstance(self.device, (Camera, Light)):
            return

        if self._switch_type == _KEY_STATUS_LIGHT:
            _LOGGER.debug("Changing Status Light to On")
            await self.device.set_status_light(True)

        if isinstance(self.device, Light):
            return

        if self._switch_type == _KEY_HDR_MODE:
            _LOGGER.debug("Turning on HDR mode")
            await self.device.set_hdr(True)
            return
        if self._switch_type == _KEY_HIGH_FPS:
            _LOGGER.debug("Turning on High FPS mode")
            await self.device.set_video_mode(VideoMode.HIGH_FPS)
            return
        if self._switch_type == _KEY_PRIVACY_MODE:
            _LOGGER.debug("Turning Privacy Mode on for %s", self.device.name)
            self._previous_mic_level = self.device.mic_volume
            self._previous_record_mode = self.device.recording_settings.mode
            await self.device.set_privacy(True, 0, RecordingMode.NEVER)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""

        if self._switch_type == _KEY_SSH:
            _LOGGER.debug("Turning off SSH")
            await self.device.set_ssh(False)

        if not isinstance(self.device, (Camera, Light)):
            return

        if self._switch_type == _KEY_STATUS_LIGHT:
            _LOGGER.debug("Changing Status Light to Off")
            await self.device.set_status_light(False)

        if not isinstance(self.device, Camera):
            return

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
