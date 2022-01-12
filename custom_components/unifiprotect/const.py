"""Constant definitions for UniFi Protect Integration."""

from homeassistant.const import Platform
from pyunifiprotect.data.types import ModelType, Version

DOMAIN = "unifiprotect"

ATTR_EVENT_SCORE = "event_score"
ATTR_WIDTH = "width"
ATTR_HEIGHT = "height"
ATTR_FPS = "fps"
ATTR_BITRATE = "bitrate"
ATTR_CHANNEL_ID = "channel_id"
ATTR_MESSAGE = "message"
ATTR_DURATION = "duration"
ATTR_ANONYMIZE = "anonymize"

CONF_DOORBELL_TEXT = "doorbell_text"
CONF_DISABLE_RTSP = "disable_rtsp"
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
DEFAULT_SCAN_INTERVAL = 5
DEFAULT_VERIFY_SSL = False

DEVICES_THAT_ADOPT = {
    ModelType.CAMERA,
    ModelType.LIGHT,
    ModelType.VIEWPORT,
    ModelType.SENSOR,
}
DEVICES_WITH_ENTITIES = DEVICES_THAT_ADOPT | {ModelType.NVR}
DEVICES_FOR_SUBSCRIBE = DEVICES_WITH_ENTITIES | {ModelType.EVENT}

MIN_REQUIRED_PROTECT_V = Version("1.20.0")
OUTDATED_LOG_MESSAGE = "You are running v%s of UniFi Protect. Minimum required version is v%s. Please upgrade UniFi Protect and then retry"

TYPE_EMPTY_VALUE = ""

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CAMERA,
    Platform.LIGHT,
    Platform.MEDIA_PLAYER,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
]
