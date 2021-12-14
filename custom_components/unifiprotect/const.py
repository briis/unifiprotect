"""Constant definitions for UniFi Protect Integration."""

# from typing_extensions import Required
from datetime import timedelta

from homeassistant.const import ATTR_ENTITY_ID, CONF_DEVICE_ID
from homeassistant.helpers import config_validation as cv
from pyunifiprotect.data.types import ModelType, Version
import voluptuous as vol

DOMAIN = "unifiprotect"

ATTR_CAMERA_ID = "camera_id"
ATTR_CHIME_ENABLED = "chime_enabled"
ATTR_CHIME_DURATION = "chime_duration"
ATTR_DEVICE_MODEL = "device_model"
ATTR_ENABLED_AT = "enabled_at"
ATTR_EVENT_SCORE = "event_score"
ATTR_EVENT_OBJECT = "event_object"
ATTR_EVENT_THUMB = "event_thumbnail"
ATTR_IS_DARK = "is_dark"
ATTR_MIC_SENSITIVITY = "mic_sensitivity"
ATTR_ONLINE = "online"
ATTR_PRIVACY_MODE = "privacy_mode"
ATTR_UP_SINCE = "up_since"
ATTR_VIEW_ID = "view_id"
ATTR_WDR_VALUE = "wdr_value"
ATTR_ZOOM_POSITION = "zoom_position"
ATTR_WIDTH = "width"
ATTR_HEIGHT = "height"
ATTR_FPS = "fps"
ATTR_BITRATE = "bitrate"
ATTR_CHANNEL_ID = "channel_id"

CONF_RECORDING_MODE = "recording_mode"
CONF_CHIME_DURATION = "chime_duration"
CONF_DOORBELL_TEXT = "doorbell_text"
CONF_DISABLE_RTSP = "disable_rtsp"
CONF_ENABLE_AT = "enable_at"
CONF_IR_MODE = "ir_mode"
CONF_STATUS_LIGHT = "light_on"
CONF_HDR_ON = "hdr_on"
CONF_HIGH_FPS_ON = "high_fps_on"
CONF_MESSAGE = "message"
CONF_MODE = "mode"
CONF_DURATION = "duration"
CONF_LEVEL = "level"
CONF_MIC_LEVEL = "mic_level"
CONF_PRIVACY_MODE = "privacy_mode"
CONF_POSITION = "position"
CONF_SENSITIVITY = "sensitivity"
CONF_VALUE = "value"
CONF_ALL_UPDATES = "all_updates"
CONF_OVERRIDE_CHOST = "override_connection_host"

CONFIG_OPTIONS = [
    CONF_ALL_UPDATES,
    CONF_DISABLE_RTSP,
]
CUSTOM_MESSAGE = "CUSTOM_MESSAGE"

DEFAULT_PORT = 443
DEFAULT_ATTRIBUTION = "Powered by UniFi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_SCAN_INTERVAL = 2
DEFAULT_VERIFY_SSL = False

RING_INTERVAL = timedelta(seconds=3)

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

SERVICE_PROFILE_WS = "profile_ws_messages"
SERVICE_ADD_DOORBELL_TEXT = "add_doorbell_text"
SERVICE_REMOVE_DOORBELL_TEXT = "remove_doorbell_text"
SERVICE_SET_DEFAULT_DOORBELL_TEXT = "set_default_doorbell_text"
SERVICE_SET_DOORBELL_MESSAGE = "set_doorbell_message"

SERVICE_LIGHT_SETTINGS = "light_settings"
SERVICE_SET_RECORDING_MODE = "set_recording_mode"
SERVICE_SET_IR_MODE = "set_ir_mode"
SERVICE_SET_STATUS_LIGHT = "set_status_light"
SERVICE_SET_HDR_MODE = "set_hdr_mode"
SERVICE_SET_HIGHFPS_VIDEO_MODE = "set_highfps_video_mode"
SERVICE_SET_DOORBELL_LCD_MESSAGE = "set_doorbell_lcd_message"
SERVICE_SET_MIC_VOLUME = "set_mic_volume"
SERVICE_SET_PRIVACY_MODE = "set_privacy_mode"
SERVICE_SET_ZOOM_POSITION = "set_zoom_position"
SERVICE_SET_WDR_VALUE = "set_wdr_value"
SERVICE_SET_DOORBELL_CHIME_DURAION = "set_doorbell_chime_duration"
SERVICE_SET_VIEWPORT_VIEW = "set_viewport_view"

