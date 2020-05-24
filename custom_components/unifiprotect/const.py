""" Constant definitions for Unifi Protect Integration."""

from homeassistant.components.camera import DOMAIN as CAMERA_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN

DOMAIN = "unifiprotect"
UNIQUE_ID = "unique_id"

ATTR_CAMERA_ID = "camera_id"
ATTR_CAMERA_TYPE = "camera_type"
ATTR_UP_SINCE = "up_since"
ATTR_ONLINE = "online"
ATTR_EVENT_SCORE = "event_score"

CONF_THUMB_WIDTH = "image_width"
CONF_RECORDING_MODE = "recording_mode"
CONF_IR_MODE = "ir_mode"
CONF_IR_ON = "ir_on"
CONF_IR_OFF = "ir_off"

DEFAULT_PORT = 7443
DEFAULT_ATTRIBUTION = "Data provided by Ubiquiti's Unifi Protect Server"
DEFAULT_BRAND = "Ubiquiti"
DEFAULT_THUMB_WIDTH = 640

DEVICE_CLASS_DOORBELL = "doorbell"

TYPE_RECORD_MOTION = "motion"
TYPE_RECORD_ALLWAYS = "always"
TYPE_RECORD_NEVER = "never"
TYPE_IR_AUTO = "auto"
TYPE_IR_ON = "always_on"
TYPE_IR_LED_OFF = "led_off"
TYPE_IR_OFF = "always_off"

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
