"""Config flow for meinvodafone integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN
from .MeinVodafoneAPI import MeinVodafoneAPI

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("username"): TextSelector(
            TextSelectorConfig(type=TextSelectorType.TEXT, autocomplete="username")
        ),
        vol.Required("password"): TextSelector(
            TextSelectorConfig(
                type=TextSelectorType.PASSWORD, autocomplete="current-password"
            )
        ),
    }
)


class MeinVodafoneConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle user step."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    reauth_entry: ConfigEntry | None = None

    def __init__(self) -> None:
        """Initialize."""
        self.api = None
        self.username = None
        self.password = None
        self.contract_id = None
        self.contracts = {}

    async def async_step_user(self, user_input=None):
        """Handle login step."""
        errors = {}

        if user_input is not None:
            try:
                # Store the username and password in the user_input to pass it to the next step
                self.username = user_input[CONF_USERNAME]
                self.password = user_input[CONF_PASSWORD]

                # Perform login using the provided credentials
                self.api = MeinVodafoneAPI(self.username, self.password)
                response = await self.api.login()

                if response:
                    self.contracts = await self.api.get_contracts()

                    # Extract contracts from the response and show it to the user for selection
                    if len(self.contracts) > 0:
                        return self.async_show_form(
                            step_id="select_contract",
                            data_schema=vol.Schema(
                                {
                                    vol.Required("contract_id"): vol.In(self.contracts),
                                }
                            ),
                            errors=errors,
                            last_step=True,
                        )
                    errors["base"] = "no_contracts"
                else:
                    errors["base"] = "login_failed"

            except Exception as e:
                _LOGGER.error("Error during login: %s", str(e))
                errors["base"] = "login_failed"

        return self.async_show_form(
            step_id="user", data_schema=CONFIG_SCHEMA, errors=errors
        )

    async def async_step_select_contract(self, user_input=None):
        """Handle contract id selection step."""
        errors = {}

        if user_input is not None:
            # Store the selected ID
            self.contract_id = user_input["contract_id"]

            await self.async_set_unique_id(self.contract_id)
            self._abort_if_unique_id_configured()

            # Create the config entry with the collected data
            return self.async_create_entry(
                title=self.contract_id,
                data={
                    "username": self.username,
                    "password": self.password,
                    "contract_id": self.contract_id,
                },
            )

        return self.async_show_form(
            step_id="select_contract",
            data_schema=vol.Schema(
                {
                    vol.Required("contract_id"): vol.In(self.contracts),
                }
            ),
            errors=errors,
            last_step=True,
        )

    async def async_step_reauth(self, user_input=None) -> dict:
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None) -> dict:
        """Dialog that informs the user that reauth is required."""
        errors = {}

        if user_input is not None:
            try:
                # Store the username and password in the user_input to pass it to the next step
                self.username = user_input[CONF_USERNAME]
                self.password = user_input[CONF_PASSWORD]

                # Perform login using the provided credentials
                self.api = MeinVodafoneAPI(self.username, self.password)
                response = await self.api.login()

                if response:
                    data = self.reauth_entry.data.copy()
                    self.hass.config_entries.async_update_entry(
                        self.reauth_entry,
                        data={
                            **data,
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                        },
                    )
                    self.hass.async_create_task(
                        self.hass.config_entries.async_reload(
                            self.reauth_entry.entry_id
                        )
                    )

                    return self.async_abort(reason="reauth_successful")
                errors["base"] = "login_failed"

            except Exception as e:
                _LOGGER.error("Error during login: %s", str(e))
                errors["base"] = "login_failed"

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
