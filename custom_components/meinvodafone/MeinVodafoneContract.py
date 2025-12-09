"""MeinVodafone Contract."""

import datetime
import logging
from typing import Any

from .const import (
    BILLING,
    CURRENT_SUMMARY,
    CYCLE_END,
    CYCLE_START,
    DATA,
    LAST_SUMMARY,
    LAST_UPDATE,
    MINUTES,
    NAME,
    REMAINING,
    SMS,
    TOTAL,
    USED,
)

_LOGGER = logging.getLogger(__name__)

# Date format constants
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
ISO_DATE_FORMAT = "%Y-%m-%d"


class MeinVodafoneContract:
    """Init MeinVodafone contract class."""

    def __init__(
        self,
        contract_id: str,
        usage_data: dict[str, Any],
    ) -> None:
        """Initialize MeinVodafone contract."""
        self.contract_id: str = contract_id
        self.usage_data: dict[str, Any] = usage_data

    def get_value(self, container: str, key: str | None = None) -> str | None:
        """Return summarized value for the usage data."""
        container_data = self.usage_data.get(container, [])

        if not container_data:
            return None

        if key == NAME:
            # Combine all names with a comma
            return ", ".join(
                [item.get(key, "") for item in container_data if item.get(key)]
            )
        if key == LAST_UPDATE:
            # Filter out None values and get the latest last_update timestamp
            valid_updates = [
                item.get(key) for item in container_data if item.get(key) is not None
            ]
            if not valid_updates:
                # Return the current datetime if no valid updates are found
                return datetime.datetime.now(datetime.timezone.utc).strftime(
                    ISO_DATETIME_FORMAT
                )
            return max(valid_updates)
        # Summarize numerical values
        total_value = sum(
            int(item.get(key, 0))
            for item in container_data
            if item.get(key) is not None
        )
        return str(total_value)

    def get_billing_value(self, key: str) -> str | None:
        """Return value from the billing information."""
        billing_data = self.usage_data.get(BILLING, {})
        return billing_data.get(key)

    def _get_datetime_from_value(
        self, container: str, key: str
    ) -> datetime.datetime | None:
        """Get datetime object from container value."""
        value = self.get_value(container, key)
        if value is None:
            return None
        try:
            return datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError) as err:
            _LOGGER.warning(
                "Failed to parse datetime from %s: %s - %s", container, value, err
            )
            return None

    def _create_usage_properties(self, container: str, metric_name: str):
        """Helper to reduce duplication (not directly implemented as Python lacks macros)."""
        # This is a conceptual helper - actual implementation would require
        # dynamic property generation or metaclass usage
        pass

    #
    # MINUTES
    #

    @property
    def minutes_name(self) -> str | None:
        """Return name of the plan."""
        return self.get_value(MINUTES, NAME)

    @property
    def minutes_remaining(self) -> str | None:
        """Return remaining minutes for the plan."""
        return self.get_value(MINUTES, REMAINING)

    @property
    def minutes_remaining_last_update(self) -> datetime.datetime | None:
        """Return remaining minutes for the plan last update timestamp."""
        return self._get_datetime_from_value(MINUTES, LAST_UPDATE)

    @property
    def is_minutes_remaining_supported(self) -> bool:
        """Return true if remaining minutes for the plan is supported."""
        return bool(self.get_value(MINUTES, REMAINING))

    @property
    def minutes_used(self) -> str | None:
        """Return used minutes for the plan."""
        return self.get_value(MINUTES, USED)

    @property
    def minutes_used_last_update(self) -> datetime.datetime | None:
        """Return used minutes for the plan last update timestamp."""
        return self._get_datetime_from_value(MINUTES, LAST_UPDATE)

    @property
    def is_minutes_used_supported(self) -> bool:
        """Return true if used minutes for the plan is supported."""
        return bool(self.get_value(MINUTES, USED))

    @property
    def minutes_total(self) -> str | None:
        """Return total minutes for the plan."""
        return self.get_value(MINUTES, TOTAL)

    @property
    def minutes_total_last_update(self) -> datetime.datetime | None:
        """Return total minutes for the plan last update timestamp."""
        return self._get_datetime_from_value(MINUTES, LAST_UPDATE)

    @property
    def is_minutes_total_supported(self) -> bool:
        """Return true if total minutes for the plan is supported."""
        return bool(self.get_value(MINUTES, TOTAL))

    #
    # SMS
    #

    @property
    def sms_name(self) -> str | None:
        """Return name of the primary plan."""
        return self.get_value(SMS, NAME)

    @property
    def sms_remaining(self) -> str | None:
        """Return remaining sms for the plan."""
        return self.get_value(SMS, REMAINING)

    @property
    def sms_remaining_last_update(self) -> datetime.datetime | None:
        """Return remaining sms for the plan last update timestamp."""
        return self._get_datetime_from_value(SMS, LAST_UPDATE)

    @property
    def is_sms_remaining_supported(self) -> bool:
        """Return true if remaining sms for the plan is supported."""
        return bool(self.get_value(SMS, REMAINING))

    @property
    def sms_used(self) -> str | None:
        """Return used sms for the plan."""
        return self.get_value(SMS, USED)

    @property
    def sms_used_last_update(self) -> datetime.datetime | None:
        """Return used sms for the plan last update timestamp."""
        return self._get_datetime_from_value(SMS, LAST_UPDATE)

    @property
    def is_sms_used_supported(self) -> bool:
        """Return true if used sms for the plan is supported."""
        return bool(self.get_value(SMS, USED))

    @property
    def sms_total(self) -> str | None:
        """Return total sms for the plan."""
        return self.get_value(SMS, TOTAL)

    @property
    def sms_total_last_update(self) -> datetime.datetime | None:
        """Return total sms for the plan last update timestamp."""
        return self._get_datetime_from_value(SMS, LAST_UPDATE)

    @property
    def is_sms_total_supported(self) -> bool:
        """Return true if total sms for the plan is supported."""
        return bool(self.get_value(SMS, TOTAL))

    #
    # DATA
    #

    @property
    def data_name(self) -> str | None:
        """Return name of the plan."""
        return self.get_value(DATA, NAME)

    @property
    def data_remaining(self) -> str | None:
        """Return remaining data for the plan."""
        return self.get_value(DATA, REMAINING)

    @property
    def data_remaining_last_update(self) -> datetime.datetime | None:
        """Return remaining data for the plan last update timestamp."""
        return self._get_datetime_from_value(DATA, LAST_UPDATE)

    @property
    def is_data_remaining_supported(self) -> bool:
        """Return true if remaining data for the plan is supported."""
        return bool(self.get_value(DATA, REMAINING))

    @property
    def data_used(self) -> str | None:
        """Return used data for the plan."""
        return self.get_value(DATA, USED)

    @property
    def data_used_last_update(self) -> datetime.datetime | None:
        """Return used data for the plan last update timestamp."""
        return self._get_datetime_from_value(DATA, LAST_UPDATE)

    @property
    def is_data_used_supported(self) -> bool:
        """Return true if used data for the plan is supported."""
        return bool(self.get_value(DATA, USED))

    @property
    def data_total(self) -> str | None:
        """Return total data for the plan."""
        return self.get_value(DATA, TOTAL)

    @property
    def data_total_last_update(self) -> datetime.datetime | None:
        """Return total data for the plan last update timestamp."""
        return self._get_datetime_from_value(DATA, LAST_UPDATE)

    @property
    def is_data_total_supported(self) -> bool:
        """Return true if total data for the plan is supported."""
        return bool(self.get_value(DATA, TOTAL))

    #
    # BILLING
    #

    @property
    def billing_current_summary(self) -> str | None:
        """Return current billing summary."""
        return self.get_billing_value(CURRENT_SUMMARY)

    @property
    def billing_current_summary_last_update(self) -> datetime.datetime:
        """Return current billing summary last update timestamp."""
        return datetime.datetime.now(datetime.timezone.utc)

    @property
    def is_billing_current_summary_supported(self) -> bool:
        """Return true if current billing summary is supported."""
        return bool(self.get_billing_value(CURRENT_SUMMARY))

    @property
    def billing_last_summary(self) -> str | None:
        """Return last billing summary."""
        return self.get_billing_value(LAST_SUMMARY)

    @property
    def billing_last_summary_last_update(self) -> datetime.datetime:
        """Return last billing summary last update timestamp."""
        return datetime.datetime.now(datetime.timezone.utc)

    @property
    def is_billing_last_summary_supported(self) -> bool:
        """Return true if last billing summary is supported."""
        return bool(self.get_billing_value(LAST_SUMMARY))

    @property
    def billing_cycle_days(self) -> int | None:
        """Return days until end of the billing cycle."""
        if not self.billing_cycle_end:
            return None

        try:
            datetime_now = datetime.datetime.now(datetime.timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cycle_end = datetime.datetime.strptime(
                self.billing_cycle_end, ISO_DATE_FORMAT
            ).replace(tzinfo=datetime.timezone.utc)
            delta = cycle_end - datetime_now
            return delta.days
        except (ValueError, TypeError) as err:
            _LOGGER.warning("Failed to calculate billing cycle days: %s", err)
            return None

    @property
    def billing_cycle_days_last_update(self) -> datetime.datetime:
        """Return days until end of the billing cycle last update timestamp."""
        return datetime.datetime.now(datetime.timezone.utc)

    @property
    def is_billing_cycle_days_supported(self) -> bool:
        """Return true if days until end of the billing cycle is supported."""
        return bool(self.billing_cycle_end)

    @property
    def billing_cycle_start(self) -> str | None:
        """Return billing cycle start date."""
        return self.get_billing_value(CYCLE_START)

    @property
    def billing_cycle_end(self) -> str | None:
        """Return billing cycle end date."""
        return self.get_billing_value(CYCLE_END)
