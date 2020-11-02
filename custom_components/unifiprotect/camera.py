"""Support for Ubiquiti's Unifi Protect NVR."""
import logging

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, ATTR_LAST_TRIP_TIME
from homeassistant.helpers import entity_platform
from homeassistant.helpers.typing import HomeAssistantType

from .const import (
    ATTR_CAMERA_ID,
    ATTR_ONLINE,
    ATTR_UP_SINCE,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEVICE_TYPE_DOORBELL,
    DOMAIN,
    SAVE_THUMBNAIL_SCHEMA,
    SERVICE_SAVE_THUMBNAIL,
    SERVICE_SET_DOORBELL_LCD_MESSAGE,
    SERVICE_SET_HDR_MODE,
    SERVICE_SET_HIGHFPS_VIDEO_MODE,
    SERVICE_SET_IR_MODE,
    SERVICE_SET_RECORDING_MODE,
    SERVICE_SET_STATUS_LIGHT,
    SET_DOORBELL_LCD_MESSAGE_SCHEMA,
    SET_HDR_MODE_SCHEMA,
    SET_HIGHFPS_VIDEO_MODE_SCHEMA,
    SET_IR_MODE_SCHEMA,
    SET_RECORDING_MODE_SCHEMA,
    SET_STATUS_LIGHT_SCHEMA,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Discover cameras on a Unifi Protect NVR."""
    entry_data = hass.data[DOMAIN][entry.entry_id]
    upv_object = entry_data["upv"]
    protect_data = entry_data["protect_data"]
    snapshot_direct = entry_data["snapshot_direct"]
    if not protect_data.data:
        return

    async_add_entities(
        [
            UnifiProtectCamera(upv_object, protect_data, camera_id, snapshot_direct)
            for camera_id in protect_data.data
        ]
    )

    platform = entity_platform.current_platform.get()

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
        SERVICE_SAVE_THUMBNAIL, SAVE_THUMBNAIL_SCHEMA, "async_save_thumbnail"
    )

    return True


class UnifiProtectCamera(UnifiProtectEntity, Camera):
    """A Ubiquiti Unifi Protect Camera."""

    def __init__(self, upv_object, protect_data, camera_id, snapshot_direct):
        """Initialize an Unifi camera."""
        super().__init__(upv_object, protect_data, camera_id, None)
        self._snapshot_direct = snapshot_direct
        self._name = self._camera_data["name"]
        self._stream_source = self._camera_data["rtsp"]
        self._last_image = None
        self._supported_features = SUPPORT_STREAM if self._stream_source else 0

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def supported_features(self):
        """Return supported features for this camera."""
        return self._supported_features

    @property
    def motion_detection_enabled(self):
        """Camera Motion Detection Status."""
        return self._camera_data["recording_mode"]

    @property
    def brand(self):
        """Return the Cameras Brand."""
        return DEFAULT_BRAND

    @property
    def model(self):
        """Return the camera model."""
        return self._model

    @property
    def is_recording(self):
        """Return true if the device is recording."""
        return (
            True
            if self._camera_data["recording_mode"] != "never"
            and self._camera_data["online"]
            else False
        )

    @property
    def device_state_attributes(self):
        """Add additional Attributes to Camera."""
        if self._device_type == DEVICE_TYPE_DOORBELL:
            last_trip_time = self._camera_data["last_ring"]
        else:
            last_trip_time = self._camera_data["last_motion"]

        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_UP_SINCE: self._camera_data["up_since"],
            ATTR_ONLINE: self._camera_data["online"],
            ATTR_CAMERA_ID: self._camera_id,
            ATTR_LAST_TRIP_TIME: last_trip_time,
        }

    async def async_set_recording_mode(self, recording_mode):
        """Set Camera Recording Mode."""
        await self.upv_object.set_camera_recording(self._camera_id, recording_mode)

    async def async_save_thumbnail(self, filename, image_width):
        """Save Thumbnail Image."""

        if not self.hass.config.is_allowed_path(filename):
            _LOGGER.error("Can't write %s, no access to path!", filename)
            return

        image = await self.upv_object.get_thumbnail(self._camera_id, image_width)
        if image is None:
            _LOGGER.error("Last recording not found for Camera %s", self.name)
            return

        try:
            await self.hass.async_add_executor_job(_write_image, filename, image)
        except OSError as err:
            _LOGGER.error("Can't write image to file: %s", err)

    async def async_set_ir_mode(self, ir_mode):
        """Set camera ir mode."""
        await self.upv_object.set_camera_ir(self._camera_id, ir_mode)

    async def async_set_status_light(self, light_on):
        """Set camera Status Light."""
        await self.upv_object.set_camera_status_light(self._camera_id, light_on)

    async def async_set_hdr_mode(self, hdr_on):
        """Set camera HDR mode."""
        await self.upv_object.set_camera_hdr_mode(self._camera_id, hdr_on)

    async def async_set_highfps_video_mode(self, high_fps_on):
        """Set camera High FPS video mode."""
        await self.upv_object.set_camera_video_mode_highfps(
            self._camera_id, high_fps_on
        )

    async def async_set_doorbell_lcd_message(self, message, duration):
        """Set LCD Message on Doorbell display."""
        if not duration.isnumeric():
            duration = None
        await self.upv_object.set_doorbell_custom_text(
            self._camera_id, message, duration
        )

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        if not await self.upv_object.set_camera_recording(self._camera_id, "motion"):
            return
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    async def async_disable_motion_detection(self):
        """Disable motion detection in camera."""
        if not await self.upv_object.set_camera_recording(self._camera_id, "never"):
            return
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    async def async_camera_image(self):
        """Return the Camera Image."""
        if self._snapshot_direct:
            last_image = await self.upv_object.get_snapshot_image_direct(
                self._camera_id
            )
        else:
            last_image = await self.upv_object.get_snapshot_image(self._camera_id)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """Return the Stream Source."""
        return self._stream_source


def _write_image(to_file, image_data):
    """Executor helper to write image."""
    with open(to_file, "wb") as img_file:
        img_file.write(image_data)
        _LOGGER.debug("Thumbnail Image written to %s", to_file)
