"""The meinvodafone integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONTRACT_ID,
    COORDINATOR,
    DATA_LISTENER,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
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

        if DATA_LISTENER in entry_data:
            entry_data[DATA_LISTENER]()

        # hass.data[DOMAIN][entry.entry_id][MEINVODAFONE_API] = None
        # hass.data[DOMAIN][entry.entry_id][CONTRACT] = None
        # hass.data[DOMAIN][entry.entry_id][CONTRACT_USAGE] = None

        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class MeinVodafoneCoordinator(DataUpdateCoordinator):
    """Class to manage fetching mail data."""

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, update_interval: timedelta
    ) -> None:
        """Initialize."""
        self.hass = hass
        self.config_entry = config_entry
        self.contract_id = config_entry.data.get(CONTRACT_ID)
        self.contract = None
        self.usage_data = {}
        self.entities_list = None
        self.update_interval = update_interval
        self.api = MeinVodafoneAPI(
            config_entry.data.get(CONF_USERNAME),
            config_entry.data.get(CONF_PASSWORD),
        )

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=self.update_interval
        )

    async def _async_update_data(self):
        """Fetch data."""

        async with asyncio.timeout(10):
            data = await self.api.get_contract_usage(self.contract_id)
            if data.get("status_code", None) != 200:
                logged_in = await self.api.login()
                if logged_in:
                    return await self.update()
                raise ConfigEntryAuthFailed(
                    f"Credentials expired for {self.contract_id}"
                )
            return await self.update()

    async def update(self) -> MeinVodafoneContract | None:
        """Update usage data from MeinVodafone."""

        data = await self.api.get_contract_usage(self.contract_id)

        self.usage_data = data.get("usage_data", {})
        self.contract = MeinVodafoneContract(
            hass=self.hass,
            config_entry=self.config_entry,
            contract_id=self.contract_id,
            usage_data=self.usage_data,
        )
        if self.entities_list is None:
            self.entities_list = MeinVodafoneEntities(self.contract).entities_list
        _LOGGER.debug(
            "Update is completed for %s. Next update in %s",
            self.contract_id,
            self.update_interval,
        )
        return self.contract
