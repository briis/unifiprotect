"""Config Flow to configure Unifi Protect Integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

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
from homeassistant.data_entry_flow import FlowResult
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

AUTH_SCHEMA = {
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
}

SETUP_SCHEMA = {
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
    **AUTH_SCHEMA,
}


class UnifiProtectFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Unifi Protect config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    @callback
    async def _async_create_entry(self, title: str, data: Dict[str, Any]):
        return self.async_create_entry(
            title=title,
            data={**data, CONF_ID: title},
            options={
                CONF_DISABLE_RTSP: False,
                CONF_DOORBELL_TEXT: "",
            },
        )

    @callback
    async def _async_get_nvr_data(
        self,
        user_input: Dict[str, Any],
        entry: Optional[config_entries.ConfigEntry] = None,
    ) -> Tuple[Optional[Dict[str, Any]], Dict[str, str]]:
        session = async_create_clientsession(
            self.hass, cookie_jar=CookieJar(unsafe=True)
        )

        if CONF_HOST in user_input:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
        # reauth flow, pull host/port from existing settings
        elif entry:
            host = entry.data[CONF_HOST]
            port = entry.data.get(CONF_PORT, DEFAULT_PORT)
        else:
            return None, {}

        protect = UpvServer(
            session=session,
            host=host,
            port=port,
            username=user_input[CONF_USERNAME],
            password=user_input[CONF_PASSWORD],
        )

        errors = {}
        nvr_data = None
        try:
            nvr_data = await protect.server_information()
            if nvr_data["server_version"] < MIN_REQUIRED_PROTECT_V:
                _LOGGER.debug("UniFi Protect Version not supported")
                errors["base"] = "protect_version"
        except NotAuthorized as ex:
            _LOGGER.debug(ex)
            errors["base"] = "connection_error"
        except NvrError as ex:
            _LOGGER.debug(ex)
            errors["base"] = "nvr_error"

        return nvr_data, errors

    @callback
    def _get_config_entry(self) -> Optional[config_entries.ConfigEntry]:
        if self.unique_id is None:
            return None

        for entry in self._async_current_entries(include_ignore=True):
            if entry.unique_id == self.unique_id:
                return entry

        return None

    async def async_step_reauth(self, user_input: Dict[str, Any] = None) -> FlowResult:
        """Perform reauth upon an API authentication error."""

        errors = {}
        if user_input is not None:
            entry = self._get_config_entry()
            if not entry:
                return await self.async_step_user()

            # validate login data
            nvr_data, errors = await self._async_get_nvr_data(user_input, entry=entry)

            if nvr_data is not None:
                new_data = {
                    **entry.data,
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                }
                self.hass.config_entries.async_update_entry(entry, data=new_data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth",
            data_schema=vol.Schema(AUTH_SCHEMA),
            errors=errors,
        )

    async def async_step_user(self, user_input: Dict[str, Any] = None) -> FlowResult:
        """Handle a flow initiated by the user."""

        errors = {}
        if user_input is not None:
            nvr_data, errors = await self._async_get_nvr_data(user_input)

            if nvr_data is not None:
                await self.async_set_unique_id(nvr_data[SERVER_ID])
                self._abort_if_unique_id_configured()

                return await self._async_create_entry(nvr_data[SERVER_NAME], user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(SETUP_SCHEMA),
            errors=errors,
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
