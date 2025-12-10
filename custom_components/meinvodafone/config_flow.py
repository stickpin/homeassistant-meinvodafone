"""Config flow for meinvodafone integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import CONTRACT_ID, DOMAIN
from .MeinVodafoneAPI import MeinVodafoneAPI

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
        ),
        vol.Required(CONF_PASSWORD): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
    }
)

REAUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class MeinVodafoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle user step."""

    VERSION = 1
    reauth_entry: ConfigEntry | None = None

    def __init__(self) -> None:
        """Initialize."""
        self.api: MeinVodafoneAPI | None = None
        self.username: str | None = None
        self.password: str | None = None
        self.contract_id: str | None = None
        self.contracts: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle login step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate input
            username = user_input.get(CONF_USERNAME, "").strip()
            password = user_input.get(CONF_PASSWORD, "").strip()

            if not username or not password:
                errors["base"] = "invalid_credentials"
                return self.async_show_form(
                    step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
                )

            self.username = username
            self.password = password
            self.api = MeinVodafoneAPI(self.username, self.password)

            try:
                async with asyncio.timeout(30):
                    response = await self.api.login()

                    if response:
                        self.contracts = await self.api.get_contracts()

                        if len(self.contracts) > 0:
                            return await self.async_step_select_contract()

                        errors["base"] = "no_contracts"
                    else:
                        errors["base"] = "login_failed"

            except asyncio.TimeoutError:
                _LOGGER.error("Timeout during login")
                errors["base"] = "timeout"
            except Exception as err:
                _LOGGER.error("Error during login: %s", str(err))
                errors["base"] = "unknown_error"
            finally:
                # Clean up session if login failed
                if errors and self.api:
                    await self.api.session.close()
                    self.api = None

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_select_contract(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle contract id selection step."""
        if user_input is not None:
            self.contract_id = user_input[CONTRACT_ID]

            await self.async_set_unique_id(self.contract_id)
            self._abort_if_unique_id_configured()

            # Don't close API session - it will be managed by the pool
            # The session used during setup will be garbage collected

            return self.async_create_entry(
                title=self.contract_id,
                data={
                    CONF_USERNAME: self.username,
                    CONF_PASSWORD: self.password,
                    CONTRACT_ID: self.contract_id,
                },
            )

        return self.async_show_form(
            step_id="select_contract",
            data_schema=vol.Schema(
                {
                    vol.Required(CONTRACT_ID): vol.In(self.contracts),
                }
            ),
            last_step=True,
        )

    async def async_step_reauth(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Dialog that informs the user that reauth is required."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input.get(CONF_USERNAME, "").strip()
            password = user_input.get(CONF_PASSWORD, "").strip()

            if not username or not password:
                errors["base"] = "invalid_credentials"
            else:
                self.api = MeinVodafoneAPI(username, password)

                try:
                    async with asyncio.timeout(30):
                        response = await self.api.login()

                        if response:
                            data = self.reauth_entry.data.copy()
                            self.hass.config_entries.async_update_entry(
                                self.reauth_entry,
                                data={
                                    **data,
                                    CONF_USERNAME: username,
                                    CONF_PASSWORD: password,
                                },
                            )
                            await self.hass.config_entries.async_reload(
                                self.reauth_entry.entry_id
                            )

                            return self.async_abort(reason="reauth_successful")

                        errors["base"] = "login_failed"

                except asyncio.TimeoutError:
                    _LOGGER.error("Timeout during reauth")
                    errors["base"] = "timeout"
                except Exception as err:
                    _LOGGER.error("Error during reauth: %s", str(err))
                    errors["base"] = "unknown_error"
                finally:
                    if self.api:
                        await self.api.session.close()
                        self.api = None

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, default=self.reauth_entry.data[CONF_USERNAME]
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
