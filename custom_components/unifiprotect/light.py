"""This component provides Lights for Unifi Protect."""

import logging

from homeassistant.components.light import (
    LightEntity,
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    ATTR_DEVICE_MODEL,
    ATTR_ONLINE,
    ATTR_UP_SINCE,
    DEFAULT_ATTRIBUTION,
    DEVICE_LIGHT,
    DOMAIN,
)

from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

ON_STATE = True


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
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
        if protect_data.data[light_id].get("type") == DEVICE_LIGHT:
            lights.append(
                UnifiProtectLight(
                    upv_object,
                    protect_data,
                    server_info,
                    light_id,
                )
            )

    async_add_entities(lights)

    # TODO: Add Light Services

    return True


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
        self.upv = upv_object
        self._name = self._camera_data["name"]

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def is_on(self):
        """If the light is currently on or off."""
        return self._camera_data["is_on"] == ON_STATE

    @property
    def icon(self):
        """Return the Icon for this light."""
        return "mdi:spotlight-beam"

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return unifi_brightness_to_hass(self._camera_data["brightness"])

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = hass_to_unifi_brightness(kwargs[ATTR_BRIGHTNESS])
        else:
            brightness = hass_to_unifi_brightness(self.brightness)

        _LOGGER.debug("Turning on light with brightness %s", brightness)
        await self.upv.set_light_on_off(self._camera_id, True, brightness)

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        _LOGGER.debug("Turning off light")
        await self.upv.set_light_on_off(self._camera_id, False)

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
            ATTR_ONLINE: self._camera_data["online"],
            ATTR_UP_SINCE: self._camera_data["up_since"],
        }

    # TODO: Add Light Services