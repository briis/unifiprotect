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
    TYPE_RECORD_ALLWAYS,
    TYPE_RECORD_MOTION,
    TYPE_RECORD_NEVER,
    TYPE_RECORD_SMARTDETECT,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = {
    "record_motion": ["Record Motion", "video-outline", "record_motion"],
    "record_always": ["Record Always", "video", "record_always"],
    "record_smart": ["Record Smart", "video", "record_smart"],
    "ir_mode": ["IR Active", "brightness-4", "ir_mode"],
    "status_light": ["Status Light On", "led-on", "status_light"],
    "hdr_mode": ["HDR Mode", "brightness-7", "hdr_mode"],
    "high_fps": ["High FPS", "video-high-definition", "high_fps"],
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up switches for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]

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
    for switch in SWITCH_TYPES:
        for camera in protect_data.data:
            # Only Add Switches if Camera supports it.
            if switch == "high_fps" and not protect_data.data[camera].get(
                "has_highfps"
            ):
                # High FPS is only supported on certain cameras
                continue
            if switch == "hdr_mode" and not protect_data.data[camera].get("has_hdr"):
                continue
            # SmartDetect capable cameras only
            if switch == "record_smart" and not protect_data.data[camera].get(
                "has_smartdetect"
            ):
                continue

            switches.append(
                UnifiProtectSwitch(
                    upv_object,
                    protect_data,
                    camera,
                    switch,
                    ir_on,
                    ir_off,
                )
            )
            _LOGGER.debug("UNIFIPROTECT SWITCH CREATED: %s", switch)

    async_add_entities(switches)


class UnifiProtectSwitch(UnifiProtectEntity, SwitchDevice):
    """A Unifi Protect Switch."""

    def __init__(self, upv_object, protect_data, camera_id, switch, ir_on, ir_off):
        """Initialize an Unifi Protect Switch."""
        super().__init__(upv_object, protect_data, camera_id, switch)
        self.upv = upv_object
        self._name = f"{SWITCH_TYPES[switch][0]} {self._camera_data['name']}"
        self._icon = f"mdi:{SWITCH_TYPES[switch][1]}"
        self._ir_on_cmd = ir_on
        self._ir_off_cmd = ir_off
        self._switch_type = SWITCH_TYPES[switch][2]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        if self._switch_type == "record_motion":
            enabled = (
                True
                if self._camera_data["recording_mode"] == TYPE_RECORD_MOTION
                else False
            )
        elif self._switch_type == "record_always":
            enabled = (
                True
                if self._camera_data["recording_mode"] == TYPE_RECORD_ALLWAYS
                else False
            )
        elif self._switch_type == "record_smart":
            enabled = (
                True
                if self._camera_data["recording_mode"] == TYPE_RECORD_SMARTDETECT
                else False
            )
        elif self._switch_type == "ir_mode":
            enabled = True if self._camera_data["ir_mode"] == self._ir_on_cmd else False
        elif self._switch_type == "hdr_mode":
            enabled = self._camera_data["hdr_mode"] is True
        elif self._switch_type == "high_fps":
            enabled = (
                True if self._camera_data["video_mode"] == TYPE_HIGH_FPS_ON else False
            )
        else:
            enabled = True if self._camera_data["status_light"] == "True" else False
        return enabled

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
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_ALLWAYS)
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
