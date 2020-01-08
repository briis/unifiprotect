"""Unifi Protect Platform."""
import logging
import voluptuous as vol
import requests
from . import protectnvr as nvr

from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_HOST,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_FILENAME,
    ATTR_ENTITY_ID,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity

__version__ = "0.0.10"

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by Unifi Protect NVR"
DATA_UFP = "data_ufp"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_THUMB_WIDTH = "640"
CONF_IMAGE_WIDTH = "image_width"

SERVICE_SAVE_THUMBNAIL = "save_thumbnail_image"

DOMAIN = "unifiprotect"
DEFAULT_PASSWORD = "ubnt"
DEFAULT_PORT = 7443
DEFAULT_SSL = False

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Optional(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_SSL, default=DEFAULT_SSL): cv.boolean,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

SAVE_THUMBNAIL_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_FILENAME): cv.string,
        vol.Optional(CONF_IMAGE_WIDTH, default=DEFAULT_THUMB_WIDTH): cv.string,
    }
)


def setup(hass, config):
    """Set up the Unifi Protect component."""
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    port = conf.get(CONF_PORT)
    use_ssl = conf.get(CONF_SSL)

    try:
        nvrobject = nvr.ProtectServer(host, port, username, password, use_ssl)
        hass.data[DATA_UFP] = nvrobject
        _LOGGER.debug("Connected to Unifi Protect Platform")

    except nvr.NotAuthorized:
        _LOGGER.error("Authorization failure while connecting to NVR")
        return False
    except nvr.NvrError as ex:
        _LOGGER.error("NVR refuses to talk to me: %s", str(ex))
        raise PlatformNotReady
    except requests.exceptions.ConnectionError as ex:
        _LOGGER.error("Unable to connect to NVR: %s", str(ex))
        raise PlatformNotReady

    async def async_save_thumbnail(call):
        """Call save video service handler."""
        await async_handle_save_thumbnail_service(hass, call)

    hass.services.register(
        DOMAIN,
        SERVICE_SAVE_THUMBNAIL,
        async_save_thumbnail,
        schema=SAVE_THUMBNAIL_SCHEMA,
    )

    return True


async def async_handle_save_thumbnail_service(hass, call):
    """Handle save thumbnail service calls."""
    # Get the Camera ID from Entity_id
    entity_id = call.data[ATTR_ENTITY_ID]
    entity_state = hass.states.get(entity_id[0])
    camera_uuid = entity_state.attributes["uuid"]
    if camera_uuid is None:
        _LOGGER.error("Unable to get Camera ID for selected Camera")
        return

    # Get other input from the service call
    filename = call.data[CONF_FILENAME]
    image_width = call.data[CONF_IMAGE_WIDTH]

    if not hass.config.is_allowed_path(filename):
        _LOGGER.error("Can't write %s, no access to path!", filename)
        return

    def _write_thumbnail(camera_id, filename, image_width):
        """Call thumbnail write."""
        image_data = hass.data[DATA_UFP].get_thumbnail(camera_id, image_width)
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
        await hass.async_add_executor_job(
            _write_thumbnail, camera_uuid, filename, image_width
        )
    except OSError as err:
        _LOGGER.error("Can't write image to file: %s", err)

