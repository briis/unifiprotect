"""Constant definitions for Unifi Protect Integration."""

# from typing_extensions import Required
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

DOMAIN = "unifiprotect"
UNIQUE_ID = "unique_id"

ATTR_CAMERA_ID = "camera_id"
ATTR_CHIME_ENABLED = "chime_enabled"
ATTR_CHIME_DURATION = "chime_duration"
ATTR_DEVICE_MODEL = "device_model"
ATTR_ENABLED_AT = "enabled_at"
ATTR_EVENT_SCORE = "event_score"
ATTR_EVENT_LENGTH = "event_length"
ATTR_EVENT_OBJECT = "event_object"
ATTR_IS_DARK = "is_dark"
ATTR_MIC_SENSITIVITY = "mic_sensitivity"
ATTR_ONLINE = "online"
ATTR_PRIVACY_MODE = "privacy_mode"
ATTR_UP_SINCE = "up_since"
ATTR_VIEWPORT_ID = "viewport_id"
ATTR_VIEW_ID = "view_id"
ATTR_WDR_VALUE = "wdr_value"
ATTR_ZOOM_POSITION = "zoom_position"

CONF_RECORDING_MODE = "recording_mode"
CONF_CHIME_ON = "chime_on"
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

CONFIG_OPTIONS = [
    CONF_DOORBELL_TEXT,
    CONF_DISABLE_RTSP,
]
CUSTOM_MESSAGE = "CUSTOM_MESSAGE"

DEFAULT_PORT = 443
DEFAULT_ATTRIBUTION = "Powered by UniFi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_SCAN_INTERVAL = 2

DEVICE_TYPE_CAMERA = "camera"
DEVICE_TYPE_LIGHT = "light"
DEVICE_TYPE_DOORBELL = "doorbell"
DEVICE_TYPE_MOTION = "motion"
DEVICE_TYPE_VIEWPORT = "viewer"
DEVICE_TYPE_SENSOR = "sensor"
DEVICE_TYPE_DARK = "is dark"

DEVICES_WITH_DOORBELL = (DEVICE_TYPE_DOORBELL,)
DEVICES_WITH_CAMERA = (DEVICE_TYPE_CAMERA, DEVICE_TYPE_DOORBELL)
DEVICES_WITH_SENSE = (DEVICE_TYPE_SENSOR,)
DEVICES_WITH_MOTION = (DEVICE_TYPE_CAMERA, DEVICE_TYPE_DOORBELL, DEVICE_TYPE_SENSOR)

ENTITY_CATEGORY_CONFIG = (
    "config"  # Replace with value from HA Core when more people are on 2021.11
)
ENTITY_CATEGORY_DIAGNOSTIC = (
    "diagnostic"  # Replace with value from HA Core when more people are on 2021.11
)

MIN_REQUIRED_PROTECT_V = "1.20.0"

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

PLATFORMS = [
    "camera",
    "binary_sensor",
    "sensor",
    "switch",
    "light",
    "select",
    "number",
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

SET_RECORDING_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_RECORDING_MODE, default=TYPE_RECORD_MOTION): vol.In(
            VALID_RECORDING_MODES
        ),
    }
)

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

SET_VIEW_PORT_VIEW_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.string,
        vol.Required(ATTR_VIEW_ID): cv.string,
    }
)
