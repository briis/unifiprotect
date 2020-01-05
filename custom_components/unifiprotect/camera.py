"""Support for Ubiquiti's Unifi Protect NVR."""
import logging
import asyncio
from datetime import timedelta

import requests
import voluptuous as vol

from homeassistant.components.camera import DOMAIN, SUPPORT_STREAM, PLATFORM_SCHEMA, CAMERA_SERVICE_SNAPSHOT, ATTR_FILENAME, Camera
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL, CONF_USERNAME, CONF_PASSWORD, CONF_NAME, CONF_FILENAME, ATTR_ENTITY_ID
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from . import ATTRIBUTION, DOMAIN, DATA_UFP, DEFAULT_BRAND, protectnvr as nvr


_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

DEPENDENCIES = ['unifiprotect']

SERVICE_SAVE_THUMBNAIL = 'save_thumbnail'

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Discover cameras on a Unifi Protect NVR."""
    component = hass.data[DOMAIN] = EntityComponent(
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL
    )

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
            UnifiVideoCamera(hass, nvrobject, camera['id'], camera["name"], camera["rtsp"], camera["recording_mode"], camera["type"], camera['up_since'], camera['last_motion'], camera['online'])
            for camera in cameras
        ]
    )

    component.async_register_entity_service(
        SERVICE_SAVE_THUMBNAIL, CAMERA_SERVICE_SNAPSHOT, save_thumbnail_service
    )


    return True

class UnifiVideoCamera(Camera):
    """A Ubiquiti Unifi Video Camera."""

    def __init__(self, hass, camera, uuid, name, stream_source, recording_mode, model, up_since, last_motion, online):
        """Initialize an Unifi camera."""
        super().__init__()
        self.hass = hass
        self._nvr = camera
        self._uuid = uuid
        self._name = name
        self._model = model
        self._up_since = up_since
        self._last_motion = last_motion
        self._online = online
        self._motion_status = recording_mode
        self._stream_source = stream_source
        self._isrecording = False
        self._camera = None
        self._last_image = None
        self._supported_features = SUPPORT_STREAM if self._stream_source else 0

        if (recording_mode != 'never' and self._online):
            self._isrecording = True

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
        return self._uuid

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
        attrs['uptime'] = self._up_since
        attrs['last_motion'] = self._last_motion
        attrs['online'] = self._online
        
        return attrs

    def update(self):
        """ Updates Attribute States."""

        caminfo = self._nvr.cameras
        for camera in caminfo:
            if (self._uuid == camera['id']):
                self._online = camera['online']
                self._up_since = camera['up_since']
                self._last_motion = camera['last_motion']
                self._motion_status = camera['recording_mode']
                if (self._motion_status != 'never' and self._online):
                    self._isrecording = True
                else:
                    self._isrecording = False
                break

    def enable_motion_detection(self):
        """Enable motion detection in camera."""
        ret = self._nvr.set_camera_recording(self._uuid,'motion')
        if not ret:
            return
        
        self._motion_status = 'motion'
        self._isrecording = True
        _LOGGER.debug("Motion Detection Enabled for Camera: " + self._name)

    def disable_motion_detection(self):
        """Disable motion detection in camera."""
        ret = self._nvr.set_camera_recording(self._uuid,'never')
        if not ret:
            return
        
        self._motion_status = 'never'
        self._isrecording = False
        _LOGGER.debug("Motion Detection Disabled for Camera: " + self._name)

    def camera_image(self):
        """Return bytes of camera image."""
        return asyncio.run_coroutine_threadsafe(
            self.async_camera_image(), self.hass.loop
        ).result()

    def request_thumbnail(self):
        image = self._nvr.get_thumbnail(self._uuid)
        return image

    def async_request_thumbnail(self):
        return self.hass.async_add_job(self.request_thumbnail)

    async def async_camera_image(self):
        """ Return the Camera Image. """
        last_image = self._nvr.get_snapshot_image(self._uuid)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """ Return the Stream Source. """
        return self._stream_source

async def save_thumbnail_service(camera, service):
    _LOGGER.info("{0} thumbnail to file".format(camera.unique_id))

    hass = camera.hass
    filename = service.data[ATTR_FILENAME]
    filename.hass = hass

    snapshot_file = filename.async_render(variables={ATTR_ENTITY_ID: camera})

    # check if we allow to access to that file
    if not hass.config.is_allowed_path(snapshot_file):
        _LOGGER.error("Can't write %s, no access to path!", snapshot_file)
        return

    image = await camera.async_request_thumbnail()
    if image is None:
        _LOGGER.warning("Last recording not found for Camera " + camera.name)
        return False

    def _write_image(to_file, image_data):
        with open(to_file, 'wb') as img_file:
            img_file.write(image_data)

    try:
        await hass.async_add_executor_job(_write_image, snapshot_file, image)
        hass.bus.fire('unifiprotect_thumbnail_ready', {
            'entity_id': 'unifiprotect.' + camera.unique_id,
            'file': snapshot_file
        })
    except OSError as err:
        _LOGGER.error("Can't write image to file: %s", err)
