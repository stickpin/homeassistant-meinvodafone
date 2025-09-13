"""MeinVodafone Contract."""

import datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

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


class MeinVodafoneContract:
    """Init MeinVodafone contract class."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        contract_id: str,
        usage_data: dict,
    ) -> None:
        """Initialize MeinVodafone contract."""
        self.hass = hass
        self.config_entry: ConfigEntry = config_entry
        self.contract_id: contract_id

        self.usage_data = usage_data

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
                return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%S")
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
        return billing_data.get(key, None)

    #
    # MINUTES
    #

    # Minutes - Plan name
    @property
    def minutes_name(self):
        """Return name of the plan."""
        return self.get_value(MINUTES, NAME)

    # Minutes - Remaining
    @property
    def minutes_remaining(self):
        """Return remaining minutes for the plan."""
        return self.get_value(MINUTES, REMAINING)

    @property
    def minutes_remaining_last_update(self):
        """Return remaining minutes for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(MINUTES, LAST_UPDATE))

    @property
    def is_minutes_remaining_supported(self):
        """Return true if remaining minutes for the plan is supported."""
        if self.get_value(MINUTES, REMAINING):
            return True
        return False

    # Minutes - Used
    @property
    def minutes_used(self):
        """Return used minutes for the plan."""
        return self.get_value(MINUTES, USED)

    @property
    def minutes_used_last_update(self):
        """Return used minutes for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(MINUTES, LAST_UPDATE))

    @property
    def is_minutes_used_supported(self):
        """Return true if used minutes for the plan is supported."""
        if self.get_value(MINUTES, USED):
            return True
        return False

    # Minutes - Total
    @property
    def minutes_total(self):
        """Return total minutes for the plan."""
        return self.get_value(MINUTES, TOTAL)

    @property
    def minutes_total_last_update(self):
        """Return total minutes for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(MINUTES, LAST_UPDATE))

    @property
    def is_minutes_total_supported(self):
        """Return true if total minutes for the plan is supported."""
        if self.get_value(MINUTES, TOTAL):
            return True
        return False

    #
    # SMS
    #

    # SMS - Plan name
    @property
    def sms_name(self):
        """Return name of the primary plan."""
        return self.get_value(SMS, NAME)

    # SMS - Remaining
    @property
    def sms_remaining(self):
        """Return remaining sms for the plan."""
        return self.get_value(SMS, REMAINING)

    @property
    def sms_remaining_last_update(self):
        """Return remaining sms for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(SMS, LAST_UPDATE))

    @property
    def is_sms_remaining_supported(self):
        """Return true if remaining sms for the plan is supported."""
        if self.get_value(SMS, REMAINING):
            return True
        return False

    # SMS - Used
    @property
    def sms_used(self):
        """Return used sms for the plan."""
        return self.get_value(SMS, USED)

    @property
    def sms_used_last_update(self):
        """Return used sms for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(SMS, LAST_UPDATE))

    @property
    def is_sms_used_supported(self):
        """Return true if used sms for the plan is supported."""
        if self.get_value(SMS, USED):
            return True
        return False

    # SMS - Total
    @property
    def sms_total(self):
        """Return total sms for the plan."""
        return self.get_value(SMS, TOTAL)

    @property
    def sms_total_last_update(self):
        """Return total sms for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(SMS, LAST_UPDATE))

    @property
    def is_sms_total_supported(self):
        """Return true if total sms for the plan is supported."""
        if self.get_value(SMS, TOTAL):
            return True
        return False

    #
    # DATA
    #

    # DATA - Plan ame
    @property
    def data_name(self):
        """Return name of the plan."""
        return self.get_value(DATA, NAME)

    # DATA - Remaining
    @property
    def data_remaining(self):
        """Return remaining data for the plan."""
        return self.get_value(DATA, REMAINING)

    @property
    def data_remaining_last_update(self):
        """Return remaining data for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(DATA, LAST_UPDATE))

    @property
    def is_data_remaining_supported(self):
        """Return true if remaining data for the plan is supported."""
        if self.get_value(DATA, REMAINING):
            return True
        return False

    # DATA - Used
    @property
    def data_used(self):
        """Return used data for the plan."""
        return self.get_value(DATA, USED)

    @property
    def data_used_last_update(self):
        """Return used data for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(DATA, LAST_UPDATE))

    @property
    def is_data_used_supported(self):
        """Return true if used data for the plan is supported."""
        if self.get_value(DATA, USED):
            return True
        return False

    # DATA - Total
    @property
    def data_total(self):
        """Return total data for the plan."""
        return self.get_value(DATA, TOTAL)

    @property
    def data_total_last_update(self):
        """Return total data for the plan last update timestamp."""
        return datetime.datetime.fromisoformat(self.get_value(DATA, LAST_UPDATE))

    @property
    def is_data_total_supported(self):
        """Return true if total data for the plan is supported."""
        if self.get_value(DATA, TOTAL):
            return True
        return False

    #
    # BILLING
    #

    # BILLING - Current Summary
    @property
    def billing_current_summary(self):
        """Return current billing summary."""
        return self.get_billing_value(CURRENT_SUMMARY)

    @property
    def billing_current_summary_last_update(self):
        """Return current billing summary last update timestamp."""
        return datetime.datetime.now(datetime.UTC)

    @property
    def is_billing_current_summary_supported(self):
        """Return true if current billing summary is supported."""
        if self.get_billing_value(CURRENT_SUMMARY):
            return True
        return False

    # BILLING - Last Summary
    @property
    def billing_last_summary(self):
        """Return last billing summary."""
        return self.get_billing_value(LAST_SUMMARY)

    @property
    def billing_last_summary_last_update(self):
        """Return last billing summary last update timestamp."""
        return datetime.datetime.now(datetime.UTC)

    @property
    def is_billing_last_summary_supported(self):
        """Return true if last billing summary is supported."""
        if self.get_billing_value(LAST_SUMMARY):
            return True
        return False

    # BILLING - Cycle Days
    @property
    def billing_cycle_days(self):
        """Return days until end of the billing cycle."""
        datetime_now = datetime.datetime.now(datetime.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cycle_end = datetime.datetime.strptime(
            self.billing_cycle_end, "%Y-%m-%d"
        ).replace(tzinfo=datetime.UTC)
        delta = cycle_end - datetime_now

        return delta.days

    @property
    def billing_cycle_days_last_update(self):
        """Return days until end of the billing cycle last update timestamp."""
        return datetime.datetime.now(datetime.UTC)

    @property
    def is_billing_cycle_days_supported(self):
        """Return true if days until end of the billing cycle is supported."""
        if self.billing_cycle_end:
            return True
        return False

    # BILLING - Cycle Start Date
    @property
    def billing_cycle_start(self):
        """Return billing cycle start date."""
        return self.get_billing_value(CYCLE_START)

    # BILLING - Cycle End Date
    @property
    def billing_cycle_end(self):
        """Return billing cycle end date."""
        return self.get_billing_value(CYCLE_END)
