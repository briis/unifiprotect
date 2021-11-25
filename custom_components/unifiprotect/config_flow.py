"""Config Flow to configure Unifi Protect Integration."""
from __future__ import annotations

import logging
from typing import Any

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


class UnifiProtectFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Unifi Protect config flow."""

    VERSION = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.entry: config_entries.ConfigEntry | None = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    @callback
    async def _async_create_entry(self, title: str, data: dict[str, Any]):
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
        user_input: dict[str, Any],
    ) -> tuple[dict[str, Any] | None, dict[str, str]]:
        session = async_create_clientsession(
            self.hass, cookie_jar=CookieJar(unsafe=True)
        )

        if CONF_HOST in user_input:
            host = user_input[CONF_HOST]
            port = user_input.get(CONF_PORT, DEFAULT_PORT)
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
        except NotAuthorized as ex:
            _LOGGER.debug(ex)
            errors[CONF_PASSWORD] = "invalid_auth"
        except NvrError as ex:
            _LOGGER.debug(ex)
            errors["base"] = "nvr_error"
        else:
            if nvr_data["server_version"] < MIN_REQUIRED_PROTECT_V:
                _LOGGER.debug("UniFi Protect Version not supported")
                errors["base"] = "protect_version"

        return nvr_data, errors

    async def async_step_reauth(self, user_input: dict[str, Any]) -> FlowResult:
        """Perform reauth upon an API authentication error."""

        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:

        errors = {}
        assert self.entry is not None

        # prepopulate fields
        form_data = {**self.entry.data}
        if user_input is not None:
            form_data.update(user_input)

            # validate login data
            nvr_data, errors = await self._async_get_nvr_data(form_data)
            if not errors:
                self.hass.config_entries.async_update_entry(self.entry, data=form_data)
                await self.hass.config_entries.async_reload(self.entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=form_data.get(CONF_USERNAME)
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""

        errors = {}
        if user_input is not None:
            nvr_data, errors = await self._async_get_nvr_data(user_input)

            if not errors:
                await self.async_set_unique_id(nvr_data[SERVER_ID])
                self._abort_if_unique_id_configured()

                return await self._async_create_entry(nvr_data[SERVER_NAME], user_input)

        user_input = user_input or {}
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST)): str,
                    vol.Required(
                        CONF_PORT, default=user_input.get(CONF_PORT, DEFAULT_PORT)
                    ): int,
                    vol.Required(
                        CONF_USERNAME, default=user_input.get(CONF_USERNAME)
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
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
