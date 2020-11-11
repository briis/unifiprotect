"""Config Flow to configure Unifi Protect Integration."""
import logging

from aiohttp import CookieJar
from pyunifiprotect import NotAuthorized, NvrError, UpvServer
import voluptuous as vol

# from homeassistant.config_entries import ConfigFlow
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    CONF_IR_OFF,
    CONF_IR_ON,
    CONF_SNAPSHOT_DIRECT,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    TYPE_IR_AUTO,
    TYPE_IR_OFF,
    TYPES_IR_OFF,
    TYPES_IR_ON,
)

_LOGGER = logging.getLogger(__name__)


class UnifiProtectFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Unifi Protect config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is None:
            return await self._show_setup_form(user_input)

        errors = {}

        session = async_create_clientsession(
            self.hass, cookie_jar=CookieJar(unsafe=True)
        )

        unifiprotect = UpvServer(
            session,
            user_input[CONF_HOST],
            user_input[CONF_PORT],
            user_input[CONF_USERNAME],
            user_input[CONF_PASSWORD],
        )

        try:
            unique_id = await unifiprotect.unique_id()
        except NotAuthorized as e:
            _LOGGER.debug(e)
            errors["base"] = "connection_error"
            return await self._show_setup_form(errors)
        except NvrError as e:
            _LOGGER.debug(e)
            errors["base"] = "nvr_error"
            return await self._show_setup_form(errors)

        entries = self._async_current_entries()
        for entry in entries:
            if entry.data[CONF_ID] == unique_id:
                return self.async_abort(reason="server_exists")

        return self.async_create_entry(
            title=unique_id,
            data={
                CONF_ID: unique_id,
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_USERNAME: user_input.get(CONF_USERNAME),
                CONF_PASSWORD: user_input.get(CONF_PASSWORD),
                CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL),
                CONF_SNAPSHOT_DIRECT: user_input.get(CONF_SNAPSHOT_DIRECT),
                CONF_IR_ON: user_input.get(CONF_IR_ON),
                CONF_IR_OFF: user_input.get(CONF_IR_OFF),
            },
        )

    async def _show_setup_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=2, max=20)),
                    vol.Optional(CONF_SNAPSHOT_DIRECT, default=False): bool,
                    vol.Optional(CONF_IR_ON, default=TYPE_IR_AUTO): vol.In(TYPES_IR_ON),
                    vol.Optional(CONF_IR_OFF, default=TYPE_IR_OFF): vol.In(
                        TYPES_IR_OFF
                    ),
                }
            ),
            errors=errors or {},
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SNAPSHOT_DIRECT,
                        default=self.config_entry.options.get(
                            CONF_SNAPSHOT_DIRECT, False
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=2, max=20)),
                }
            ),
        )
