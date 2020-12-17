"""This component provides Switches for Unifi Protect."""

import logging

try:
    from homeassistant.components.switch import SwitchEntity as SwitchDevice
except ImportError:
    # Prior to HA v0.110
    from homeassistant.components.switch import SwitchDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    ATTR_CAMERA_TYPE,
    CONF_IR_OFF,
    CONF_IR_ON,
    DEFAULT_ATTRIBUTION,
    DOMAIN,
    TYPE_HIGH_FPS_ON,
    TYPE_RECORD_ALWAYS,
    TYPE_RECORD_MOTION,
    TYPE_RECORD_NEVER,
    TYPE_RECORD_SMARTDETECT,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

_SWITCH_NAME = 0
_SWITCH_ICON = 1
_SWITCH_TYPE = 2
_SWITCH_REQUIRES = 3

SWITCH_TYPES = {
    "record_motion": ["Record Motion", "video-outline", "record_motion", None],
    "record_always": ["Record Always", "video", "record_always", None],
    "record_smart": ["Record Smart", "video", "record_smart", "has_smartdetect"],
    "ir_mode": ["IR Active", "brightness-4", "ir_mode", None],
    "status_light": ["Status Light On", "led-on", "status_light", None],
    "hdr_mode": ["HDR Mode", "brightness-7", "hdr_mode", "has_hdr"],
    "high_fps": ["High FPS", "video-high-definition", "high_fps", "has_highfps"],
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up switches for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]

    if not protect_data.data:
        return

    ir_on = entry.data[CONF_IR_ON]
    if ir_on == "always_on":
        ir_on = "on"

    ir_off = entry.data[CONF_IR_OFF]
    if ir_off == "led_off":
        ir_off = "autoFilterOnly"
    elif ir_off == "always_off":
        ir_off = "off"

    switches = []
    for switch, switch_type in SWITCH_TYPES.items():
        required_field = switch_type[_SWITCH_REQUIRES]
        for camera_id in protect_data.data:
            # Only Add Switches if Camera supports it.
            if required_field and not protect_data.data[camera_id].get(required_field):
                continue

            switches.append(
                UnifiProtectSwitch(
                    upv_object,
                    protect_data,
                    server_info,
                    camera_id,
                    switch,
                    ir_on,
                    ir_off,
                )
            )
            _LOGGER.debug("UNIFIPROTECT SWITCH CREATED: %s", switch)

    async_add_entities(switches)


class UnifiProtectSwitch(UnifiProtectEntity, SwitchDevice):
    """A Unifi Protect Switch."""

    def __init__(
        self, upv_object, protect_data, server_info, camera_id, switch, ir_on, ir_off
    ):
        """Initialize an Unifi Protect Switch."""
        super().__init__(upv_object, protect_data, server_info, camera_id, switch)
        self.upv = upv_object
        switch_type = SWITCH_TYPES[switch]
        self._name = f"{switch_type[_SWITCH_NAME]} {self._camera_data['name']}"
        self._icon = f"mdi:{switch_type[_SWITCH_ICON]}"
        self._ir_on_cmd = ir_on
        self._ir_off_cmd = ir_off
        self._switch_type = switch_type[_SWITCH_TYPE]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._switch_type == "record_motion":
            return self._camera_data["recording_mode"] == TYPE_RECORD_MOTION
        elif self._switch_type == "record_always":
            return self._camera_data["recording_mode"] == TYPE_RECORD_ALWAYS
        elif self._switch_type == "record_smart":
            return self._camera_data["recording_mode"] == TYPE_RECORD_SMARTDETECT
        elif self._switch_type == "ir_mode":
            return self._camera_data["ir_mode"] == self._ir_on_cmd
        elif self._switch_type == "hdr_mode":
            return self._camera_data["hdr_mode"] is True
        elif self._switch_type == "high_fps":
            return self._camera_data["video_mode"] == TYPE_HIGH_FPS_ON
        else:
            return self._camera_data["status_light"] == "True"

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_CAMERA_TYPE: self._device_type,
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._switch_type == "record_motion":
            _LOGGER.debug(f"Turning on Motion Detection for {self._name}")
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_MOTION)
        elif self._switch_type == "record_always":
            _LOGGER.debug("Turning on Constant Recording")
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_ALWAYS)
        elif self._switch_type == "record_smart":
            _LOGGER.debug("Turning on SmartDetect Recording")
            await self.upv.set_camera_recording(
                self._camera_id, TYPE_RECORD_SMARTDETECT
            )
        elif self._switch_type == "ir_mode":
            _LOGGER.debug("Turning on IR")
            await self.upv.set_camera_ir(self._camera_id, self._ir_on_cmd)
        elif self._switch_type == "hdr_mode":
            _LOGGER.debug("Turning on HDR mode")
            await self.upv.set_camera_hdr_mode(self._camera_id, True)
        elif self._switch_type == "high_fps":
            _LOGGER.debug("Turning on High FPS mode")
            await self.upv.set_camera_video_mode_highfps(self._camera_id, True)
        else:
            _LOGGER.debug("Changing Status Light to On")
            await self.upv.set_camera_status_light(self._camera_id, True)
        await self.protect_data.async_refresh(force_camera_update=True)

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if self._switch_type == "ir_mode":
            _LOGGER.debug("Turning off IR")
            await self.upv.set_camera_ir(self._camera_id, self._ir_off_cmd)
        elif self._switch_type == "status_light":
            _LOGGER.debug("Changing Status Light to Off")
            await self.upv.set_camera_status_light(self._camera_id, False)
        elif self._switch_type == "hdr_mode":
            _LOGGER.debug("Turning off HDR mode")
            await self.upv.set_camera_hdr_mode(self._camera_id, False)
        elif self._switch_type == "high_fps":
            _LOGGER.debug("Turning off High FPS mode")
            await self.upv.set_camera_video_mode_highfps(self._camera_id, False)
        else:
            _LOGGER.debug("Turning off Recording")
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_NEVER)
        await self.protect_data.async_refresh(force_camera_update=True)
