"""Support for Ubiquiti's Unifi Protect NVR."""
import logging
from datetime import timedelta

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_LAST_TRIP_TIME,
    CONF_ID,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.util import slugify
import homeassistant.helpers.device_registry as dr

from .const import (
    ATTR_CAMERA_ID,
    ATTR_UP_SINCE,
    ATTR_ONLINE,
    DOMAIN,
    DEFAULT_ATTRIBUTION,
    DEFAULT_BRAND,
    DEVICE_CLASS_DOORBELL,
    ENTITY_ID_CAMERA_FORMAT,
    ENTITY_UNIQUE_ID,
    DEFAULT_BRAND,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)


async def async_setup_entry(
    hass: HomeAssistantType, entry: ConfigEntry, async_add_entities
) -> None:
    """Discover cameras on a Unifi Protect NVR."""
    upv_object = hass.data[DOMAIN][entry.data[CONF_ID]]["upv"]
    coordinator = hass.data[DOMAIN][entry.data[CONF_ID]]["coordinator"]
    if not coordinator.data:
        return

    cameras = [camera for camera in coordinator.data]

    async_add_entities(
        [
            UnifiProtectCamera(upv_object, coordinator, camera, entry.data[CONF_ID])
            for camera in cameras
        ]
    )

    return True


class UnifiProtectCamera(Camera):
    """A Ubiquiti Unifi Protect Camera."""

    def __init__(self, upv_object, coordinator, camera, instance):
        """Initialize an Unifi camera."""
        super().__init__()
        self.upv_object = upv_object
        self.coordinator = coordinator
        self._camera_id = camera
        self._camera = coordinator.data[camera]

        self._name = self._camera["name"]
        self._mac = self._camera["mac"]
        self._firmware_version = self._camera["firmware_version"]
        self._server_id = self._camera["server_id"]
        self._device_type = self._camera["type"]
        self._model = self._camera["model"]
        self._up_since = self._camera["up_since"]
        self._last_motion = self._camera["last_motion"]
        self._last_ring = self._camera["last_ring"]
        self._online = self._camera["online"]
        self._motion_status = self._camera["recording_mode"]
        self._stream_source = self._camera["rtsp"]
        self._thumbnail = self._camera["event_thumbnail"]
        self._isrecording = False
        self._camera = None
        self._last_image = None
        self._supported_features = SUPPORT_STREAM if self._stream_source else 0
        self.entity_id = ENTITY_ID_CAMERA_FORMAT.format(
            slugify(instance), slugify(self._name).replace(" ", "_")
        )
        self._unique_id = ENTITY_UNIQUE_ID.format(camera, self._mac)

        if self._motion_status != "never" and self._online:
            self._isrecording = True

        _LOGGER.debug(f"UNIFIPROTECT CAMERA CREATED: {self._name}")

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
        return self._unique_id

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
        return {
            ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION,
            ATTR_UP_SINCE: self._up_since,
            ATTR_ONLINE: self._online,
            ATTR_CAMERA_ID: self._camera_id,
            ATTR_LAST_TRIP_TIME: self._last_ring
            if self._device_type == DEVICE_CLASS_DOORBELL
            else self._last_motion,
        }

    @property
    def device_info(self):
        return {
            "connections": {(dr.CONNECTION_NETWORK_MAC, self._mac)},
            "name": self.name,
            "manufacturer": DEFAULT_BRAND,
            "model": self._device_type,
            "sw_version": self._firmware_version,
            "via_device": (DOMAIN, self._server_id),
        }

    def update(self):
        """ Updates Attribute States."""
        data = self.coordinator.data
        camera = data[self._camera_id]

        self._online = camera["online"]
        self._up_since = camera["up_since"]
        self._last_motion = camera["last_motion"]
        self._last_ring = camera["last_ring"]
        self._motion_status = camera["recording_mode"]
        if self._motion_status != "never" and self._online:
            self._isrecording = True
        else:
            self._isrecording = False

    async def async_enable_motion_detection(self):
        """Enable motion detection in camera."""
        ret = await self.upv_object.set_camera_recording(self._camera_id, "motion")
        if not ret:
            return

        self._motion_status = "motion"
        self._isrecording = True
        _LOGGER.debug("Motion Detection Enabled for Camera: %s", self._name)

    async def async_disable_motion_detection(self):
        """Disable motion detection in camera."""
        ret = await self.upv_object.set_camera_recording(self._camera_id, "never")
        if not ret:
            return

        self._motion_status = "never"
        self._isrecording = False
        _LOGGER.debug("Motion Detection Disabled for Camera: %s", self._name)

    async def async_camera_image(self):
        """ Return the Camera Image. """
        last_image = await self.upv_object.get_snapshot_image(self._camera_id)
        self._last_image = last_image
        return self._last_image

    async def stream_source(self):
        """ Return the Stream Source. """
        return self._stream_source

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
