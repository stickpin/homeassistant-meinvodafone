"""The meinvodafone integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONTRACT_ID,
    COORDINATOR,
    DATA_LISTENER,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    REQUEST_TIMEOUT,
)
from .MeinVodafoneAPI import MeinVodafoneAPI
from .MeinVodafoneContract import MeinVodafoneContract
from .MeinVodafoneEntities import MeinVodafoneEntities

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up MeinVodafone from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    update_interval = timedelta(minutes=DEFAULT_UPDATE_INTERVAL)

    coordinator = MeinVodafoneCoordinator(hass, config_entry, update_interval)

    await coordinator.async_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = {
        COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry_data = hass.data[DOMAIN].pop(entry.entry_id)

        # Clean up API session
        coordinator = entry_data.get(COORDINATOR)
        if coordinator and coordinator.api:
            await coordinator.api.session.close()

        if DATA_LISTENER in entry_data:
            entry_data[DATA_LISTENER]()

    return unload_ok


class MeinVodafoneCoordinator(DataUpdateCoordinator):
    """Class to manage fetching MeinVodafone data."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, update_interval: timedelta
    ) -> None:
        """Initialize."""
        self.config_entry = config_entry
        self.contract_id = config_entry.data.get(CONTRACT_ID)
        self.contract: MeinVodafoneContract | None = None
        self.usage_data: dict = {}
        self.entities_list: list = []
        self.update_interval = update_interval

        username = config_entry.data.get(CONF_USERNAME)
        password = config_entry.data.get(CONF_PASSWORD)

        if not username or not password:
            raise ValueError("Username and password are required")

        self.api = MeinVodafoneAPI(username, password)

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval
        )

    async def _async_update_data(self) -> MeinVodafoneContract | None:
        """Fetch data."""
        _LOGGER.debug("Starting data update for contract %s", self.contract_id)
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                data = await self.api.get_contract_usage(self.contract_id)
                status_code = data.get("status_code")

                if status_code == 401:  # Unauthorized
                    _LOGGER.debug("Session expired, attempting re-login")
                    if await self.api.login():
                        data = await self.api.get_contract_usage(self.contract_id)
                        if data.get("status_code") == 200:
                            return await self.update(data.get("usage_data", {}))
                    raise ConfigEntryAuthFailed(
                        f"Authentication failed for {self.contract_id}"
                    )
                elif status_code != 200:
                    raise UpdateFailed(f"Failed to fetch data: status {status_code}")

                return await self.update(data.get("usage_data", {}))
        except asyncio.TimeoutError as err:
            raise UpdateFailed("Timeout fetching data") from err
        except ConfigEntryAuthFailed:
            raise  # Re-raise authentication errors without wrapping
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def update(self, usage_data: dict) -> MeinVodafoneContract | None:
        """Update usage data from MeinVodafone."""
        self.usage_data = usage_data
        self.contract = MeinVodafoneContract(
            contract_id=self.contract_id,
            usage_data=self.usage_data,
        )
        if not self.entities_list:
            self.entities_list = MeinVodafoneEntities(self.contract).entities_list
        _LOGGER.debug(
            "Update is completed for %s. Next update in %s",
            self.contract_id,
            self.update_interval,
        )
        return self.contract