TYPE_LIGHT_RECORD_MOTION = "motion"
TYPE_RECORD_MOTION = "detections"
TYPE_RECORD_ALWAYS = "always"
TYPE_RECORD_NEVER = "never"
TYPE_RECORD_NOTSET = "notset"
TYPE_RECORD_OFF = "off"
TYPE_INFRARED_AUTO = "auto"
TYPE_INFRARED_AUTOFILTER = "autoFilterOnly"
TYPE_INFRARED_OFF = "off"
TYPE_INFRARED_ON = "on"
TYPE_HIGH_FPS_ON = "highFps"
TYPE_HIGH_FPS_OFF = "default"
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
]
# CORE: Remove this before merging to core.
PLATFORMS_NEXT = PLATFORMS + [
    "button",
]
VALID_INFRARED_MODES = [
    TYPE_INFRARED_AUTO,
    TYPE_INFRARED_AUTOFILTER,
    TYPE_INFRARED_OFF,
    TYPE_INFRARED_ON,
]
VALID_RECORDING_MODES = [
    TYPE_RECORD_MOTION,
    TYPE_RECORD_ALWAYS,
    TYPE_RECORD_NEVER,
    TYPE_RECORD_NOTSET,
]
VALID_BOOLEAN_MODES = [True, False]

VALID_LIGHT_MODES = [TYPE_LIGHT_RECORD_MOTION, TYPE_RECORD_ALWAYS, TYPE_RECORD_OFF]
LIGHT_SETTINGS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MODE): vol.In(VALID_LIGHT_MODES),
        vol.Optional(CONF_ENABLE_AT): cv.string,
        vol.Optional(CONF_DURATION): vol.Coerce(int),
        vol.Optional(CONF_SENSITIVITY): vol.Coerce(int),
    }
)

DOORBELL_TEXT_SCHEMA = vol.All(
    vol.Schema(
        {
            **cv.ENTITY_SERVICE_FIELDS,
            vol.Required(CONF_MESSAGE): cv.string,
        },
    ),
    cv.has_at_least_one_key(CONF_DEVICE_ID),
)

SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=TYPE_RECORD_MOTION): vol.In(
            VALID_RECORDING_MODES
        ),
    }
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

# CORE: Remove this before merging to core.
SET_IR_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_IR_MODE, default=TYPE_INFRARED_AUTO): vol.In(
            VALID_INFRARED_MODES
        ),
    }
)

SET_STATUS_LIGHT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_STATUS_LIGHT, default=True): vol.In(VALID_BOOLEAN_MODES),
    }
)

SET_HDR_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_HDR_ON, default=True): vol.In(VALID_BOOLEAN_MODES),
    }
)

SET_HIGHFPS_VIDEO_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_HIGH_FPS_ON, default=True): vol.In(VALID_BOOLEAN_MODES),
    }
)

SET_PRIVACY_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_PRIVACY_MODE, default=False): vol.In(VALID_BOOLEAN_MODES),
        vol.Required(CONF_MIC_LEVEL, default=-1): vol.Coerce(int),
        vol.Optional(CONF_RECORDING_MODE, default=TYPE_RECORD_NOTSET): vol.In(
            VALID_RECORDING_MODES
        ),
    }
)

SET_DOORBELL_LCD_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MESSAGE): cv.string,
        vol.Optional(CONF_DURATION, default="None"): cv.string,
    }
)

SET_MIC_VOLUME_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_LEVEL, default=100): vol.Coerce(int),
    }
)

SET_ZOOM_POSITION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_POSITION, default=0): vol.Coerce(int),
    }
)

SET_WDR_VALUE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_VALUE, default=1): vol.Coerce(int),
    }
)

SET_DOORBELL_CHIME_DURATION_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_CHIME_DURATION, default=300): vol.Coerce(int),
    }
)
