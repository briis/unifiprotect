"""Support for Ubiquiti's Unifi Protect NVR."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    DEVICE_CLASS_SPEAKER,
    MediaPlayerEntity,
    MediaPlayerEntityDescription,
)
from homeassistant.components.media_player.const import (
    MEDIA_TYPE_MUSIC,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_STOP,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_STEP,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_IDLE, STATE_PLAYING
from homeassistant.core import HomeAssistant, callback
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.data import Camera

from custom_components.unifiprotect.data import UnifiProtectData

from .const import DOMAIN
from .entity import UnifiProtectEntity
from .models import UnifiProtectEntryData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    """Discover cameras with speakers on a Unifi Protect NVR."""
    entry_data: UnifiProtectEntryData = hass.data[DOMAIN][entry.entry_id]
    protect = entry_data.protect
    protect_data = entry_data.protect_data

    async_add_entities(
        [
            UnifiProtectMediaPlayer(
                protect,
                protect_data,
                camera,
            )
            for camera in protect.bootstrap.cameras.values()
            if camera.feature_flags.has_speaker
        ]
    )


class UnifiProtectMediaPlayer(UnifiProtectEntity, MediaPlayerEntity):
    """A Ubiquiti UniFi Protect Speaker."""

    def __init__(
        self,
        protect: ProtectApiClient,
        protect_data: UnifiProtectData,
        camera: Camera,
    ):
        """Initialize an UniFi speaker."""

        description = MediaPlayerEntityDescription(
            key="speaker", device_class=DEVICE_CLASS_SPEAKER
        )
        super().__init__(protect, protect_data, camera, description)

        self.device: Camera = camera
        self._attr_name = f"{self.device.name} Speaker"
        self._attr_supported_features = (
            SUPPORT_PLAY_MEDIA
            | SUPPORT_VOLUME_SET
            | SUPPORT_VOLUME_STEP
            | SUPPORT_STOP
            | SUPPORT_SELECT_SOURCE
        )
        self._attr_media_content_type = MEDIA_TYPE_MUSIC
        self._async_update_device_from_protect()

    @callback
    def _async_update_device_from_protect(self):
        super()._async_update_device_from_protect()
        self._attr_volume_level = float(self.device.speaker_settings.volume / 100)

        if (
            self.device.talkback_stream is not None
            and self.device.talkback_stream.is_running
        ):
            self._attr_state = STATE_PLAYING
        else:
            self._attr_state = STATE_IDLE

    @callback
    async def async_set_volume_level(self, volume: float):
        """Set volume level, range 0..1."""

        volume_int = int(volume * 100)
        await self.device.set_speaker_volume(volume_int)

    def media_stop(self):
        """Send stop command."""

        if (
            self.device.talkback_stream is not None
            and self.device.talkback_stream.is_running
        ):
            _LOGGER.debug("Stopping playback for %s Speaker", self.device.name)
            self.device.talkback_stream.stop()

    async def async_play_media(self, media_type: str, media_id: str, **kwargs):
        """Play a piece of media."""

        if media_type != MEDIA_TYPE_MUSIC:
            return

        _LOGGER.debug("Playing Media %s for %s Speaker", media_id, self.device.name)
        self.media_stop()
        self._attr_state = STATE_PLAYING
        try:
            await self.device.play_audio(media_id)
        finally:
            self._async_updated_event()
