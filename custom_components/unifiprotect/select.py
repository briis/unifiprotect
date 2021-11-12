"""This component provides select entities for Unifi Protect."""
import logging
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import (
    CUSTOM_MESSAGE,
    DEVICES_WITH_CAMERA,
    DEVICE_TYPE_DOORBELL,
    DEVICE_TYPE_LIGHT,
    DEVICE_TYPE_VIEWPORT,
    ENTITY_CATEGORY_CONFIG,
    TYPE_INFRARED_AUTO,
    TYPE_INFRARED_AUTOFILTER,
    TYPE_INFRARED_OFF,
    TYPE_INFRARED_ON,
    TYPE_LIGHT_RECORD_MOTION,
    TYPE_RECORD_ALWAYS,
    TYPE_RECORD_OFF,
    DOMAIN,
)
from .entity import UnifiProtectEntity

ATTR_VIEWS = "views"

_LOGGER = logging.getLogger(__name__)

_SELECT_ENTITY_IR = "infrared"
_SELECT_ENTITY_REC_MODE = "recording_mode"
_SELECT_ENTITY_VIEWER = "viewer"
_SELECT_ENTITY_LIGHT_MOTION = "light_motion"
_SELECT_ENTITY_DOORBELL_TEXT = "doorbell_text"

DOORBELL_BASE_TEXT = [
    {"id": "LEAVE_PACKAGE_AT_DOOR", "value": "LEAVE PACKAGE AT DOOR"},
    {"id": "DO_NOT_DISTURB", "value": "DO NOT DISTURB"},
]

INFRARED_MODES = [
    {"id": TYPE_INFRARED_AUTO, "name": "Auto"},
    {"id": TYPE_INFRARED_ON, "name": "Always Enable"},
    {"id": TYPE_INFRARED_AUTOFILTER, "name": "Auto (Filter Only, no LED's)"},
    {"id": TYPE_INFRARED_OFF, "name": "Always Disable"},
]

LIGHT_MODE_MOTION = "On Motion"
LIGHT_MODE_DARK = "When Dark"
LIGHT_MODE_OFF = "Manual"
LIGHT_MODES = [LIGHT_MODE_MOTION, LIGHT_MODE_DARK, LIGHT_MODE_OFF]

RECORDING_MODES = ["Always", "Never", "Detections"]


@dataclass
class UnifiprotectRequiredKeysMixin:
    """Mixin for required keys."""

    ufp_device_type: str


@dataclass
class UnifiProtectSelectEntityDescription(
    SelectEntityDescription, UnifiprotectRequiredKeysMixin
):
    """Describes Unifi Protect Sensor entity."""


