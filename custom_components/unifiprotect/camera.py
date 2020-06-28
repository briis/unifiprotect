"""Support for Ubiquiti's Unifi Protect NVR."""
import logging
from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_LAST_TRIP_TIME,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.helpers import entity_platform

from .const import (
    ATTR_CAMERA_ID,
    ATTR_UP_SINCE,
    ATTR_ONLINE,
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEVICE_CLASS_DOORBELL,
    SERVICE_SET_IR_MODE,
    SERVICE_SET_RECORDING_MODE,
    SERVICE_SAVE_THUMBNAIL,
    SET_IR_MODE_SCHEMA,
    SET_RECORDING_MODE_SCHEMA,
    SAVE_THUMBNAIL_SCHEMA,
)
from .entity import UnifiProtectEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Discover cameras on a Unifi Protect NVR."""
    upv_object = hass.data[DOMAIN][entry.entry_id]["upv"]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    snapshot_direct = hass.data[DOMAIN][entry.entry_id]["snapshot_direct"]
    if not coordinator.data:
        return

    cameras = [camera for camera in coordinator.data]

    async_add_entities(
        [
            UnifiProtectCamera(upv_object, coordinator, camera, snapshot_direct)
            for camera in cameras
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
        SERVICE_SAVE_THUMBNAIL, SAVE_THUMBNAIL_SCHEMA, "async_save_thumbnail"
    )

    return True


class UnifiProtectCamera(UnifiProtectEntity, Camera):
    """A Ubiquiti Unifi Protect Camera."""

    def __init__(self, upv_object, coordinator, camera_id, snapshot_direct):
        """Initialize an Unifi camera."""
        super().__init__(upv_object, coordinator, camera_id, None)
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
        """The Cameras Brand."""
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
        if self._device_type == DEVICE_CLASS_DOORBELL:
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

        def _write_image(to_file, image_data):
            """Executor helper to write image."""
            with open(to_file, "wb") as img_file:
                img_file.write(image_data)
                _LOGGER.debug("Thumbnail Image written to %s", filename)

        try:
            await self.hass.async_add_executor_job(_write_image, filename, image)
        except OSError as err:
            _LOGGER.error("Can't write image to file: %s", err)

    async def async_set_ir_mode(self, ir_mode):
        """Set camera ir mode."""
        await self.upv_object.set_camera_ir(self._camera_id, ir_mode)

    async def async_update(self):
        """Update the entity.

        Only used by the generic entity update service.
        """
        await self.coordinator.async_request_refresh()

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        ret = await self.upv_object.set_camera_recording(self._camera_id, "motion")
        if not ret:
            return
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    async def async_disable_motion_detection(self):
        """Disable motion detection in camera."""
        ret = await self.upv_object.set_camera_recording(self._camera_id, "never")
        if not ret:
            return
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    async def async_camera_image(self):
        """ Return the Camera Image. """
        if self._snapshot_direct:
            last_image = await self.upv_object.get_snapshot_image_direct(
                self._camera_id
            )
        else:
            last_image = await self.upv_object.get_snapshot_image(self._camera_id)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """ Return the Stream Source. """
        return self._stream_source
