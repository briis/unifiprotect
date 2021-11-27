"""Base class for protect data."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Generator, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from pyunifiprotect import ProtectApiClient
from pyunifiprotect.data import Bootstrap, Event, ModelType, WSSubscriptionMessage
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel
from pyunifiprotect.data.nvr import NVR, Liveview
from pyunifiprotect.exceptions import NotAuthorized, NvrError

from .const import DEVICES_WITH_ENTITIES

_LOGGER = logging.getLogger(__name__)


class UnifiProtectData:
    """Coordinate updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        protect: ProtectApiClient,
        update_interval: timedelta,
        entry: ConfigEntry,
    ):
        """Initialize an subscriber."""
        super().__init__()
        self._hass = hass
        self._protect = protect
        self._entry = entry
        self._hass = hass
        self._update_interval = update_interval
        self._subscriptions = {}
        self._unsub_interval = None
        self._unsub_websocket = None

        self.last_update_success = False

    def get_by_types(
        self, device_types: Iterable[ModelType]
    ) -> Generator[ProtectAdoptableDeviceModel, None, None]:
        """Get all devices matching types."""

        for device_type in device_types:
            attr = f"{device_type.value}s"
            devices: dict[str, ProtectAdoptableDeviceModel] = getattr(
                self._protect.bootstrap, attr
            )
            for device in devices.values():
                yield device

    async def async_setup(self):
        """Subscribe and do the refresh."""
        self._unsub_websocket = self._protect.subscribe_websocket(
            self._async_process_ws_message
        )
        await self.async_refresh()

    async def async_stop(self, *args):
        """Stop processing data."""
        if self._unsub_websocket:
            self._unsub_websocket()
            self._unsub_websocket = None
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None
        await self._protect.async_disconnect_ws()

    async def async_refresh(self, *_, force=False):
        """Update the data."""
        try:
            self._async_process_updates(await self._protect.update(force=force))
            self.last_update_success = True
        except NvrError:
            if self.last_update_success:
                _LOGGER.exception("Error while updating")
            self.last_update_success = False
        except NotAuthorized:
            await self.async_stop()
            _LOGGER.exception("Reauthentication required")
            self._entry.async_start_reauth(self._hass)
            self.last_update_success = False

    @callback
    def _async_process_ws_message(self, message: WSSubscriptionMessage):
        if message.new_obj.model in DEVICES_WITH_ENTITIES:
            self.async_signal_device_id_update(message.new_obj.id)
        # trigger updates for camera that the event references
        elif isinstance(message.new_obj, Event) and message.new_obj.camera is not None:
            self.async_signal_device_id_update(message.new_obj.camera.id)
        # trigger update for all viewports when a liveview updates
        elif isinstance(message.new_obj, Liveview):
            for viewer in self._protect.bootstrap.viewers.values():
                self.async_signal_device_id_update(viewer.id)
        # trigger update for all Cameras with LCD screens when NVR Doorbell settings updates
        elif (
            isinstance(message.new_obj, NVR)
            and "doorbell_settings" in message.changed_data
        ):
            self._protect.bootstrap.nvr.update_all_messages()
            for camera in self._protect.bootstrap.cameras.values():
                if camera.feature_flags.has_lcd_screen:
                    self.async_signal_device_id_update(camera.id)

    @callback
    def _async_process_updates(self, updates: Bootstrap | None):
        """Process update from the protect data."""

        # Websocket connected, use data from it
        if updates is None:
            return

        for device_type in DEVICES_WITH_ENTITIES:
            attr = f"{device_type.value}s"
            devices: dict[str, ProtectAdoptableDeviceModel] = getattr(
                self._protect.bootstrap, attr
            )
            for device_id in devices.keys():
                self.async_signal_device_id_update(device_id)

    @callback
    def async_subscribe_device_id(self, device_id, update_callback):
        """Add an callback subscriber."""
        if not self._subscriptions:
            self._unsub_interval = async_track_time_interval(
                self._hass, self.async_refresh, self._update_interval
            )
        self._subscriptions.setdefault(device_id, []).append(update_callback)

        def _unsubscribe():
            self.async_unsubscribe_device_id(device_id, update_callback)

        return _unsubscribe

    @callback
    def async_unsubscribe_device_id(self, device_id, update_callback):
        """Remove a callback subscriber."""
        self._subscriptions[device_id].remove(update_callback)
        if not self._subscriptions[device_id]:
            del self._subscriptions[device_id]
        if not self._subscriptions:
            self._unsub_interval()
            self._unsub_interval = None

    @callback
    def async_signal_device_id_update(self, device_id):
        """Call the callbacks for a device_id."""
        if not self._subscriptions.get(device_id):
            return

        for update_callback in self._subscriptions[device_id]:
            update_callback()
