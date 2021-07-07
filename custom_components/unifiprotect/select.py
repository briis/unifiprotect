"""This component provides select entities for Unifi Protect."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_DEVICE_MODEL,
    DEFAULT_ATTRIBUTION,
    DEVICE_TYPE_VIEWPORT,
    DOMAIN,
)
from .entity import UnifiProtectEntity

ATTR_VIEWS = "views"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Viewport Live Views for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    if not protect_data.data:
        return

    # Get Current Views
    liveviews = await upv_object.get_live_views()

    views = []
    for device_id in protect_data.data:
        device_data = protect_data.data[device_id]
        if device_data["type"] == DEVICE_TYPE_VIEWPORT:
            views.append(
                UnifiProtectSelects(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    DEVICE_TYPE_VIEWPORT,
                    liveviews,
                )
            )
            _LOGGER.debug(
                "UNIFIPROTECT SELECT CREATED: %s",
                device_data["name"],
            )

    if not views:
        return

    async_add_entities(views)

    return True


class UnifiProtectSelects(UnifiProtectEntity, SelectEntity):
    """A Unifi Protect Select Entity."""

    def __init__(
        self,
        upv_object,
        protect_data,
        server_info,
        device_id,
        sensor_type,
        liveviews,
    ):
        """Initialize the Viewport Media Player."""
        super().__init__(upv_object, protect_data, server_info, device_id, None)
        self._name = f"{sensor_type.capitalize()} {self._device_data['name']}"
        self._liveviews = liveviews
        self._attr_options = self.viewport_view_names()
        self._name = f"{sensor_type.capitalize()} {self._device_data['name']}"

    @property
    def name(self):
        """Return name of the entity."""
        return self._name

    @property
    def current_option(self) -> str:
        """Return the current selected option."""
        return self.get_view_name_from_id(self._device_data["liveview"])

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_DEVICE_MODEL: self._model,
            ATTR_VIEWS: self._liveviews,
        }

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
        """Change the diffuser room size."""
        if option in self.options:
            _LOGGER.debug("OPTION: %s", option)
            view_id = self.get_view_id_from_name(option)
            await self.upv_object.set_viewport_view(self._device_id, view_id)
        else:
            raise ValueError(
                f"Can't set the value to {option}. Allowed values are: {self.options}"
            )