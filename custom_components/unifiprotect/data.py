"""Base class for protect data."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Generator
from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from pyunifiprotect.exceptions import NotAuthorized
from pyunifiprotect.unifi_protect_server import NvrError, UpvServer

_LOGGER = logging.getLogger(__name__)


@dataclass
class UnifiProtectDevice:
    device_id: str
    type: str
    data: dict


class UnifiProtectData:
    """Coordinate updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        protectserver: UpvServer,
        update_interval: timedelta,
        entry: ConfigEntry,
    ):
        """Initialize an subscriber."""
        super().__init__()
        self._hass = hass
        self._protectserver = protectserver
        self._entry = entry
        self._hass = hass
        self._update_interval = update_interval
        self._subscriptions = {}
        self._unsub_interval = None
        self._unsub_websocket = None

        self.data = {}
        self.last_update_success = False

    def get_by_types(self, device_types) -> Generator[UnifiProtectDevice, None, None]:
        """Get all devices matching types."""
        if not self.data:
            return

        for device_id, device_data in self.data.items():
            device_type = device_data.get("type")
            if device_type and device_type in device_types:
                yield UnifiProtectDevice(device_id, device_type, device_data)

    async def async_setup(self):
        """Subscribe and do the refresh."""
        self._unsub_websocket = self._protectserver.subscribe_websocket(
            self._async_process_updates
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
        await self._protectserver.async_disconnect_ws()

    async def async_refresh(self, *_, force_camera_update=False):
        """Update the data."""
        try:
            self._async_process_updates(
                await self._protectserver.update(
                    force_camera_update=force_camera_update
                )
            )
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
    def _async_process_updates(self, updates):
        """Process update from the protect data."""
        for device_id, data in updates.items():
            self.data[device_id] = data
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
