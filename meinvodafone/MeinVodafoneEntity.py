"""MeinVodafone Entity."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MeinVodafoneEntity(CoordinatorEntity, Entity):
    """Base class for all MeinVodafone entities."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        coordinator: str,
        attr: str,
    ) -> None:
        """Initialize MeinVodafone base entity."""

        super().__init__(coordinator)

        self.config_entry = config_entry
        self.coordinator = coordinator
        self.attr = attr
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.coordinator.contract_id)},
            "name": self.coordinator.contract_id,
            "model": self.coordinator.contract_id,
            "manufacturer": "Vodafone",
        }

    @property
    def available(self) -> bool:
        """Return true if entity is supported."""
        return getattr(self.coordinator.contract, "is_" + self.attr + "_supported")
