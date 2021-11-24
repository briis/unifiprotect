"""Config Flow to configure Unifi Protect Integration."""
from __future__ import annotations

import logging
from typing import Optional

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

    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        return await self._init_config_entry(user_input=user_input, reauth=True)

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        return await self._init_config_entry(user_input=user_input)

    def _get_form(self, reauth: bool):
        form = self._show_setup_form
        if reauth:
            form = self._show_reauth_form

        return form

    async def _get_protect(self, user_input) -> Optional[UpvServer]:
        session = async_create_clientsession(
            self.hass, cookie_jar=CookieJar(unsafe=True)
        )

        if self.unique_id is not None:
            entry = await self.async_set_unique_id(self.unique_id)
            host = entry.data[CONF_HOST]
            port = entry.data[CONF_PORT]
        elif CONF_HOST in user_input and CONF_PORT in user_input:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
        else:
            return None

        return UpvServer(
            session=session,
            host=host,
            port=port,
            username=user_input[CONF_USERNAME],
            password=user_input[CONF_PASSWORD],
        )

    async def _reload_entry(self, unique_id, user_input):
        entry = await self.async_set_unique_id(unique_id)

        new_data = entry.data.copy()
        new_data[CONF_USERNAME] = user_input[CONF_USERNAME]
        new_data[CONF_PASSWORD] = user_input[CONF_PASSWORD]

        self.hass.config_entries.async_update_entry(entry, data=new_data)
        await self.hass.config_entries.async_reload(entry.entry_id)
        return self.async_abort(reason="reauth_successful")

    async def _init_config_entry(self, user_input=None, reauth=False):
        """Common method to initalize config entry"""

        form = self._get_form(reauth)
        if user_input is None:
            return await form(user_input)

        errors = {}
        protect = await self._get_protect(user_input)

        if protect is None:
            return await form(errors)

        try:
            server_info = await protect.server_information()
            if server_info["server_version"] < MIN_REQUIRED_PROTECT_V:
                _LOGGER.debug("UniFi Protect Version not supported")
                errors["base"] = "protect_version"
                return await form(errors)

        except NotAuthorized as ex:
            _LOGGER.debug(ex)
            errors["base"] = "connection_error"
            return await form(errors)
        except NvrError as ex:
            _LOGGER.debug(ex)
            errors["base"] = "nvr_error"
            return await form(errors)

        unique_id = server_info[SERVER_ID]
        if reauth:
            return await self._reload_entry(unique_id, user_input)

        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=server_info[SERVER_NAME],
            data={
                CONF_ID: server_info[SERVER_NAME],
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

    async def _show_reauth_form(self, errors=None):
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="reauth",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors or {},
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