SELECT_TYPES: tuple[UnifiProtectSelectEntityDescription, ...] = (
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_REC_MODE,
        name="Recording Mode",
        icon="mdi:video-outline",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_type=DEVICES_WITH_CAMERA,
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_VIEWER,
        name="Viewer",
        icon="mdi:view-dashboard",
        ufp_device_type=DEVICE_TYPE_VIEWPORT,
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_LIGHT_MOTION,
        name="Lightning",
        icon="mdi:spotlight",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_type=DEVICE_TYPE_LIGHT,
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_IR,
        name="Infrared",
        icon="mdi:circle-opacity",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_type=DEVICES_WITH_CAMERA,
    ),
    UnifiProtectSelectEntityDescription(
        key=_SELECT_ENTITY_DOORBELL_TEXT,
        name="Doorbell Text",
        icon="mdi:card-text",
        entity_category=ENTITY_CATEGORY_CONFIG,
        ufp_device_type=DEVICE_TYPE_DOORBELL,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Select entities for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    doorbell_text = entry_data["doorbell_text"]

    if not protect_data.data:
        return

    # Get Current Views
    liveviews = await upv_object.get_live_views()

    entities = []
    for description in SELECT_TYPES:
        for device_id in protect_data.data:
            if (
                protect_data.data[device_id].get("type")
                not in description.ufp_device_type
            ):
                continue

            entities.append(
                UnifiProtectSelects(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    description,
                    liveviews,
                    doorbell_text,
                )
            )
            _LOGGER.debug(
                "Adding select entity %s for %s",
                description.name,
                protect_data.data[device_id].get("name"),
            )

    if not entities:
        return

    async_add_entities(entities)


class UnifiProtectSelects(UnifiProtectEntity, SelectEntity):
    """A Unifi Protect Select Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        description: UnifiProtectSelectEntityDescription,
        liveviews,
        doorbell_text,
    ):
        """Initialize the Viewport Media Player."""
        super().__init__(upv_object, protect_data, server_info, device_id, description)
        self._select_entity = self.entity_description.key
        self._name = f"{self.entity_description.name} {self._device_data['name']}"
        self._device_type = self.entity_description.ufp_device_type
        self._liveviews = liveviews

        self._doorbell_texts = []
        if self._select_entity == _SELECT_ENTITY_VIEWER:
            self._attr_options = self.viewport_view_names()
        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
            self._attr_options = LIGHT_MODES
        if self._select_entity == _SELECT_ENTITY_IR:
            self._attr_options = self.infrared_names()
        if self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            for item in DOORBELL_BASE_TEXT:
                self._doorbell_texts.append({"id": item["id"], "value": item["value"]})
            if doorbell_text is not None:
                _local_text = doorbell_text.split(",")
                for item in _local_text:
                    if len(item.strip()) == 0:
                        continue
                    self._doorbell_texts.append(
                        {"id": CUSTOM_MESSAGE, "value": item.strip()}
                    )
            self._attr_options = self.doorbell_texts()
        if self._select_entity == _SELECT_ENTITY_REC_MODE:
            self._attr_options = RECORDING_MODES

    @property
    def name(self):
        """Return name of the entity."""
        return self._name

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        if self._select_entity == _SELECT_ENTITY_VIEWER:
            return self.get_view_name_from_id(self._device_data["liveview"])

        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
            lightmode = self._device_data["motion_mode"]
            if lightmode == TYPE_LIGHT_RECORD_MOTION:
                lightmode = LIGHT_MODE_MOTION
            elif lightmode == TYPE_RECORD_ALWAYS:
                lightmode = LIGHT_MODE_DARK
            else:
                lightmode = LIGHT_MODE_OFF
            return lightmode

        if self._select_entity == _SELECT_ENTITY_IR:
            return self.get_infrared_name_from_id()

        if self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            return self._device_data["doorbell_text"]

        return self._device_data["recording_mode"].capitalize()

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attr = {
            **super().extra_state_attributes,
        }
        if self._device_type == DEVICE_TYPE_VIEWPORT:
            attr[ATTR_VIEWS] = self._liveviews

        return attr

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

    def get_infrared_name_from_id(self):
        """Returns Select Option from Infrared setting"""
        _value = None
        for item in INFRARED_MODES:
            if self._device_data["ir_mode"] == item["id"]:
                _value = item["name"]
                break
        return _value

    def get_infrared_id_from_name(self, option):
        """Returns Infrared setting from Select Option"""
        _value = None
        for item in INFRARED_MODES:
            if option == item["name"]:
                _value = item["id"]
                break
        return _value

    def infrared_names(self):
        """Returns valid options array for Infrared"""
        arr = []
        for item in INFRARED_MODES:
            arr.append(item["name"])
        return arr

    def get_doorbell_text_type_from_name(self, option):
        """Returns the Doorbell Text Type from the Option Text"""
        _id = None
        for item in self._doorbell_texts:
            if option == item["value"]:
                _id = item["id"]
                break
        return _id

    def doorbell_texts(self):
        """Returns a list of defined Doorbell Texts"""
        arr = []
        for item in self._doorbell_texts:
            arr.append(item["value"])

        return arr

    async def async_select_option(self, option: str) -> None:
        """Change the Select Entity Option."""
        if self._select_entity == _SELECT_ENTITY_VIEWER:
            if option in self.options:
                _LOGGER.debug("Viewport View set to: %s", option)
                view_id = self.get_view_id_from_name(option)
                await self.upv_object.set_viewport_view(self._device_id, view_id)
            else:
                raise ValueError(
                    f"Can't set the value to {option}. Allowed values are: {self.options}"
                )

        if self._select_entity == _SELECT_ENTITY_LIGHT_MOTION:
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
                await self.upv_object.light_settings(
                    self._device_id, lightmode, enable_at=timing
                )

        if self._select_entity == _SELECT_ENTITY_IR:
            if option in self.options:
                infrared_id = self.get_infrared_id_from_name(option)
                await self.upv_object.set_camera_ir(self._device_id, infrared_id)

        if self._select_entity == _SELECT_ENTITY_DOORBELL_TEXT:
            if option in self.options:
                text_type = self.get_doorbell_text_type_from_name(option)
                await self.upv_object.set_doorbell_lcd_text(
                    self._device_id, text_type, option
                )
                _LOGGER.debug("Changed Doorbell LCD Text to: %s", option)

        if self._select_entity == _SELECT_ENTITY_REC_MODE:
            if option in self.options:
                _LOGGER.debug("Changing Recording Mode to %s", option)
                await self.upv_object.set_camera_recording(
                    self._device_id, option.lower()
                )
