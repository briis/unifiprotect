"""Support for Ubiquiti's UniFi Protect NVR."""
from __future__ import annotations

import logging
from typing import Any, Callable, Generator, Sequence

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import Entity
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.data import Camera as UFPCamera
from pyunifiprotect.data.devices import CameraChannel

from .const import (
    ATTR_BITRATE,
    ATTR_CHANNEL_ID,
    ATTR_FPS,
    ATTR_HEIGHT,
    ATTR_WIDTH,
    DOMAIN,
)
from .data import ProtectData
from .entity import ProtectDeviceEntity

_LOGGER = logging.getLogger(__name__)


def get_camera_channels(
    protect: ProtectApiClient,
) -> Generator[tuple[UFPCamera, CameraChannel, bool], None, None]:
    """Get all the camera channels."""
    for camera in protect.bootstrap.cameras.values():
        if len(camera.channels) == 0:
            _LOGGER.warning(
                "Camera does not have any channels: %s (id: %s)", camera.name, camera.id
            )
            continue

        is_default = True
        for channel in camera.channels:
            if channel.is_rtsp_enabled:
                yield camera, channel, is_default
                is_default = False

        # no RTSP enabled use first channel with no stream
        if is_default:
            yield camera, camera.channels[0], True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[Sequence[Entity]], None],
) -> None:
    """Discover cameras on a UniFi Protect NVR."""
    data: ProtectData = hass.data[DOMAIN][entry.entry_id]
    disable_stream = data.disable_stream

    items = []
    for camera, channel, is_default in get_camera_channels(data.api):
        if channel.is_rtsp_enabled:
            items.append(
                ProtectCamera(
                    data,
                    camera,
                    channel,
                    is_default,
                    True,
                    disable_stream,
                )
            )
            items.append(
                ProtectCamera(
                    data,
                    camera,
                    channel,
                    is_default,
                    False,
                    disable_stream,
                )
            )
        else:
            items.append(
                ProtectCamera(
                    data,
                    camera,
                    channel,
                    is_default,
                    True,
                    disable_stream,
                )
            )

    async_add_entities(items)


class ProtectCamera(ProtectDeviceEntity, Camera):
    """A Ubiquiti UniFi Protect Camera."""

    def __init__(
        self,
        data: ProtectData,
        camera: UFPCamera,
        channel: CameraChannel,
        is_default: bool,
        secure: bool,
        disable_stream: bool,
    ) -> None:
        """Initialize an UniFi camera."""
        self.device: UFPCamera = camera
        self.channel = channel
        self._secure = secure
        self._disable_stream = disable_stream
        self._last_image: bytes | None = None
        super().__init__(data)

        if self._secure:
            self._attr_unique_id = f"{self.device.id}_{self.channel.id}"
            self._attr_name = f"{self.device.name} {self.channel.name}"
        else:
            self._attr_unique_id = f"{self.device.id}_{self.channel.id}_insecure"
            self._attr_name = f"{self.device.name} {self.channel.name} Insecure"
        # only the default (first) channel is enabled by default
        self._attr_entity_registry_enabled_default = is_default and secure

    @callback
    def _async_set_stream_source(self) -> None:
        disable_stream = self._disable_stream
        if not self.channel.is_rtsp_enabled:
            disable_stream = False

        rtsp_url = self.channel.rtsp_url
        if self._secure:
            rtsp_url = self.channel.rtsps_url

        # _async_set_stream_source called by __init__
        self._stream_source = (  # pylint: disable=attribute-defined-outside-init
            None if disable_stream else rtsp_url
        )
        self._attr_supported_features: int = (
            SUPPORT_STREAM if self._stream_source else 0
        )

    @callback
    def _async_update_device_from_protect(self) -> None:
        super()._async_update_device_from_protect()
        self.channel = self.device.channels[self.channel.id]
        self._async_set_stream_source()

    @callback
    def _async_update_extra_attrs_from_protect(self) -> dict[str, Any]:
        """Add additional Attributes to Camera."""
        return {
            ATTR_WIDTH: self.channel.width,
            ATTR_HEIGHT: self.channel.height,
            ATTR_FPS: self.channel.fps,
            ATTR_BITRATE: self.channel.bitrate,
            ATTR_CHANNEL_ID: self.channel.id,
        }

    @property
    def motion_detection_enabled(self) -> bool:
        """Camera Motion Detection Status."""
        return self.device.feature_flags.has_motion_zones and super().available

    @property
    def is_recording(self) -> bool:
        """Return true if the device is recording."""
        return self.device.is_connected and self.device.is_recording

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return the Camera Image."""
        last_image = await self.device.get_snapshot(width, height)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self) -> str | None:
        """Return the Stream Source."""
        return self._stream_source
