"""Constant definitions for UniFi Protect Integration."""

from homeassistant.const import ATTR_ENTITY_ID, CONF_DEVICE_ID
from homeassistant.helpers import config_validation as cv
from pyunifiprotect.data.types import ModelType, Version
import voluptuous as vol

DOMAIN = "unifiprotect"

ATTR_EVENT_SCORE = "event_score"
ATTR_EVENT_OBJECT = "event_object"
ATTR_EVENT_THUMB = "event_thumbnail"
ATTR_WIDTH = "width"
ATTR_HEIGHT = "height"
ATTR_FPS = "fps"
ATTR_BITRATE = "bitrate"
ATTR_CHANNEL_ID = "channel_id"

CONF_DOORBELL_TEXT = "doorbell_text"
CONF_DISABLE_RTSP = "disable_rtsp"
CONF_MESSAGE = "message"
CONF_DURATION = "duration"
CONF_ANONYMIZE = "anonymize"
CONF_ALL_UPDATES = "all_updates"
CONF_OVERRIDE_CHOST = "override_connection_host"

CONFIG_OPTIONS = [
    CONF_ALL_UPDATES,
    CONF_DISABLE_RTSP,
    CONF_OVERRIDE_CHOST,
]

DEFAULT_PORT = 443
DEFAULT_ATTRIBUTION = "Powered by UniFi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_SCAN_INTERVAL = 2
DEFAULT_VERIFY_SSL = False

DEVICE_TYPE_CAMERA = "camera"
DEVICES_THAT_ADOPT = {
    ModelType.CAMERA,
    ModelType.LIGHT,
    ModelType.VIEWPORT,
    ModelType.SENSOR,
}
DEVICES_WITH_ENTITIES = DEVICES_THAT_ADOPT | {ModelType.NVR}
DEVICES_FOR_SUBSCRIBE = DEVICES_WITH_ENTITIES | {ModelType.EVENT}

EVENT_UPDATE_TOKENS = "unifiprotect_update_tokens"

MIN_REQUIRED_PROTECT_V = Version("1.20.0")
OUTDATED_LOG_MESSAGE = "You are running v%s of UniFi Protect. Minimum required version is v%s. Please upgrade UniFi Protect and then retry"

SERVICE_GENERATE_DATA = "take_sample"
SERVICE_PROFILE_WS = "profile_ws_messages"
SERVICE_ADD_DOORBELL_TEXT = "add_doorbell_text"
SERVICE_REMOVE_DOORBELL_TEXT = "remove_doorbell_text"
SERVICE_SET_DEFAULT_DOORBELL_TEXT = "set_default_doorbell_text"
SERVICE_SET_DOORBELL_MESSAGE = "set_doorbell_message"

TYPE_EMPTY_VALUE = ""

PLATFORMS = [
    "camera",
    "binary_sensor",
    "sensor",
    "switch",
    "light",
    "select",
    "number",
    "media_player",
    "button",
]

DOORBELL_TEXT_SCHEMA = vol.All(
    vol.Schema(
        {
            **cv.ENTITY_SERVICE_FIELDS,
            vol.Required(CONF_MESSAGE): cv.string,
        },
    ),
    cv.has_at_least_one_key(CONF_DEVICE_ID),
)

GENERATE_DATA_SCHEMA = vol.All(
    vol.Schema(
        {
            **cv.ENTITY_SERVICE_FIELDS,
            vol.Required(CONF_DURATION): vol.Coerce(int),
            vol.Required(CONF_ANONYMIZE): vol.Coerce(bool),
        },
    ),
    cv.has_at_least_one_key(CONF_DEVICE_ID),
)

PROFILE_WS_SCHEMA = vol.All(
    vol.Schema(
        {
            **cv.ENTITY_SERVICE_FIELDS,
            vol.Required(CONF_DURATION): vol.Coerce(int),
        },
    ),
    cv.has_at_least_one_key(CONF_DEVICE_ID),
)

SET_DOORBELL_LCD_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MESSAGE): cv.string,
        vol.Optional(CONF_DURATION, default="None"): cv.string,
    }
)
