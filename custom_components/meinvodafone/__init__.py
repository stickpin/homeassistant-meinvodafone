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

from .MeinVodafoneAPIPool import MeinVodafoneAPIPool
from .const import (
    CONTRACT_ID,
    COORDINATOR,
    DATA_LISTENER,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MEINVODAFONE_API_POOL,
    REQUEST_TIMEOUT,
)
from .MeinVodafoneContract import MeinVodafoneContract
from .MeinVodafoneEntities import MeinVodafoneEntities

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up MeinVodafone from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Create API pool if it doesn't exist (shared across all entries)
    if MEINVODAFONE_API_POOL not in hass.data[DOMAIN]:
        hass.data[DOMAIN][MEINVODAFONE_API_POOL] = MeinVodafoneAPIPool()

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

        if DATA_LISTENER in entry_data:
            entry_data[DATA_LISTENER]()

        # Note: Don't close API session here - it might be used by other contracts
        # The session will be closed when all entries for that username are removed

    # If this was the last entry, clean up the API pool
    if (
        not hass.data[DOMAIN]
        or len([k for k in hass.data[DOMAIN] if k != MEINVODAFONE_API_POOL]) == 0
    ):
        if MEINVODAFONE_API_POOL in hass.data[DOMAIN]:
            await hass.data[DOMAIN][MEINVODAFONE_API_POOL].close_all()
            del hass.data[DOMAIN][MEINVODAFONE_API_POOL]

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

        # Get shared API instance from pool
        api_pool: MeinVodafoneAPIPool = hass.data[DOMAIN][MEINVODAFONE_API_POOL]
        self.api = api_pool.get_or_create(username, password)
        self.username = username  # Store for potential cleanup

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval
        )

    async def _async_update_data(self) -> MeinVodafoneContract | None:
        """Fetch data."""
        _LOGGER.debug("Starting data update for contract %s", self.contract_id)
        try:
            # Get API pool reference
            api_pool: MeinVodafoneAPIPool = self.hass.data[DOMAIN][
                MEINVODAFONE_API_POOL
            ]

            # Ensure authenticated before fetching data
            if not await api_pool.ensure_authenticated(self.api, self.username):
                raise ConfigEntryAuthFailed(
                    f"Authentication failed for {self.contract_id}"
                )

            async with asyncio.timeout(REQUEST_TIMEOUT):
                data = await self.api.get_contract_usage(self.contract_id)
                status_code = data.get("status_code")

                if status_code == 401:  # Unauthorized
                    _LOGGER.debug("Session expired, attempting re-login")

                    # Mark as unauthenticated and try again
                    self.api.is_authenticated = False
                    if await api_pool.ensure_authenticated(self.api, self.username):
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
