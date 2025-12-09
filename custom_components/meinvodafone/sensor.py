"""Sensor platform for meinvodafone integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import MeinVodafoneCoordinator
from .const import COORDINATOR, DOMAIN
from .MeinVodafoneEntity import MeinVodafoneEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Initialize meinvodafone config entry."""
    coordinator: MeinVodafoneCoordinator = hass.data[DOMAIN][config_entry.entry_id][
        COORDINATOR
    ]

    if coordinator.contract:
        # Filter and create sensor entities
        sensors = [
            MeinVodafoneSensor(
                config_entry=config_entry,
                coordinator=coordinator,
                entity=entity,
            )
            for entity in coordinator.entities_list
            if entity.component == "sensor"
        ]
        async_add_entities(sensors)


class MeinVodafoneSensor(MeinVodafoneEntity, SensorEntity):
    """MeinVodafone Sensor."""

    def __init__(
        self,
        config_entry: ConfigEntry,
        coordinator: MeinVodafoneCoordinator,
        entity: Any,  # Type: Sensor from MeinVodafoneEntities
    ) -> None:
        """Initialize MeinVodafone Sensor."""
        super().__init__(
            config_entry=config_entry,
            coordinator=coordinator,
            attr=entity.attr,
        )

        # Store entity configuration
        self._entity = entity
        self.plan_name: str | None = entity.plan_name

        # Set sensor attributes
        self._attr_name = entity.name
        self._attr_unique_id = f"{coordinator.contract_id}_{entity.attr}"
        self._attr_has_entity_name = True
        self._attr_icon = entity.icon
        self._attr_native_unit_of_measurement = entity.unit
        self._attr_device_class = entity.device_class
        self._attr_state_class = entity.state_class
        self._attr_should_poll = False
        self._attr_suggested_display_precision = entity.display_precision

        # Set initial value
        if coordinator.contract:
            self._attr_native_value = getattr(coordinator.contract, entity.attr, None)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return sensor specific state attributes."""
        if not self.coordinator.contract:
            return {}

        attributes: dict[str, Any] = {}

        # Add last update timestamp
        last_update_attr = f"{self.attr}_last_update"
        if hasattr(self.coordinator.contract, last_update_attr):
            last_update = getattr(self.coordinator.contract, last_update_attr, None)
            if last_update is not None:
                attributes["last_update"] = last_update

        # Add billing cycle information if available
        if hasattr(self.coordinator.contract, "billing_cycle_start"):
            cycle_start = getattr(self.coordinator.contract, "billing_cycle_start")
            if cycle_start is not None:
                attributes["billing_cycle_start"] = cycle_start

        if hasattr(self.coordinator.contract, "billing_cycle_end"):
            cycle_end = getattr(self.coordinator.contract, "billing_cycle_end")
            if cycle_end is not None:
                attributes["billing_cycle_end"] = cycle_end

        # Add plan name if available
        if self.plan_name and hasattr(self.coordinator.contract, self.plan_name):
            plan_value = getattr(self.coordinator.contract, self.plan_name, None)
            if plan_value is not None:
                attributes["plans"] = plan_value

        return attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.contract:
            self._attr_native_value = getattr(
                self.coordinator.contract, self.attr, None
            )
        self.async_write_ha_state()
