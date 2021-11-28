"""This component provides Switches for Unifi Protect."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DEVICES_WITH_CAMERA,
    DOMAIN,
    ENTITY_CATEGORY_CONFIG,
    TYPE_HIGH_FPS_ON,
    TYPE_RECORD_NEVER,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

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
        ufp_required_field="has_ledstatus",
        ufp_value="status_light",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_HDR_MODE,
        name="HDR Mode",
        icon="mdi:brightness-7",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="has_hdr",
        ufp_value="hdr_mode",
    ),
    # UnifiProtectSwitchEntityDescription(
    #     key=_KEY_HIGH_FPS,
    #     name="High FPS",
    #     icon="mdi:video-high-definition",
    #     entity_category=ENTITY_CATEGORY_CONFIG,
    #     ufp_required_field="has_highfps",
    #     ufp_value="video_mode",
    # ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_PRIVACY_MODE,
        name="Privacy Mode",
        icon="mdi:eye-settings",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="privacy_on",
        ufp_value="privacy_on",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up switches for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data.upv
    protect_data = entry_data.protect_data
    server_info = entry_data.server_info

    switches = []
    for description in SWITCH_TYPES:
        for device in protect_data.get_by_types(DEVICES_WITH_CAMERA):
            device_data = device.data
            if description.ufp_required_field and not isinstance(
                device_data.get(description.ufp_required_field), bool
            ):
                continue

            switches.append(
                UnifiProtectSwitch(
                    upv_object,
                    protect_data,
                    server_info,
                    device.device_id,
                    description,
                )
            )
            _LOGGER.debug(
                "Adding switch entity %s for %s",
                description.name,
                device_data.get("name"),
            )

    async_add_entities(switches)


class UnifiProtectSwitch(UnifiProtectEntity, SwitchEntity):
    """A Unifi Protect Switch."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectSwitchEntityDescription,
    ):
        """Initialize an Unifi Protect Switch."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._attr_name = f"{self.entity_description.name} {self._device_data['name']}"
        self._switch_type = self.entity_description.key

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        ufp_value = self._device_data[self.entity_description.ufp_value]
        if self._switch_type == _KEY_HIGH_FPS:
            return ufp_value == TYPE_HIGH_FPS_ON
        return ufp_value is True

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._switch_type == _KEY_HDR_MODE:
            _LOGGER.debug("Turning on HDR mode")
            await self.upv_object.set_camera_hdr_mode(self._device_id, True)
        elif self._switch_type == _KEY_HIGH_FPS:
            _LOGGER.debug("Turning on High FPS mode")
            await self.upv_object.set_camera_video_mode_highfps(self._device_id, True)
        elif self._switch_type == _KEY_PRIVACY_MODE:
            _LOGGER.debug("Turning Privacy Mode on for %s", self._device_data["name"])
            self._device_data["save_mic_level"] = self._device_data["mic_volume"]
            self._device_data["save_rec_mode"] = self._device_data["recording_mode"]
            await self.upv_object.set_privacy_mode(
                self._device_id, True, 0, TYPE_RECORD_NEVER
            )
        else:
            _LOGGER.debug("Changing Status Light to On")
            await self.upv_object.set_device_status_light(
                self._device_id, True, self._device_type
            )
        await self.protect_data.async_refresh(force_camera_update=True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if self._switch_type == _KEY_STATUS_LIGHT:
            _LOGGER.debug("Changing Status Light to Off")
            await self.upv_object.set_device_status_light(
                self._device_id, False, self._device_type
            )
        elif self._switch_type == _KEY_HDR_MODE:
            _LOGGER.debug("Turning off HDR mode")
            await self.upv_object.set_camera_hdr_mode(self._device_id, False)
        elif self._switch_type == _KEY_PRIVACY_MODE:
            _LOGGER.debug("Turning Privacy Mode off for %s", self._device_data["name"])
            await self.upv_object.set_privacy_mode(
                self._device_id,
                False,
                self._device_data["save_mic_level"],
                self._device_data["save_rec_mode"],
            )
        else:
            _LOGGER.debug("Turning off High FPS mode")
            await self.upv_object.set_camera_video_mode_highfps(self._device_id, False)

        await self.protect_data.async_refresh(force_camera_update=True)
