"""Unifi Protect Platform."""
import logging
import voluptuous as vol
import requests
from . import protectnvr as nvr

from homeassistant.const import ATTR_ATTRIBUTION, CONF_HOST, CONF_PORT, CONF_SSL, CONF_USERNAME, CONF_PASSWORD
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers.entity import Entity

__version__ = '0.0.4'

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by Unifi Protect NVR"
DATA_UFP = "data_ufp"
NVR = "nvr_ufp"
DEFAULT_BRAND = "Ubiquiti"

DOMAIN = "unifiprotect"
DEFAULT_ENTITY_NAMESPACE = "unifprotect"
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

def setup(hass, config):
    """Set up the Unifi Protect component."""
    conf = config[DOMAIN]
    host = conf.get(CONF_HOST)
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    port = conf.get(CONF_PORT)
    use_ssl = conf.get(CONF_SSL)

    try:
        nvrobject = nvr.protectRemote(host,port,username,password,use_ssl)
        hass.data[DATA_UFP] = nvrobject

    except nvr.NotAuthorized:
        _LOGGER.error("Authorization failure while connecting to NVR")
        return False
    except nvr.NvrError as ex:
        _LOGGER.error("NVR refuses to talk to me: %s", str(ex))
        raise PlatformNotReady
    except requests.exceptions.ConnectionError as ex:
        _LOGGER.error("Unable to connect to NVR: %s", str(ex))
        raise PlatformNotReady
    return True

