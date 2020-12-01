"""Constant definitions for Unifi Protect Integration."""

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID, CONF_FILENAME
from homeassistant.helpers import config_validation as cv

DOMAIN = "unifiprotect"
UNIQUE_ID = "unique_id"

ATTR_CAMERA_ID = "camera_id"
ATTR_CAMERA_TYPE = "camera_type"
ATTR_UP_SINCE = "up_since"
ATTR_ONLINE = "online"
ATTR_EVENT_SCORE = "event_score"
ATTR_EVENT_LENGTH = "event_length"
ATTR_EVENT_OBJECT = "event_object"

CONF_THUMB_WIDTH = "image_width"
CONF_RECORDING_MODE = "recording_mode"
CONF_SNAPSHOT_DIRECT = "snapshot_direct"
CONF_IR_MODE = "ir_mode"
CONF_IR_ON = "ir_on"
CONF_IR_OFF = "ir_off"
CONF_STATUS_LIGHT = "light_on"
CONF_HDR_ON = "hdr_on"
CONF_HIGH_FPS_ON = "high_fps_on"
CONF_MESSAGE = "message"
CONF_DURATION = "duration"

DEFAULT_PORT = 443
DEFAULT_ATTRIBUTION = "Powered by Unifi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_THUMB_WIDTH = 640
DEFAULT_SCAN_INTERVAL = 2

DEVICE_TYPE_DOORBELL = "doorbell"
DEVICE_TYPE_MOTION = "motion"

SERVICE_SAVE_THUMBNAIL = "save_thumbnail_image"
SERVICE_SET_RECORDING_MODE = "set_recording_mode"
SERVICE_SET_IR_MODE = "set_ir_mode"
SERVICE_SET_STATUS_LIGHT = "set_status_light"
SERVICE_SET_HDR_MODE = "set_hdr_mode"
SERVICE_SET_HIGHFPS_VIDEO_MODE = "set_highfps_video_mode"
SERVICE_SET_DOORBELL_LCD_MESSAGE = "set_doorbell_lcd_message"

TYPE_RECORD_MOTION = "motion"
TYPE_RECORD_ALLWAYS = "always"
TYPE_RECORD_NEVER = "never"
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
]

VALID_IR_MODES = [TYPE_IR_ON, TYPE_IR_AUTO, TYPE_IR_OFF, TYPE_IR_LED_OFF]
VALID_RECORDING_MODES = [
    TYPE_RECORD_MOTION,
    TYPE_RECORD_ALLWAYS,
    TYPE_RECORD_NEVER,
    TYPE_RECORD_SMART,
]
VALID_LIGHT_MODES = [True, False]

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
        vol.Optional(CONF_STATUS_LIGHT, default=True): vol.In(VALID_LIGHT_MODES),
    }
)

SET_HDR_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_HDR_ON, default=True): vol.In(VALID_LIGHT_MODES),
    }
)

SET_HIGHFPS_VIDEO_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(CONF_HIGH_FPS_ON, default=True): vol.In(VALID_LIGHT_MODES),
    }
)

SET_DOORBELL_LCD_MESSAGE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(CONF_MESSAGE): cv.string,
        vol.Optional(CONF_DURATION, default="None"): cv.string,
    }
)
