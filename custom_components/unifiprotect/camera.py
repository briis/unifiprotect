"""Support for Ubiquiti's UniFi Protect NVR."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any, Callable, Generator, Sequence

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import Entity
from pyunifiprotect.api import ProtectApiClient
from pyunifiprotect.data import Camera as UFPCamera
from pyunifiprotect.data.devices import CameraChannel
from pyunifiprotect.data.types import (
    DoorbellMessageType,
    IRLEDMode,
    RecordingMode,
    VideoMode,
)
from pyunifiprotect.utils import utc_now

from .const import (
    ATTR_BITRATE,
    ATTR_CAMERA_ID,
    ATTR_CHANNEL_ID,
    ATTR_CHIME_DURATION,
    ATTR_CHIME_ENABLED,
    ATTR_FPS,
    ATTR_HEIGHT,
    ATTR_IS_DARK,
    ATTR_MIC_SENSITIVITY,
    ATTR_PRIVACY_MODE,
    ATTR_UP_SINCE,
    ATTR_WDR_VALUE,
    ATTR_WIDTH,
    ATTR_ZOOM_POSITION,
    DOMAIN,
    SERVICE_SET_DOORBELL_CHIME_DURAION,
    SERVICE_SET_DOORBELL_LCD_MESSAGE,
    SERVICE_SET_HDR_MODE,
    SERVICE_SET_HIGHFPS_VIDEO_MODE,
    SERVICE_SET_IR_MODE,
    SERVICE_SET_MIC_VOLUME,
    SERVICE_SET_PRIVACY_MODE,
    SERVICE_SET_RECORDING_MODE,
    SERVICE_SET_STATUS_LIGHT,
    SERVICE_SET_WDR_VALUE,
    SERVICE_SET_ZOOM_POSITION,
    SET_DOORBELL_CHIME_DURATION_SCHEMA,
    SET_DOORBELL_LCD_MESSAGE_SCHEMA,
    SET_HDR_MODE_SCHEMA,
    SET_HIGHFPS_VIDEO_MODE_SCHEMA,
    SET_IR_MODE_SCHEMA,
    SET_MIC_VOLUME_SCHEMA,
    SET_PRIVACY_MODE_SCHEMA,
    SET_RECORDING_MODE_SCHEMA,
    SET_STATUS_LIGHT_SCHEMA,
    SET_WDR_VALUE_SCHEMA,
    SET_ZOOM_POSITION_SCHEMA,
    TYPE_RECORD_NOTSET,
)
from .data import ProtectData
from .entity import ProtectDeviceEntity

_LOGGER = logging.getLogger(__name__)


def get_camera_channels(
    protect: ProtectApiClient,
) -> Generator[tuple[UFPCamera, CameraChannel, bool], None, None]:
    """Get all the camera channels."""
    for camera in protect.bootstrap.cameras.values():
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

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_SET_RECORDING_MODE,
        SET_RECORDING_MODE_SCHEMA,
        "async_set_recording_mode",
    )

    platform.async_register_entity_service(
        SERVICE_SET_IR_MODE, SET_IR_MODE_SCHEMA, "async_set_ir_mode"
    )

    platform.async_register_entity_service(
        SERVICE_SET_STATUS_LIGHT, SET_STATUS_LIGHT_SCHEMA, "async_set_status_light"
    )

    platform.async_register_entity_service(
        SERVICE_SET_HDR_MODE, SET_HDR_MODE_SCHEMA, "async_set_hdr_mode"
    )

    platform.async_register_entity_service(
        SERVICE_SET_HIGHFPS_VIDEO_MODE,
        SET_HIGHFPS_VIDEO_MODE_SCHEMA,
        "async_set_highfps_video_mode",
    )

    platform.async_register_entity_service(
        SERVICE_SET_DOORBELL_LCD_MESSAGE,
        SET_DOORBELL_LCD_MESSAGE_SCHEMA,
        "async_set_doorbell_lcd_message",
    )

    platform.async_register_entity_service(
        SERVICE_SET_MIC_VOLUME, SET_MIC_VOLUME_SCHEMA, "async_set_mic_volume"
    )

    platform.async_register_entity_service(
        SERVICE_SET_PRIVACY_MODE, SET_PRIVACY_MODE_SCHEMA, "async_set_privacy_mode"
    )

    platform.async_register_entity_service(
        SERVICE_SET_ZOOM_POSITION, SET_ZOOM_POSITION_SCHEMA, "async_set_zoom_position"
    )

    platform.async_register_entity_service(
        SERVICE_SET_WDR_VALUE, SET_WDR_VALUE_SCHEMA, "async_set_wdr_value"
    )

    platform.async_register_entity_service(
        SERVICE_SET_DOORBELL_CHIME_DURAION,
        SET_DOORBELL_CHIME_DURATION_SCHEMA,
        "async_set_doorbell_chime_duration",
    )


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
            ATTR_UP_SINCE: self.device.up_since,
            ATTR_CAMERA_ID: self.device.id,
            ATTR_CHIME_ENABLED: self.device.feature_flags.has_chime,
            ATTR_CHIME_DURATION: self.device.chime_duration,
            ATTR_IS_DARK: self.device.is_dark,
            ATTR_MIC_SENSITIVITY: self.device.mic_volume,
            ATTR_PRIVACY_MODE: self.device.is_privacy_on,
            ATTR_WDR_VALUE: self.device.isp_settings.wdr,
            ATTR_ZOOM_POSITION: self.device.isp_settings.zoom_position,
            ATTR_WIDTH: self.channel.width,
            ATTR_HEIGHT: self.channel.height,
            ATTR_FPS: self.channel.fps,
            ATTR_BITRATE: self.channel.bitrate,
            ATTR_CHANNEL_ID: self.channel.id,
        }

    @property
    def supported_features(self) -> int:
        """Return supported features for this camera.

        CORE: Remove this before merging to core.
        """
        return self._attr_supported_features

    @property
    def motion_detection_enabled(self) -> bool:
        """Camera Motion Detection Status."""
        return self.device.feature_flags.has_motion_zones and super().available

    @property
    def is_recording(self) -> bool:
        """Return true if the device is recording."""
        return self.device.is_connected and self.device.is_recording

    async def async_set_recording_mode(self, recording_mode: str) -> None:
        """Set Camera Recording Mode."""
        await self.device.set_recording_mode(RecordingMode(recording_mode))

    async def async_set_ir_mode(self, ir_mode: str) -> None:
        """Set camera ir mode."""
        await self.device.set_ir_led_model(IRLEDMode(ir_mode))

    async def async_set_status_light(self, light_on: bool) -> None:
        """Set camera Status Light."""
        await self.device.set_status_light(light_on)

    async def async_set_hdr_mode(self, hdr_on: bool) -> None:
        """Set camera HDR mode."""
        await self.device.set_hdr(hdr_on)

    async def async_set_doorbell_chime_duration(self, chime_duration: int) -> None:
        """Set Doorbell Chime duration."""
        await self.device.set_chime_duration(chime_duration)

    async def async_set_highfps_video_mode(self, high_fps_on: bool) -> None:
        """Set camera High FPS video mode."""
        await self.device.set_video_mode(
            VideoMode.HIGH_FPS if high_fps_on else VideoMode.DEFAULT
        )

    async def async_set_doorbell_lcd_message(self, message: str, duration: str) -> None:
        """Set LCD Message on Doorbell display."""

        reset_at = None
        if duration.isnumeric():
            reset_at = utc_now() + timedelta(minutes=int(duration))

        await self.device.set_lcd_text(
            DoorbellMessageType.CUSTOM_MESSAGE, message, reset_at=reset_at
        )

    async def async_set_mic_volume(self, level: int) -> None:
        """Set camera Microphone Level."""
        await self.device.set_mic_volume(level)

    async def async_set_privacy_mode(
        self, privacy_mode: bool, mic_level: int, recording_mode: str
    ) -> None:
        """Set camera Privacy mode."""

        arg_mic_level: None | int = None
        arg_recording_mode: None | RecordingMode = None
        if mic_level >= 0:
            arg_mic_level = mic_level
        if recording_mode != TYPE_RECORD_NOTSET:
            arg_recording_mode = RecordingMode(recording_mode)

        await self.device.set_privacy(
            privacy_mode, mic_level=arg_mic_level, recording_mode=arg_recording_mode
        )

    async def async_set_wdr_value(self, value: int) -> None:
        """Set camera wdr value."""
        await self.device.set_wdr_level(value)

    async def async_set_zoom_position(self, position: int) -> None:
        """Set camera Zoom Position."""
        await self.device.set_camera_zoom(position)

    async def async_enable_motion_detection(self) -> None:
        """Enable motion detection in camera."""
        if not await self.device.set_recording_mode(RecordingMode.DETECTIONS):
            return
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self.device.name)

    async def async_disable_motion_detection(self) -> None:
        """Disable motion detection in camera."""
        if not await self.device.set_recording_mode(RecordingMode.NEVER):
            return
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self.device.name)

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
