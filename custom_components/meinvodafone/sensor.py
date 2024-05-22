"""Sensor platform for meinvodafone integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass
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
        async_add_entities(
            MeinVodafoneSensor(
                hass=hass,
                config_entry=config_entry,
                coordinator=coordinator,
                attr=entity.attr,
                name=entity.name,
                icon=entity.icon,
                unit=entity.unit,
                device_class=entity.device_class,
                plan_name=entity.plan_name,
                value=getattr(coordinator.contract, entity.attr),
                state_class=SensorStateClass.MEASUREMENT,
                display_precision=entity.display_precision,
            )
            for entity in (
                entity
                for entity in coordinator.entities_list
                if entity.component == "sensor"
            )
        )


class MeinVodafoneSensor(MeinVodafoneEntity, SensorEntity):
    """MeinVodafone Sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        coordinator: str,
        attr: str,
        name: str,
        icon: str,
        unit: str,
        device_class: str,
        plan_name: str,
        value: str,
        state_class: str,
        display_precision: int,
    ) -> None:
        """Initialize MeinVodafone Sensor."""
        super().__init__(
            config_entry=config_entry,
            coordinator=coordinator,
            attr=attr,
        )
        self.hass = hass
        self.config_entry = config_entry
        self.coordinator = coordinator
        self.plan_name = plan_name
        self.attr = attr
        self._attr_name = name
        self._attr_unique_id = f"{self.coordinator.contract_id}_{attr}"
        self._attr_has_entity_name = True
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_available = True
        self._attr_native_value = value
        self._attr_should_poll = False
        self._attr_suggested_display_precision = display_precision
        self.entity_id = f"sensor.{self.coordinator.contract_id}_{attr}"

    @property
    def extra_state_attributes(self) -> dict:
        """Return sensor specific state attributes."""
        attributes = {
            "last_update": getattr(
                self.coordinator.contract, self.attr + "_last_update"
            ),
        }
        if hasattr(self.coordinator.contract, "billing_cycle_start"):
            attributes["billing_cycle_start"] = getattr(
                self.coordinator.contract, "billing_cycle_start"
            )
        if hasattr(self.coordinator.contract, "billing_cycle_end"):
            attributes["billing_cycle_end"] = getattr(
                self.coordinator.contract, "billing_cycle_end"
            )
        if self.plan_name:
            attributes["plans"] = getattr(self.coordinator.contract, self.plan_name)
        return attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self.coordinator.contract, self.attr)
        self.async_write_ha_state()
