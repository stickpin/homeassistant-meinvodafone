"""MeinVodafone Entities."""

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.sensor.const import UnitOfInformation, UnitOfTime
from homeassistant.const import CURRENCY_EURO
from homeassistant.helpers.entity import EntityCategory

from .MeinVodafoneContract import MeinVodafoneContract

_LOGGER = logging.getLogger(__name__)


class BaseEntity:
    """Base class for all components."""

    def __init__(
        self,
        component: str,
        attr: str,
        name: str,
        icon: str | None = None,
        plan_name: str | None = None,
        entity_type: EntityCategory | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        display_precision: int | None = None,
    ) -> None:
        """Init."""
        self.attr = attr
        self.component = component
        self.name = name
        self.icon = icon
        self.plan_name = plan_name
        self.entity_type = entity_type
        self.device_class = device_class
        self.state_class = state_class
        self.display_precision = display_precision
        self.contract: MeinVodafoneContract | None = None

    def setup(self, contract: MeinVodafoneContract) -> bool:
        """Set up entity if supported."""
        self.contract = contract
        if not self.is_supported:
            _LOGGER.debug("%s %s is not supported", type(self).__name__, self.attr)
            return False

        _LOGGER.debug("%s %s is supported", type(self).__name__, self.attr)
        return True

    @property
    def is_supported(self) -> bool:
        """Check entity is supported."""
        if not self.contract:
            return False

        supported_attr = f"is_{self.attr}_supported"
        if hasattr(self.contract, supported_attr):
            return getattr(self.contract, supported_attr)
        return False


class Sensor(BaseEntity):
    """Base class for sensor type entities."""

    def __init__(
        self,
        attr: str,
        name: str,
        icon: str | None,
        unit: str | None,
        plan_name: str | None = None,
        entity_type: EntityCategory | None = None,
        device_class: SensorDeviceClass | None = None,
        state_class: SensorStateClass | None = None,
        display_precision: int | None = None,
    ) -> None:
        """Init."""
        super().__init__(
            component="sensor",
            attr=attr,
            name=name,
            icon=icon,
            plan_name=plan_name,
            entity_type=entity_type,
            device_class=device_class,
            state_class=state_class,
            display_precision=display_precision,
        )
        self.unit = unit


def create_entities() -> list[Sensor]:
    """Return list of all entities."""
    return [
        # Minutes sensors
        Sensor(
            attr="minutes_remaining",
            name="Minutes remaining",
            icon="mdi:clock-plus",
            unit=UnitOfTime.MINUTES,
            plan_name="minutes_name",
            state_class=SensorStateClass.MEASUREMENT,
            display_precision=0,
        ),
        Sensor(
            attr="minutes_used",
            name="Minutes used",
            icon="mdi:clock-minus",
            unit=UnitOfTime.MINUTES,
            plan_name="minutes_name",
            state_class=SensorStateClass.MEASUREMENT,
            display_precision=0,
        ),
        Sensor(
            attr="minutes_total",
            name="Minutes total",
            icon="mdi:clock-check",
            unit=UnitOfTime.MINUTES,
            plan_name="minutes_name",
            state_class=SensorStateClass.MEASUREMENT,
            display_precision=0,
        ),
        # SMS sensors
        Sensor(
            attr="sms_remaining",
            name="SMS remaining",
            icon="mdi:message-plus",
            unit="sms",
            plan_name="sms_name",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        Sensor(
            attr="sms_used",
            name="SMS used",
            icon="mdi:message-minus",
            unit="sms",
            plan_name="sms_name",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        Sensor(
            attr="sms_total",
            name="SMS total",
            icon="mdi:message-check",
            unit="sms",
            plan_name="sms_name",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        # Data sensors
        Sensor(
            attr="data_remaining",
            name="Data remaining",
            icon="mdi:web-plus",
            unit=UnitOfInformation.MEBIBYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            plan_name="data_name",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        Sensor(
            attr="data_used",
            name="Data used",
            icon="mdi:web-minus",
            unit=UnitOfInformation.MEBIBYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            plan_name="data_name",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        Sensor(
            attr="data_total",
            name="Data total",
            icon="mdi:web-check",
            unit=UnitOfInformation.MEBIBYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            plan_name="data_name",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        # Billing sensors
        Sensor(
            attr="billing_current_summary",
            name="Billing current summary",
            icon="mdi:credit-card-search",
            unit=CURRENCY_EURO,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        Sensor(
            attr="billing_last_summary",
            name="Billing last summary",
            icon="mdi:credit-card-clock",
            unit=CURRENCY_EURO,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        Sensor(
            attr="billing_cycle_days",
            name="Billing cycle days",
            icon="mdi:credit-card-sync",
            unit=UnitOfTime.DAYS,
            state_class=SensorStateClass.MEASUREMENT,
            display_precision=0,
        ),
    ]


class MeinVodafoneEntities:
    """Class for accessing the entities."""

    def __init__(self, contract: MeinVodafoneContract) -> None:
        """Initialize instruments."""
        self.entities_list: list[Sensor] = []

        for entity in create_entities():
            if entity.setup(contract):
                self.entities_list.append(entity)
