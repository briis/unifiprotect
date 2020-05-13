"""Unifi Protect Platform."""

import logging
from datetime import timedelta

import requests
import voluptuous as vol
from aiohttp import CookieJar

from . import unifi_protect_server as upv

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FILENAME,
    CONF_SCAN_INTERVAL,
    ATTR_ENTITY_ID,
)
import homeassistant.helpers.config_validation as cv
from homeassistant import core
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)

ATTR_CAMERA_ID = "camera_id"
ATTR_UP_SINCE = "up_since"
ATTR_ONLINE = "online"

CONF_THUMB_WIDTH = "image_width"
CONF_MIN_SCORE = "minimum_score"
CONF_RECORDING_MODE = "recording_mode"
CONF_IR_MODE = "ir_mode"

TYPE_RECORD_MOTION = "motion"
TYPE_RECORD_ALLWAYS = "always"
TYPE_RECORD_NEVER = "never"
TYPE_IR_AUTO = "auto"
TYPE_IR_ON = "always_on"
TYPE_IR_LED_OFF = "led_off"
TYPE_IR_OFF = "always_off"

DEFAULT_ATTRIBUTION = "Data provided by Ubiquiti's Unifi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_MIN_SCORE = 0
DEFAULT_PORT = 7443
DEFAULT_RECORDING_MODE = "motion"
DEFAULT_IR_MODE = TYPE_IR_AUTO
DEFAULT_SCAN_INTERVAL = timedelta(seconds=2)
DEFAULT_SSL = False
DEFAULT_THUMB_WIDTH = 640

DEVICE_CLASS_DOORBELL = "doorbell"

DOMAIN = "unifiprotect"
UPV_DATA = DOMAIN

SERVICE_SAVE_THUMBNAIL = "save_thumbnail_image"
SERVICE_SET_RECORDING_MODE = "set_recording_mode"
SERVICE_SET_IR_MODE = "set_ir_mode"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.time_period,
                vol.Optional(CONF_THUMB_WIDTH, default=DEFAULT_THUMB_WIDTH): int,
                vol.Optional(CONF_MIN_SCORE, default=DEFAULT_MIN_SCORE): int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SAVE_THUMBNAIL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_FILENAME): cv.string,
        vol.Optional(CONF_THUMB_WIDTH, default=DEFAULT_THUMB_WIDTH): cv.string,
    }
)

SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=DEFAULT_RECORDING_MODE): cv.string,
    }
)

SET_IR_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_IR_MODE, default=DEFAULT_IR_MODE): cv.string,
    }
)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Unifi Protect component."""
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    port = conf.get(CONF_PORT)
    use_ssl = conf.get(CONF_SSL)
    minimum_score = conf.get(CONF_MIN_SCORE)
    scan_interval = conf[CONF_SCAN_INTERVAL]
    session = async_create_clientsession(hass, cookie_jar=CookieJar(unsafe=True))

    try:
        upv_server = upv.UpvServer(
            session, host, port, username, password, use_ssl, minimum_score
        )
        _LOGGER.debug("Connected to Unifi Protect Platform")
    except upv.NotAuthorized:
        _LOGGER.error("Authorization failure while connecting to NVR")
        return False
    except upv.NvrError as ex:
        _LOGGER.error("NVR refuses to talk to me: %s", str(ex))
        raise PlatformNotReady
    except requests.exceptions.ConnectionError as ex:
        _LOGGER.error("Unable to connect to NVR: %s", str(ex))
        raise PlatformNotReady

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=upv_server.update,
        update_interval=scan_interval,
    )
    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_refresh()
    hass.data[UPV_DATA] = {
        "coordinator": coordinator,
        "upv": upv_server,
    }

    async def async_save_thumbnail(call):
        """Call save video service handler."""
        await async_handle_save_thumbnail_service(hass, call)

    async def async_set_recording_mode(call):
        """Call Set Recording Mode."""
        await async_handle_set_recording_mode(hass, call)

    async def async_set_ir_mode(call):
        """Call Set Infrared Mode."""
        await async_handle_set_ir_mode(hass, call)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SAVE_THUMBNAIL,
        async_save_thumbnail,
        schema=SAVE_THUMBNAIL_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_RECORDING_MODE,
        async_set_recording_mode,
        schema=SET_RECORDING_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, SERVICE_SET_IR_MODE, async_set_ir_mode, schema=SET_IR_MODE_SCHEMA,
    )

    return True


async def async_handle_set_recording_mode(hass, call):
    """Handle setting Recording Mode."""
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    rec_mode = call.data[CONF_RECORDING_MODE].lower()
    if rec_mode not in {"always", "motion", "never"}:
        rec_mode = "motion"

    await hass.data[UPV_DATA]["upv"].set_camera_recording(camera_id, rec_mode)


async def async_handle_set_ir_mode(hass, call):
    """Handle enable Always recording."""
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    ir_mode = call.data[CONF_IR_MODE].lower()
    if ir_mode not in {"always_on", "auto", "always_off", "led_off"}:
        ir_mode = "auto"

    await hass.data[UPV_DATA]["upv"].set_camera_ir(camera_id, ir_mode)


async def async_handle_save_thumbnail_service(hass, call):
    """Handle save thumbnail service calls."""
    # Get the Camera ID from Entity_id
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_id = entity_state.attributes[ATTR_CAMERA_ID]
    if camera_id is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    # Get other input from the service call
    filename = call.data[CONF_FILENAME]
    image_width = call.data[CONF_THUMB_WIDTH]

    if not hass.config.is_allowed_path(filename):
        _LOGGER.error("Can't write %s, no access to path!", filename)
        return

    async def _write_thumbnail(camera_id, filename, image_width):
        """Call thumbnail write."""
        image_data = await hass.data[UPV_DATA]["upv"].get_thumbnail(
            camera_id, image_width
        )
        if image_data is None:
            _LOGGER.warning(
                "Last recording not found for Camera %s",
                entity_state.attributes["friendly_name"],
            )
            return False
        # We got an image, now write the image to disk
        with open(filename, "wb") as img_file:
            img_file.write(image_data)
            _LOGGER.debug("Thumbnail Image written to %s", filename)

    try:
        await _write_thumbnail(camera_id, filename, image_width)
    except OSError as err:
        _LOGGER.error("Can't write image to file: %s", err)
