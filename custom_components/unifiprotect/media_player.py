"""Provides support for the Viewport Device, using Media Player."""
import logging

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_PLAY_MEDIA,
    SUPPORT_SELECT_SOURCE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    STATE_OFF,
    STATE_PLAYING,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform

from .const import (
    ATTR_DEVICE_MODEL,
    DEFAULT_ATTRIBUTION,
    DEVICE_TYPE_VIEWPORT,
    DOMAIN,
    SERVICE_SET_VIEWPORT_VIEW,
    SET_VIEW_PORT_VIEW_SCHEMA,
)
from .entity import UnifiProtectEntity

SUPPORT_VIEWPORT = SUPPORT_SELECT_SOURCE | SUPPORT_PLAY_MEDIA
ATTR_VIEWS = "views"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Set up Viewport Media Players for UniFi Protect integration."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    server_info = entry_data["server_info"]
    if not protect_data.data:
        return

    # Get Current Views
    liveviews = await upv_object.get_live_views()

    viewports = []
    for device_id in protect_data.data:
        device_data = protect_data.data[device_id]
        if device_data["type"] == DEVICE_TYPE_VIEWPORT:
            viewports.append(
                UnifiProtectMediaPlayer(
                    upv_object,
                    protect_data,
                    server_info,
                    device_id,
                    DEVICE_TYPE_VIEWPORT,
                    liveviews,
                )
            )
            _LOGGER.debug(
                "UNIFIPROTECT VIEWPORT PLAYER CREATED: %s",
                device_data["name"],
            )

    if not viewports:
        return

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_SET_VIEWPORT_VIEW, SET_VIEW_PORT_VIEW_SCHEMA, "async_set_viewport_view"
    )

    async_add_entities(viewports)

    return True


class UnifiProtectMediaPlayer(UnifiProtectEntity, MediaPlayerEntity):
    """A Unifi Protect Viewport Media Player."""

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

    @property
    def name(self):
        """Return name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return Off if Viewport is Off, else Playing."""
        if self._device_data["online"]:
            return STATE_PLAYING
        return STATE_OFF

    @property
    def icon(self):
        """Sets the icon for this device."""
        return "mdi:monitor-dashboard"

    @property
    def source(self):
        """Name of the current liveview source."""
        return self.get_view_name_from_id(self._device_data["liveview"])

    @property
    def source_list(self):
        """List of available liveview sources."""
        _sources = []
        for item in self._liveviews:
            _sources.append(item["name"])
        return _sources

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_VIEWPORT

    @property
    def media_title(self):
        """Title of current playing media."""
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

    async def async_select_source(self, source):
        """Set the Liveview."""
        self._liveviews = await self.upv_object.get_live_views()
        view_id = None
        for item in self._liveviews:
            if item["name"] == source:
                view_id = item["id"]
                break

        if view_id is not None:
            await self.async_set_viewport_view(view_id)

    async def async_set_viewport_view(self, view_id):
        """Change Liveview on Viewport."""

        await self.upv_object.set_viewport_view(self._device_id, view_id)
