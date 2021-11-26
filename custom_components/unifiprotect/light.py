"""This component provides Lights for Unifi Protect."""
from __future__ import annotations
from datetime import timedelta

import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from pyunifiprotect.data.devices import Light
from pyunifiprotect.data.types import LightModeEnableType, LightModeType
from pyunifiprotect.utils import to_js_time

from .const import (
    ATTR_ONLINE,
    ATTR_UP_SINCE,
    DOMAIN,
    LIGHT_SETTINGS_SCHEMA,
    SERVICE_LIGHT_SETTINGS,
)
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)

ON_STATE = True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up lights for UniFi Protect integration."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    entities = [
        UnifiProtectLight(
            protect,
            protect_data,
            device,
        )
        for device in protect.bootstrap.lights.values()
    ]

    if not entities:
        return

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(
        SERVICE_LIGHT_SETTINGS, LIGHT_SETTINGS_SCHEMA, "async_light_settings"
    )

    async_add_entities(entities)


def unifi_brightness_to_hass(value):
    """Convert unifi brightness 1..6 to hass format 0..255."""
    return min(255, round((value / 6) * 255))


def hass_to_unifi_brightness(value):
    """Convert hass brightness 0..255 to unifi 1..6 scale."""
    return max(1, round((value / 255) * 6))


class UnifiProtectLight(UnifiProtectEntity, LightEntity):
    """A Ubiquiti Unifi Protect Light Entity."""

    def __init__(self, protect, protect_data, device):
        """Initialize an Unifi light."""
        super().__init__(protect, protect_data, device, None)
        self.device: Light = device
        self._attr_name = self.device.name
        self._attr_icon = "mdi:spotlight-beam"
        self._attr_supported_features = SUPPORT_BRIGHTNESS
        self._async_update_device_from_protect()

    @callback
    def _async_update_device_from_protect(self):
        super()._async_update_device_from_protect()
        self._attr_is_on = self.device.is_light_on
        self._attr_brightness = unifi_brightness_to_hass(
            self.device.light_device_settings.led_level
        )

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        hass_brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
        unifi_brightness = hass_to_unifi_brightness(hass_brightness)

        _LOGGER.debug("Turning on light with brightness %s", unifi_brightness)
        await self.device.set_light(True, unifi_brightness)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        _LOGGER.debug("Turning off light")
        await self.device.set_light(False)

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return {
            **super().extra_state_attributes,
            ATTR_ONLINE: self.device.is_connected,
            ATTR_UP_SINCE: to_js_time(self.device.up_since),
        }

    async def async_light_settings(
        self,
        mode,
        enable_at: str | None = None,
        duration: int | None = None,
        sensitivity: int | None = None,
    ):
        """Adjust Light Settings."""

        turn_off_duration: timedelta | None = None
        enable_at_mode: LightModeEnableType | None = None
        if enable_at is not None:
            enable_at_mode = LightModeEnableType(enable_at)
        if duration is not None:
            turn_off_duration = timedelta(seconds=duration)

        await self.device.set_light_settings(
            LightModeType(mode),
            enable_at=enable_at_mode,
            duration=turn_off_duration,
            sensitivity=sensitivity,
        )
