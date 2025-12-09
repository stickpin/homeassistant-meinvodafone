"""MeinVodafone Entity."""

import logging
from typing import TYPE_CHECKING

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

if TYPE_CHECKING:
    from . import MeinVodafoneCoordinator

_LOGGER = logging.getLogger(__name__)


class MeinVodafoneEntity(CoordinatorEntity["MeinVodafoneCoordinator"]):
    """Base class for all MeinVodafone entities."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        coordinator: "MeinVodafoneCoordinator",
        attr: str,
    ) -> None:
        """Initialize MeinVodafone base entity.

        Args:
            config_entry: The config entry for this integration.
            coordinator: The data update coordinator.
            attr: The attribute name from the contract (e.g., 'data_remaining').
        """
        super().__init__(coordinator)

        self.config_entry: ConfigEntry = config_entry
        self.coordinator: "MeinVodafoneCoordinator" = coordinator
        self.attr: str = attr

        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.contract_id)},
            name=self.coordinator.contract_id,
            model=self.coordinator.contract_id,
            manufacturer="Vodafone",
        )

    @property
    def available(self) -> bool:
        """Return true if entity is available and supported."""
        if not self.coordinator.contract:
            return False

        supported_attr = f"is_{self.attr}_supported"
        return getattr(self.coordinator.contract, supported_attr, False)
