"""This component provides number entities for Unifi Protect."""
import logging
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from .const import (
    ATTR_DEVICE_MODEL,
    DEFAULT_ATTRIBUTION,
    DEVICES_WITH_CAMERA,
    DOMAIN,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)

_ENTITY_WDR = "wdr_value"

_NUMBER_NAME = 0
_NUMBER_ICON = 1
_NUMBER_MIN_VALUE = 2
_NUMBER_MAX_VALUE = 3
_NUMBER_STEP = 4
_NUMBER_MODE = 5
_NUMBER_TYPE = 6

NUMBER_TYPES = {
    _ENTITY_WDR: [
        "Wide Dynamic Range",
        "state-machine",
        0,
        3,
        1,
        "auto",
        DEVICES_WITH_CAMERA,
    ],
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    if not protect_data.data:
        return

    number_entities = []
    for item, item_type in NUMBER_TYPES.items():
        for device_id in protect_data.data:
            if protect_data.data[device_id].get("type") in item_type[_NUMBER_TYPE]:
                number_entities.append(
                    UnifiProtectNumbers(
                        upv_object,
                        protect_data,
                        server_info,
                        device_id,
                        item,
                    )
                )
                _LOGGER.debug(
                    "UNIFIPROTECT NUMBER ENTITY CREATED: %s %s",
                    item_type[_NUMBER_NAME],
                    protect_data.data[device_id].get("name"),
                )

    if not number_entities:
        return

    async_add_entities(number_entities)

    return True


class UnifiProtectNumbers(UnifiProtectEntity, NumberEntity):
    """A Unifi Protect Number Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        number_entity,
    ):
        """Initialize the Number Entities."""
        super().__init__(
            upv_object, protect_data, server_info, device_id, number_entity
        )
        self.upv = upv_object
        self._number_entity = number_entity
        number_item = NUMBER_TYPES[self._number_entity]
        self._name = f"{number_item[_NUMBER_NAME]} {self._device_data['name']}"
        self._icon = f"mdi:{number_item[_NUMBER_ICON]}"
        self._device_type = number_item[_NUMBER_TYPE]
        self._attr_max_value = number_item[_NUMBER_MAX_VALUE]
        self._attr_min_value = number_item[_NUMBER_MIN_VALUE]
        self._attr_step = number_item[_NUMBER_STEP]
        self._attr_mode = number_item[_NUMBER_MODE]

    @property
    def name(self):
        """Return name of the entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._number_entity == _ENTITY_WDR:
            return self._device_data["wdr"]

    @property
    def mode(self):
        """Return the mode of the entity."""
        return self._attr_mode

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attr = {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
        }

        return attr

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    async def async_set_value(self, value: float) -> None:
        """Set new value."""
        if self._number_entity == _ENTITY_WDR:
            _LOGGER.debug(
                "Setting WDR Value to %s for Camera %s",
                value,
                self._device_data["name"],
            )
            await self.upv.set_camera_wdr(self._device_id, value)
