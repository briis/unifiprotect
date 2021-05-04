"""Constant definitions for Unifi Protect Integration."""

from homeassistant.const import ATTR_ENTITY_ID, CONF_FILENAME
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
ATTR_WDR_VALUE = "wdr_value"
ATTR_ZOOM_POSITION = "zoom_position"

CONF_THUMB_WIDTH = "image_width"
CONF_RECORDING_MODE = "recording_mode"
CONF_SNAPSHOT_DIRECT = "snapshot_direct"
CONF_CHIME_ON = "chime_on"
CONF_CHIME_DURATION = "chime_duration"
CONF_DISABLE_RTSP = "disable_rtsp"
CONF_ENABLE_AT = "enable_at"
CONF_IR_MODE = "ir_mode"
CONF_IR_ON = "ir_on"
CONF_IR_OFF = "ir_off"
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

DEFAULT_PORT = 443
DEFAULT_ATTRIBUTION = "Powered by Unifi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_THUMB_WIDTH = 640
DEFAULT_SCAN_INTERVAL = 2

DEVICE_TYPE_CAMERA = "camera"
DEVICE_TYPE_LIGHT = "light"

DEVICE_TYPE_DOORBELL = "doorbell"
DEVICE_TYPE_MOTION = "motion"

DEVICES_WITH_CAMERA = (DEVICE_TYPE_CAMERA, DEVICE_TYPE_DOORBELL)

SERVICE_LIGHT_SETTINGS = "light_settings"
SERVICE_SAVE_THUMBNAIL = "save_thumbnail_image"
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

TYPE_RECORD_MOTION = "motion"
TYPE_RECORD_ALWAYS = "always"
TYPE_RECORD_NEVER = "never"
TYPE_RECORD_NOTSET = "notset"
TYPE_RECORD_OFF = "off"
TYPE_RECORD_SMART = "smart"
TYPE_RECORD_SMARTDETECT = "smartDetect"
TYPE_IR_AUTO = "auto"
TYPE_IR_ON = "always_on"
TYPE_IR_LED_OFF = "led_off"
TYPE_IR_OFF = "always_off"
TYPE_HIGH_FPS_ON = "highFps"
TYPE_HIGH_FPS_OFF = "default"

TYPES_IR_OFF = [
    TYPE_IR_OFF,
    TYPE_IR_LED_OFF,
]

TYPES_IR_ON = [
    TYPE_IR_AUTO,
    TYPE_IR_ON,
]

UNIFI_PROTECT_PLATFORMS = [
    "camera",
    "binary_sensor",
    "sensor",
    "switch",
    "light",
]

VALID_IR_MODES = [TYPE_IR_ON, TYPE_IR_AUTO, TYPE_IR_OFF, TYPE_IR_LED_OFF]
VALID_RECORDING_MODES = [
    TYPE_RECORD_MOTION,
    TYPE_RECORD_ALWAYS,
    TYPE_RECORD_NEVER,
    TYPE_RECORD_SMART,
    TYPE_RECORD_NOTSET,
]
VALID_BOOLEAN_MODES = [True, False]


LIGHT_SETTINGS_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MODE): cv.string,
        vol.Optional(CONF_ENABLE_AT): cv.string,
        vol.Optional(CONF_DURATION): vol.Coerce(int),
        vol.Optional(CONF_SENSITIVITY): vol.Coerce(int),
    }
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
        vol.Optional(CONF_RECORDING_MODE, default=TYPE_RECORD_MOTION): vol.In(
            VALID_RECORDING_MODES
        ),
    }
)

SET_IR_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_IR_MODE, default=TYPE_IR_AUTO): vol.In(VALID_IR_MODES),
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
