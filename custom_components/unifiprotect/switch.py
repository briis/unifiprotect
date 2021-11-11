"""This component provides Switches for Unifi Protect."""
import logging
from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import (
    DOMAIN,
    ENTITY_CATEGORY_CONFIG,
    TYPE_HIGH_FPS_ON,
    TYPE_RECORD_NEVER,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_required_field: str


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
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_HDR_MODE,
        name="HDR Mode",
        icon="mdi:brightness-7",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="has_hdr",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_HIGH_FPS,
        name="High FPS",
        icon="mdi:video-high-definition",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="has_highfps",
    ),
    UnifiProtectSwitchEntityDescription(
        key=_KEY_PRIVACY_MODE,
        name="Privacy Mode",
        icon="mdi:eye-settings",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_required_field="privacy_on",
    ),
)

PRIVACY_OFF = [[0, 0], [0, 0], [0, 0], [0, 0]]
PRIVACY_ON = [[0, 0], [1, 0], [1, 1], [0, 1]]
ZONE_NAME = "hass zone"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up switches for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]

    if not protect_data.data:
        return

    switches = []
    for description in SWITCH_TYPES:
        for device_id in protect_data.data:
            if description.ufp_required_field and not isinstance(
                protect_data.data[device_id].get(description.ufp_required_field), bool
            ):
                continue

            if protect_data.data[device_id].get(description.ufp_required_field):
                switches.append(
                    UnifiProtectSwitch(
                        upv_object,
                        protect_data,
                        server_info,
                        device_id,
                        description,
                    )
                )
                _LOGGER.debug(
                    "Adding switch entity %s for %s",
                    description.name,
                    protect_data.data[device_id].get("name"),
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
        self.entity_description = description
        self._name = f"{self.entity_description.name} {self._device_data['name']}"
        self._switch_type = self.entity_description.key

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._switch_type == _KEY_HDR_MODE:
            return self._device_data["hdr_mode"] is True
        if self._switch_type == _KEY_HIGH_FPS:
            return self._device_data["video_mode"] == TYPE_HIGH_FPS_ON
        if self._switch_type == _KEY_PRIVACY_MODE:
            return self._device_data["privacy_on"] is True
        return (
            self._device_data["status_light"] is True
            if "status_light" in self._device_data
            else True
        )

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
