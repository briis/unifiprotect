"""Config Flow to configure Unifi Protect Integration."""
from __future__ import annotations

import logging

from aiohttp import CookieJar
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_ID,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from pyunifiprotect import NotAuthorized, NvrError, UpvServer
from pyunifiprotect.const import SERVER_ID, SERVER_NAME
import voluptuous as vol

from .const import (
    CONF_DISABLE_RTSP,
    CONF_DOORBELL_TEXT,
    DEFAULT_PORT,
    DOMAIN,
    MIN_REQUIRED_PROTECT_V,
)

_LOGGER = logging.getLogger(__name__)


class UnifiProtectFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Unifi Protect config flow."""

    VERSION = 1

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
            server_info = await unifiprotect.server_information()
            if server_info["server_version"] < MIN_REQUIRED_PROTECT_V:
                _LOGGER.debug("UniFi Protect Version not supported")
                errors["base"] = "protect_version"
                return await self._show_setup_form(errors)

        except NotAuthorized as ex:
            _LOGGER.debug(ex)
            errors["base"] = "connection_error"
            return await self._show_setup_form(errors)
        except NvrError as ex:
            _LOGGER.debug(ex)
            errors["base"] = "nvr_error"
            return await self._show_setup_form(errors)

        unique_id = server_info[SERVER_ID]
        server_name = server_info[SERVER_NAME]

        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=server_name,
            data={
                CONF_ID: server_name,
                CONF_HOST: user_input[CONF_HOST],
                CONF_PORT: user_input[CONF_PORT],
                CONF_USERNAME: user_input.get(CONF_USERNAME),
                CONF_PASSWORD: user_input.get(CONF_PASSWORD),
            },
            options={
                CONF_DISABLE_RTSP: False,
                CONF_DOORBELL_TEXT: "",
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
                    vol.Required(
                        CONF_USERNAME,
                        default=self.config_entry.data.get(CONF_USERNAME, ""),
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=self.config_entry.data.get(CONF_PASSWORD, ""),
                    ): str,
                    vol.Optional(
                        CONF_DOORBELL_TEXT,
                        default=self.config_entry.options.get(CONF_DOORBELL_TEXT, ""),
                    ): str,
                    vol.Optional(
                        CONF_DISABLE_RTSP,
                        default=self.config_entry.options.get(CONF_DISABLE_RTSP, False),
                    ): bool,
                }
            ),
        )
