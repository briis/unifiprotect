"""Support for Ubiquiti's Unifi Protect NVR."""
import logging
import asyncio
from datetime import timedelta

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.const import ATTR_ATTRIBUTION
from . import (
    UPV_DATA,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    ATTR_CAMERA_ID,
    ATTR_UP_SINCE,
    ATTR_LAST_MOTION,
    ATTR_ONLINE,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

DEPENDENCIES = ["unifiprotect"]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Discover cameras on a Unifi Protect NVR."""

    upv_object = hass.data[UPV_DATA]
    if not upv_object:
        return

    cameras = [camera for camera in upv_object.devices]

    async_add_entities(
        [UnifiVideoCamera(hass, upv_object, camera) for camera in cameras]
    )

    return True


class UnifiVideoCamera(Camera):
    """A Ubiquiti Unifi Video Camera."""

    def __init__(self, hass, upv_object, camera):
        """Initialize an Unifi camera."""
        super().__init__()
        self.hass = hass
        self.upv_object = upv_object
        self._camera_id = camera
        self._camera = self.upv_object.devices[camera]

        self._name = self._camera["name"]
        self._model = self._camera["type"]
        self._up_since = self._camera["up_since"]
        self._last_motion = self._camera["last_motion"]
        self._online = self._camera["online"]
        self._motion_status = self._camera["recording_mode"]
        self._stream_source = self._camera["rtsp"]
        self._thumbnail = self._camera["motion_thumbnail"]
        self._isrecording = False
        self._camera = None
        self._last_image = None
        self._supported_features = SUPPORT_STREAM if self._stream_source else 0

        if self._motion_status != "never" and self._online:
            self._isrecording = True

        _LOGGER.debug("Camera %s added to Home Assistant", self._name)

    @property
    def should_poll(self):
        """Poll Cameras to update attributes."""
        return True

    @property
    def supported_features(self):
        """Return supported features for this camera."""
        return self._supported_features

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._camera_id

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    @property
    def motion_detection_enabled(self):
        """Camera Motion Detection Status."""
        return self._motion_status

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
        return self._isrecording

    @property
    def device_state_attributes(self):
        """Add additional Attributes to Camera."""
        attrs = {}
        attrs[ATTR_ATTRIBUTION] = DEFAULT_ATTRIBUTION
        attrs[ATTR_UP_SINCE] = self._up_since
        attrs[ATTR_LAST_MOTION] = self._last_motion
        attrs[ATTR_ONLINE] = self._online
        attrs[ATTR_CAMERA_ID] = self._camera_id

        return attrs

    def update(self):
        """ Updates Attribute States."""
        data = self.upv_object.devices
        camera = data[self._camera_id]

        self._online = camera["online"]
        self._up_since = camera["up_since"]
        self._last_motion = camera["last_motion"]
        self._motion_status = camera["recording_mode"]
        if self._motion_status != "never" and self._online:
            self._isrecording = True
        else:
            self._isrecording = False
        # self._thumbnail = camera["motion_thumbnail"]

    def enable_motion_detection(self):
        """Enable motion detection in camera."""
        ret = self.upv_object.set_camera_recording(self._camera_id, "motion")
        if not ret:
            return

        self._motion_status = "motion"
        self._isrecording = True
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    def disable_motion_detection(self):
        """Disable motion detection in camera."""
        ret = self.upv_object.set_camera_recording(self._camera_id, "never")
        if not ret:
            return

        self._motion_status = "never"
        self._isrecording = False
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    def camera_image(self):
        """Return bytes of camera image."""
        return asyncio.run_coroutine_threadsafe(
            self.async_camera_image(), self.hass.loop
        ).result()

    async def async_camera_image(self):
        """ Return the Camera Image. """
        last_image = self.upv_object.get_snapshot_image(self._camera_id)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """ Return the Stream Source. """
        return self._stream_source
