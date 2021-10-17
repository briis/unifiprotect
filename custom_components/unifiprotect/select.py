"""This component provides select entities for Unifi Protect."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_DEVICE_MODEL,
    DEFAULT_ATTRIBUTION,
    DEVICES_WITH_CAMERA,
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_VIEWPORT,
    TYPE_LIGHT_RECORD_MOTION,
    TYPE_RECORD_ALWAYS,
    TYPE_RECORD_OFF,
    DOMAIN,
)
from .entity import UnifiProtectEntity

ATTR_VIEWS = "views"

_LOGGER = logging.getLogger(__name__)

_SELECT_NAME = 0
_SELECT_ICON = 1
_SELECT_TYPE = 2

LIGHT_MODE_MOTION = "On Motion"
LIGHT_MODE_DARK = "When Dark"
LIGHT_MODE_OFF = "Manual"
LIGHT_MODES = [LIGHT_MODE_MOTION, LIGHT_MODE_DARK, LIGHT_MODE_OFF]

RECORDING_MODES = ["Always", "Never", "Detections"]

SELECT_TYPES = {
    "recording_mode": [
        "Recording Mode",
        "video-outline",
        DEVICES_WITH_CAMERA,
    ],
    "viewer": [
        "Viewer",
        "view-dashboard",
        DEVICE_TYPE_VIEWPORT,
    ],
    "light_motion": [
        "Lightning",
        "spotlight",
        DEVICE_TYPE_LIGHT,
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

    # Get Current Views
    liveviews = await upv_object.get_live_views()

    select_entities = []
    for item, item_type in SELECT_TYPES.items():
        for device_id in protect_data.data:
            if protect_data.data[device_id].get("type") in item_type[_SELECT_TYPE]:
                select_entities.append(
                    UnifiProtectSelects(
                        upv_object,
                        protect_data,
                        server_info,
                        device_id,
                        item,
                        liveviews,
                    )
                )
                _LOGGER.debug(
                    "UNIFIPROTECT SELECT CREATED: %s",
                    protect_data.data[device_id].get("name"),
                )

    if not select_entities:
        return

    async_add_entities(select_entities)

    return True


class UnifiProtectSelects(UnifiProtectEntity, SelectEntity):
    """A Unifi Protect Select Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        select_entity,
        liveviews,
    ):
        """Initialize the Viewport Media Player."""
        super().__init__(upv_object, protect_data, server_info, device_id, None)
        self.upv = upv_object
        select_item = SELECT_TYPES[select_entity]
        self._name = f"{select_item[_SELECT_NAME]} {self._device_data['name']}"
        self._icon = f"mdi:{select_item[_SELECT_ICON]}"
        self._device_type = select_item[_SELECT_TYPE]
        self._liveviews = liveviews
        if self._device_type == DEVICE_TYPE_VIEWPORT:
            self._attr_options = self.viewport_view_names()
        elif self._device_type == DEVICE_TYPE_LIGHT:
            self._attr_options = LIGHT_MODES
        else:
            self._attr_options = RECORDING_MODES

    @property
    def name(self):
        """Return name of the entity."""
        return self._name

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        if self._device_type == DEVICE_TYPE_VIEWPORT:
            return self.get_view_name_from_id(self._device_data["liveview"])
        if self._device_type == DEVICE_TYPE_LIGHT:
            lightmode = self._device_data["motion_mode"]
            if lightmode == TYPE_LIGHT_RECORD_MOTION:
                lightmode = LIGHT_MODE_MOTION
            elif lightmode == TYPE_RECORD_ALWAYS:
                lightmode = LIGHT_MODE_DARK
            else:
                lightmode = LIGHT_MODE_OFF
            return lightmode

        return self._device_data["recording_mode"].capitalize()

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attr = {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
        }
        if self._device_type == DEVICE_TYPE_VIEWPORT:
            attr[ATTR_VIEWS] = self._liveviews

        return attr

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    def get_view_name_from_id(self, view_id):
        """Returns the Liveview Name from the ID"""
        _source = None
        for item in self._liveviews:
            if view_id == item["id"]:
                _source = item["name"]
                break
        return _source

    def get_view_id_from_name(self, view_name):
        """Returns the Liveview ID from the Name"""
        _id = None
        for item in self._liveviews:
            if view_name == item["name"]:
                _id = item["id"]
                break
        return _id

    def viewport_view_names(self):
        """Returns an arrya with the view names"""
        views = []
        for item in self._liveviews:
            views.append(item["name"])
        return views

    async def async_select_option(self, option: str) -> None:
        """Change the Select Entity Option."""
        if self._device_type == DEVICE_TYPE_VIEWPORT:
            if option in self.options:
                _LOGGER.debug("Viewport View set to: %s", option)
                view_id = self.get_view_id_from_name(option)
                await self.upv_object.set_viewport_view(self._device_id, view_id)
            else:
                raise ValueError(
                    f"Can't set the value to {option}. Allowed values are: {self.options}"
                )
        elif self._device_type == DEVICE_TYPE_LIGHT:
            if option in self.options:
                if option == LIGHT_MODE_MOTION:
                    lightmode = TYPE_LIGHT_RECORD_MOTION
                    timing = "fulltime"
                elif option == LIGHT_MODE_DARK:
                    lightmode = TYPE_RECORD_ALWAYS
                    timing = "dark"
                else:
                    lightmode = TYPE_RECORD_OFF
                    timing = None

                _LOGGER.debug("Changing Light Mode to %s", option)
                await self.upv.light_settings(
                    self._device_id, lightmode, enable_at=timing
                )
        else:
            if option in self.options:
                _LOGGER.debug("Changing Recording Mode to %s", option)
                await self.upv.set_camera_recording(self._device_id, option.lower())
