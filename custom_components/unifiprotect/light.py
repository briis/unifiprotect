"""This component provides Lights for Unifi Protect."""

import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform

from .const import (
    ATTR_DEVICE_MODEL,
    ATTR_ONLINE,
    ATTR_UP_SINCE,
    DEFAULT_ATTRIBUTION,
    DEVICE_TYPE_LIGHT,
    DOMAIN,
    LIGHT_SETTINGS_SCHEMA,
    SERVICE_LIGHT_SETTINGS,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

ON_STATE = True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up lights for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]

    if not protect_data.data:
        return

    lights = []
    for light_id in protect_data.data:
        if protect_data.data[light_id].get("type") == DEVICE_TYPE_LIGHT:
            lights.append(
                UnifiProtectLight(
                    upv_object,
                    protect_data,
                    server_info,
                    light_id,
                )
            )

    if not lights:
        # No lights found
        return

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_LIGHT_SETTINGS, LIGHT_SETTINGS_SCHEMA, "async_light_settings"
    )

    async_add_entities(lights)


def unifi_brightness_to_hass(value):
    """Convert unifi brightness 1..6 to hass format 0..255."""
    return min(255, round((value / 6) * 255))


def hass_to_unifi_brightness(value):
    """Convert hass brightness 0..255 to unifi 1..6 scale."""
    return max(1, round((value / 255) * 6))


class UnifiProtectLight(UnifiProtectEntity, LightEntity):
    """A Ubiquiti Unifi Protect Light Entity."""

    def __init__(self, upv_object, protect_data, server_info, light_id):
        """Initialize an Unifi light."""
        super().__init__(upv_object, protect_data, server_info, light_id, None)
        self._name = self._device_data["name"]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """If the light is currently on or off."""
        return self._device_data["is_on"] == ON_STATE

    @property
    def icon(self):
        """Return the Icon for this light."""
        return "mdi:spotlight-beam"

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return unifi_brightness_to_hass(self._device_data["brightness"])

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        hass_brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness)
        unifi_brightness = hass_to_unifi_brightness(hass_brightness)

        _LOGGER.debug("Turning on light with brightness %s", unifi_brightness)
        await self.upv_object.set_light_on_off(self._device_id, True, unifi_brightness)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        _LOGGER.debug("Turning off light")
        await self.upv_object.set_light_on_off(self._device_id, False)

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
            ATTR_ONLINE: self._device_data["online"],
            ATTR_UP_SINCE: self._device_data["up_since"],
        }

    async def async_light_settings(self, mode, **kwargs):
        """Adjust Light Settings."""
        k_enable_at = kwargs.get("enable_at")
        k_duration = kwargs.get("duration")
        if k_duration is not None:
            k_duration = k_duration * 1000
        k_sensitivity = kwargs.get("sensitivity")

        await self.upv_object.light_settings(
            self._device_id,
            mode,
            enable_at=k_enable_at,
            duration=k_duration,
            sensitivity=k_sensitivity,
        )
