"""This component provides Switches for Unifi Protect."""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from .const import (
    ATTR_DEVICE_MODEL,
    DEFAULT_ATTRIBUTION,
    DOMAIN,
    TYPE_HIGH_FPS_ON,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

_SWITCH_NAME = 0
_SWITCH_ICON = 1
_SWITCH_TYPE = 2
_SWITCH_REQUIRES = 3

SWITCH_TYPES = {
    "status_light": ["Status Light On", "led-on", "status_light", "has_ledstatus"],
    "hdr_mode": ["HDR Mode", "brightness-7", "hdr_mode", "has_hdr"],
    "high_fps": ["High FPS", "video-high-definition", "high_fps", "has_highfps"],
}


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
    for switch, switch_type in SWITCH_TYPES.items():
        required_field = switch_type[_SWITCH_REQUIRES]

        for device_id in protect_data.data:
            # Only Add Switches if Device supports it.
            if required_field and not protect_data.data[device_id].get(required_field):
                continue

            switches.append(
                UnifiProtectSwitch(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    switch,
                )
            )
            _LOGGER.debug("UNIFIPROTECT SWITCH CREATED: %s", switch)

    async_add_entities(switches)


class UnifiProtectSwitch(UnifiProtectEntity, SwitchEntity):
    """A Unifi Protect Switch."""

    def __init__(self, upv_object, protect_data, server_info, device_id, switch):
        """Initialize an Unifi Protect Switch."""
        super().__init__(upv_object, protect_data, server_info, device_id, switch)
        self.upv = upv_object
        switch_type = SWITCH_TYPES[switch]
        self._name = f"{switch_type[_SWITCH_NAME]} {self._device_data['name']}"
        self._icon = f"mdi:{switch_type[_SWITCH_ICON]}"
        self._switch_type = switch_type[_SWITCH_TYPE]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._switch_type == "hdr_mode":
            return self._device_data["hdr_mode"] is True
        if self._switch_type == "high_fps":
            return self._device_data["video_mode"] == TYPE_HIGH_FPS_ON
        return (
            self._device_data["status_light"] is True
            if "status_light" in self._device_data
            else True
        )

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._switch_type == "hdr_mode":
            _LOGGER.debug("Turning on HDR mode")
            await self.upv.set_camera_hdr_mode(self._device_id, True)
        elif self._switch_type == "high_fps":
            _LOGGER.debug("Turning on High FPS mode")
            await self.upv.set_camera_video_mode_highfps(self._device_id, True)
        else:
            _LOGGER.debug("Changing Status Light to On")
            await self.upv.set_device_status_light(
                self._device_id, True, self._device_type
            )
        await self.protect_data.async_refresh(force_camera_update=True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if self._switch_type == "status_light":
            _LOGGER.debug("Changing Status Light to Off")
            await self.upv.set_device_status_light(
                self._device_id, False, self._device_type
            )
        elif self._switch_type == "hdr_mode":
            _LOGGER.debug("Turning off HDR mode")
            await self.upv.set_camera_hdr_mode(self._device_id, False)
        else:
            _LOGGER.debug("Turning off High FPS mode")
            await self.upv.set_camera_video_mode_highfps(self._device_id, False)

        await self.protect_data.async_refresh(force_camera_update=True)
