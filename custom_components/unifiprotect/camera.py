"""Support for Ubiquiti's Unifi Protect NVR."""
import logging
import asyncio

import requests
import voluptuous as vol

from homeassistant.components.camera import SUPPORT_STREAM, PLATFORM_SCHEMA, Camera
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_USERNAME, CONF_PASSWORD
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from . import ATTRIBUTION, DATA_UFP, DEFAULT_BRAND

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['unifiprotect']

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Discover cameras on a Unifi Protect NVR."""

    try:
        # Exceptions may be raised in all method calls to the nvr library.
        nvrobject = hass.data.get(DATA_UFP)
        cameras = nvrobject.cameras

        cameras = [
            camera
            for camera in cameras
        ]
    except nvr.NotAuthorized:
        _LOGGER.error("Authorization failure while connecting to NVR")
        return False
    except nvr.NvrError as ex:
        _LOGGER.error("NVR refuses to talk to me: %s", str(ex))
        raise PlatformNotReady
    except requests.exceptions.ConnectionError as ex:
        _LOGGER.error("Unable to connect to NVR: %s", str(ex))
        raise PlatformNotReady

    async_add_entities(
        [
            UnifiVideoCamera(hass, nvrobject, camera['id'], camera["name"], camera["rtsp"], camera["recording_mode"], camera["type"])
            for camera in cameras
        ]
    )
    return True

class UnifiVideoCamera(Camera):
    """A Ubiquiti Unifi Video Camera."""

    def __init__(self, hass, camera, uuid, name, stream_source, recording_mode, model):
        """Initialize an Unifi camera."""
        super().__init__()
        self.hass = hass
        self._nvr = camera
        self._uuid = uuid
        self._name = name
        self._model = model
        self._motion_status = recording_mode
        self._stream_source = stream_source
        self._isrecording = False
        self._camera = None
        self._last_image = None
        self._supported_features = SUPPORT_STREAM if self._stream_source else 0

        if (recording_mode != 'never'):
            self._isrecording = True

    @property
    def supported_features(self):
        """Return supported features for this camera."""
        return self._supported_features

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
        return "Ubiquiti"

    @property
    def model(self):
        """Return the camera model."""
        return self._model

    @property
    def is_recording(self):
        """Return true if the device is recording."""
        return self._isrecording

    def enable_motion_detection(self):
        """Enable motion detection in camera."""
        ret = self._nvr.set_camera_recording(self._uuid,'motion')
        if not ret:
            return
        
        self._motion_status = 'motion'
        self._isrecording = True

    def disable_motion_detection(self):
        """Disable motion detection in camera."""
        ret = self._nvr.set_camera_recording(self._uuid,'never')
        if not ret:
            return
        
        self._motion_status = 'never'
        self._isrecording = False

    def camera_image(self):
        """Return bytes of camera image."""
        return asyncio.run_coroutine_threadsafe(
            self.async_camera_image(), self.hass.loop
        ).result()

    async def async_camera_image(self):
        """ Return the Camera Image. """
        last_image = self._nvr.get_snapshot_image(self._uuid)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """ Return the Stream Source. """
        return self._stream_source
