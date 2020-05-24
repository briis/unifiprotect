""" This component provides Switches for Unifi Protect."""

import logging
import voluptuous as vol
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.device_registry as dr

try:
    from homeassistant.components.switch import SwitchEntity as SwitchDevice
except ImportError:
    # Prior to HA v0.110
    from homeassistant.components.switch import SwitchDevice
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_ID,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
from .const import (
    ATTR_CAMERA_TYPE,
    CONF_IR_ON,
    CONF_IR_OFF,
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    TYPE_RECORD_ALLWAYS,
    TYPE_RECORD_MOTION,
    TYPE_RECORD_NEVER,
    TYPE_IR_AUTO,
    TYPE_IR_OFF,
    TYPE_IR_LED_OFF,
    TYPE_IR_ON,
    ENTITY_ID_SWITCH_FORMAT,
    ENTITY_UNIQUE_ID,
)

_LOGGER = logging.getLogger(__name__)

SWITCH_TYPES = {
    "record_motion": ["Record Motion", "camcorder", "record_motion"],
    "record_always": ["Record Always", "camcorder", "record_always"],
    "ir_mode": ["IR Active", "brightness-4", "ir_mode"],
}


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """A Ubiquiti Unifi Protect Sensor."""
    upv_object = hass.data[DOMAIN][entry.data[CONF_ID]]["upv"]
    coordinator = hass.data[DOMAIN][entry.data[CONF_ID]]["coordinator"]
    if not coordinator.data:
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
        for camera in coordinator.data:
            switches.append(
                UnifiProtectSwitch(
                    coordinator,
                    upv_object,
                    camera,
                    switch,
                    ir_on,
                    ir_off,
                    entry.data[CONF_ID],
                )
            )

    async_add_entities(switches, True)

    return True


class UnifiProtectSwitch(SwitchDevice):
    """A Unifi Protect Switch."""

    def __init__(
        self, coordinator, upv_object, camera, switch, ir_on, ir_off, instance
    ):
        """Initialize an Unifi Protect Switch."""
        self.coordinator = coordinator
        self.upv = upv_object
        self._camera_id = camera
        self._camera = self.coordinator.data[camera]
        self._name = f"{SWITCH_TYPES[switch][0]} {self._camera['name']}"
        self._mac = self._camera["mac"]
        self._firmware_version = self._camera["firmware_version"]
        self._server_id = self._camera["server_id"]
        self._icon = f"mdi:{SWITCH_TYPES[switch][2]}"
        self._ir_on_cmd = ir_on
        self._ir_off_cmd = ir_off
        self._camera_type = self._camera["type"]
        self._switch_type = SWITCH_TYPES[switch][2]

        self.entity_id = ENTITY_ID_SWITCH_FORMAT.format(
            slugify(instance), slugify(self._name).replace(" ", "_")
        )
        self._unique_id = ENTITY_UNIQUE_ID.format(switch, self._mac)

        _LOGGER.debug(f"UNIFIPROTECT SWITCH CREATED: {self._name}")

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def should_poll(self):
        """Poll for status regularly."""
        return False

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        camera = self.coordinator.data[self._camera_id]
        if self._switch_type == "record_motion":
            enabled = True if camera["recording_mode"] == TYPE_RECORD_MOTION else False
        elif self._switch_type == "record_always":
            enabled = True if camera["recording_mode"] == TYPE_RECORD_ALLWAYS else False
        else:
            enabled = True if camera["ir_mode"] == self._ir_on_cmd else False
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
            ATTR_CAMERA_TYPE: self._camera_type,
        }

    @property
    def device_info(self):
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "name": self.name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._camera_type,
            "sw_version": self._firmware_version,
            "via_device": (DOMAIN, self._server_id),
        }

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self._switch_type == "record_motion":
            _LOGGER.debug("Turning on Motion Detection")
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_MOTION)
        elif self._switch_type == "record_always":
            _LOGGER.debug("Turning on Constant Recording")
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_ALLWAYS)
        else:
            _LOGGER.debug("Turning on IR")
            await self.upv.set_camera_ir(self._camera_id, self._ir_on_cmd)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if self._switch_type == "ir_mode":
            _LOGGER.debug("Turning off IR")
            await self.upv.set_camera_ir(self._camera_id, self._ir_off_cmd)
        else:
            _LOGGER.debug("Turning off Recording")
            await self.upv.set_camera_recording(self._camera_id, TYPE_RECORD_NEVER)
        await self.coordinator.async_request_refresh()
