"""Base class for protect data."""
from __future__ import annotations

import collections
from datetime import timedelta
import logging
from typing import Any, Generator, Iterable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from pyunifiprotect import NotAuthorized, NvrError, ProtectApiClient
from pyunifiprotect.data import (
    Bootstrap,
    Event,
    Liveview,
    ModelType,
    WSSubscriptionMessage,
)
from pyunifiprotect.data.base import ProtectAdoptableDeviceModel, ProtectDeviceModel

from .const import CONF_DISABLE_RTSP, DEVICES_THAT_ADOPT, DEVICES_WITH_ENTITIES

_LOGGER = logging.getLogger(__name__)


class ProtectData:
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
        self._entry = entry
        self._hass = hass
        self._update_interval = update_interval
        self._subscriptions: dict[str, list[CALLBACK_TYPE]] = {}
        self._unsub_interval: CALLBACK_TYPE | None = None
        self._unsub_websocket: CALLBACK_TYPE | None = None

        self.last_update_success = False
        self.access_tokens: dict[str, collections.deque] = {}
        self.api = protect

    @property
    def disable_stream(self) -> bool:
        return self._entry.options.get(CONF_DISABLE_RTSP, False)

    def get_by_types(
        self, device_types: Iterable[ModelType]
    ) -> Generator[ProtectAdoptableDeviceModel, None, None]:
        """Get all devices matching types."""

        for device_type in device_types:
            attr = f"{device_type.value}s"
            devices: dict[str, ProtectAdoptableDeviceModel] = getattr(
                self.api.bootstrap, attr
            )
            for device in devices.values():
                yield device

    async def async_setup(self) -> None:
        """Subscribe and do the refresh."""
        self._unsub_websocket = self.api.subscribe_websocket(
            self._async_process_ws_message
        )
        await self.async_refresh()

    async def async_stop(self, *args: Any) -> None:
        """Stop processing data."""
        if self._unsub_websocket:
            self._unsub_websocket()
            self._unsub_websocket = None
        if self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None
        await self.api.async_disconnect_ws()

    async def async_refresh(self, *_: Any, force: bool = False) -> None:
        """Update the data."""
        try:
            self._async_process_updates(await self.api.update(force=force))
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
    def _async_process_ws_message(self, message: WSSubscriptionMessage) -> None:
        if message.new_obj.model in DEVICES_WITH_ENTITIES:
            self.async_signal_device_id_update(message.new_obj.id)
            # trigger update for all Cameras with LCD screens when NVR Doorbell settings updates
            if "doorbell_settings" in message.changed_data:
                _LOGGER.error(
                    "Doorbell settings updated. Restart Home Assistant to update Viewport select options"
                )
        # trigger updates for camera that the event references
        elif isinstance(message.new_obj, Event) and message.new_obj.camera is not None:
            self.async_signal_device_id_update(message.new_obj.camera.id)
        # trigger update for all viewports when a liveview updates
        elif len(self.api.bootstrap.viewers) > 0 and isinstance(
            message.new_obj, Liveview
        ):
            _LOGGER.error(
                "Liveviews updated. Restart Home Assistant to update Viewport select options"
            )

    @callback
    def _async_process_updates(self, updates: Bootstrap | None) -> None:
        """Process update from the protect data."""

        # Websocket connected, use data from it
        if updates is None:
            return

        self.async_signal_device_id_update(self.api.bootstrap.nvr.id)
        for device_type in DEVICES_THAT_ADOPT:
            attr = f"{device_type.value}s"
            devices: dict[str, ProtectDeviceModel] = getattr(self.api.bootstrap, attr)
            for device_id in devices.keys():
                self.async_signal_device_id_update(device_id)

    @callback
    def async_subscribe_device_id(
        self, device_id: str, update_callback: CALLBACK_TYPE
    ) -> CALLBACK_TYPE:
        """Add an callback subscriber."""
        if not self._subscriptions:
            self._unsub_interval = async_track_time_interval(
                self._hass, self.async_refresh, self._update_interval
            )
        self._subscriptions.setdefault(device_id, []).append(update_callback)

        def _unsubscribe() -> None:
            self.async_unsubscribe_device_id(device_id, update_callback)

        return _unsubscribe

    @callback
    def async_unsubscribe_device_id(
        self, device_id: str, update_callback: CALLBACK_TYPE
    ) -> None:
        """Remove a callback subscriber."""
        self._subscriptions[device_id].remove(update_callback)
        if not self._subscriptions[device_id]:
            del self._subscriptions[device_id]
        if not self._subscriptions and self._unsub_interval:
            self._unsub_interval()
            self._unsub_interval = None

    @callback
    def async_signal_device_id_update(self, device_id: str) -> None:
        """Call the callbacks for a device_id."""
        if not self._subscriptions.get(device_id):
            return

        for update_callback in self._subscriptions[device_id]:
            update_callback()

    @callback
    def async_get_or_create_access_tokens(self, entity_id: str) -> collections.deque:
        """Wrapper around access_tokens to automatically create underlaying data structure if missing."""
        if entity_id not in self.access_tokens:
            self.access_tokens[entity_id] = collections.deque([], 2)
        return self.access_tokens[entity_id]
