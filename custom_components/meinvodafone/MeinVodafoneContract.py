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

    def get_value(self, container: str, key: str, index: int | None = None) -> str | None:
        """Return value if found in the usage data."""
        container_data = self.usage_data.get(container, None)
        if index is not None and container_data and 0 <= index < len(container_data):
            return container_data[index].get(key)
        return container_data.get(key, None)

    #
    # MINUTES - Primary plan
    #

    # Minutes - Primary plan - Name
    @property
    def primary_minutes_name(self):
        """Return name of the primary plan."""
        return self.get_value(MINUTES, NAME, 0)

    # Minutes - Primary plan - Remaining
    @property
    def primary_minutes_remaining(self):
        """Return remaining minutes for the primary plan."""
        return self.get_value(MINUTES, REMAINING, 0)

    @property
    def primary_minutes_remaining_last_update(self):
        """Return remaining minutes for the primary plan last update timestamp."""
        return self.get_value(MINUTES, LAST_UPDATE, 0)

    @property
    def is_primary_minutes_remaining_supported(self):
        """Return true if remaining minutes for the primary plan is supported."""
        if self.get_value(MINUTES, REMAINING, 0):
            return True
        return False

    # Minutes - Primary plan - Used
    @property
    def primary_minutes_used(self):
        """Return used minutes for the primary plan."""
        return self.get_value(MINUTES, USED, 0)

    @property
    def primary_minutes_used_last_update(self):
        """Return used minutes for the primary plan last update timestamp."""
        return self.get_value(MINUTES, LAST_UPDATE, 0)

    @property
    def is_primary_minutes_used_supported(self):
        """Return true if used minutes for the primary plan is supported."""
        if self.get_value(MINUTES, USED, 0):
            return True
        return False

    # Minutes - Primary plan - Total
    @property
    def primary_minutes_total(self):
        """Return total minutes for the primary plan."""
        return self.get_value(MINUTES, TOTAL, 0)

    @property
    def primary_minutes_total_last_update(self):
        """Return total minutes for the primary plan last update timestamp."""
        return self.get_value(MINUTES, LAST_UPDATE, 0)

    @property
    def is_primary_minutes_total_supported(self):
        """Return true if total minutes for the primary plan is supported."""
        if self.get_value(MINUTES, TOTAL, 0):
            return True
        return False

    #
    # MINUTES - Secondary plan
    #

    # Minutes - Secondary plan - Name
    @property
    def secondary_minutes_name(self):
        """Return name of the secondary plan."""
        return self.get_value(MINUTES, NAME, 1)

    # Minutes - Secondary plan - Remaining
    @property
    def secondary_minutes_remaining(self):
        """Return remaining minutes for the secondary plan."""
        return self.get_value(MINUTES, REMAINING, 1)

    @property
    def secondary_minutes_remaining_last_update(self):
        """Return remaining minutes for the secondary plan last update timestamp."""
        return self.get_value(MINUTES, LAST_UPDATE, 1)

    @property
    def is_secondary_minutes_remaining_supported(self):
        """Return true if remaining minutes for the secondary plan is supported."""
        if self.get_value(MINUTES, REMAINING, 1):
            return True
        return False

    # Minutes - Secondary contract - Used
    @property
    def secondary_minutes_used(self):
        """Return used minutes for the secondary plan."""
        return self.get_value(MINUTES, USED, 1)

    @property
    def secondary_minutes_used_last_update(self):
        """Return used minutes for the secondary plan last update timestamp."""
        return self.get_value(MINUTES, LAST_UPDATE, 1)

    @property
    def is_secondary_minutes_used_supported(self):
        """Return true if used minutes for the secondary plan is supported."""
        if self.get_value(MINUTES, USED, 1):
            return True
        return False

    # Minutes - Secondary contract - Total
    @property
    def secondary_minutes_total(self):
        """Return total minutes for the secondary plan."""
        return self.get_value(MINUTES, TOTAL, 1)

    @property
    def secondary_minutes_total_last_update(self):
        """Return total minutes for the secondary plan last update timestamp."""
        return self.get_value(MINUTES, LAST_UPDATE, 1)

    @property
    def is_secondary_minutes_total_supported(self):
        """Return true if total minutes for the secondary plan is supported."""
        if self.get_value(MINUTES, TOTAL, 1):
            return True
        return False

    #
    # SMS - Primary plan
    #

    # SMS - Primary plan - Name
    @property
    def primary_sms_name(self):
        """Return name of the primary plan."""
        return self.get_value(SMS, NAME, 0)

    # SMS - Primary plan - Remaining
    @property
    def primary_sms_remaining(self):
        """Return remaining sms for the primary plan."""
        return self.get_value(SMS, REMAINING, 0)

    @property
    def primary_sms_remaining_last_update(self):
        """Return remaining sms for the primary plan last update timestamp."""
        return self.get_value(SMS, LAST_UPDATE, 0)

    @property
    def is_primary_sms_remaining_supported(self):
        """Return true if remaining sms for the primary plan is supported."""
        if self.get_value(SMS, REMAINING, 0):
            return True
        return False

    # SMS - Primary plan - Used
    @property
    def primary_sms_used(self):
        """Return used sms for the primary plan."""
        return self.get_value(SMS, USED, 0)

    @property
    def primary_sms_used_last_update(self):
        """Return used sms for the primary plan last update timestamp."""
        return self.get_value(SMS, LAST_UPDATE, 0)

    @property
    def is_primary_sms_used_supported(self):
        """Return true if used sms for the primary plan is supported."""
        if self.get_value(SMS, USED, 0):
            return True
        return False

    # SMS - Primary plan - Total
    @property
    def primary_sms_total(self):
        """Return total sms for the primary plan."""
        return self.get_value(SMS, TOTAL, 0)

    @property
    def primary_sms_total_last_update(self):
        """Return total sms for the primary plan last update timestamp."""
        return self.get_value(SMS, LAST_UPDATE, 0)

    @property
    def is_primary_sms_total_supported(self):
        """Return true if total sms for the primary plan is supported."""
        if self.get_value(SMS, TOTAL, 0):
            return True
        return False

    #
    # SMS - Secondary plan
    #

    # SMS - Secondary plan - Name
    @property
    def secondary_sms_name(self):
        """Return name of the secondary plan."""
        return self.get_value(SMS, NAME, 1)

    # SMS - Secondary plan - Remaining
    @property
    def secondary_sms_remaining(self):
        """Return remaining sms for the secondary plan."""
        return self.get_value(SMS, REMAINING, 1)

    @property
    def secondary_sms_remaining_last_update(self):
        """Return remaining sms for the secondary plan last update timestamp."""
        return self.get_value(SMS, LAST_UPDATE, 1)

    @property
    def is_secondary_sms_remaining_supported(self):
        """Return true if remaining sms for the secondary plan is supported."""
        if self.get_value(SMS, REMAINING, 1):
            return True
        return False

    # SMS - Secondary contract - Used
    @property
    def secondary_sms_used(self):
        """Return used sms for the secondary plan."""
        return self.get_value(SMS, USED, 1)

    @property
    def secondary_sms_used_last_update(self):
        """Return used sms for the secondary plan last update timestamp."""
        return self.get_value(SMS, LAST_UPDATE, 1)

    @property
    def is_secondary_sms_used_supported(self):
        """Return true if used sms for the secondary plan is supported."""
        if self.get_value(SMS, USED, 1):
            return True
        return False

    # SMS - Secondary contract - Total
    @property
    def secondary_sms_total(self):
        """Return total sms for the secondary plan."""
        return self.get_value(SMS, TOTAL, 1)

    @property
    def secondary_sms_total_last_update(self):
        """Return total sms for the secondary plan last update timestamp."""
        return self.get_value(SMS, LAST_UPDATE, 1)

    @property
    def is_secondary_sms_total_supported(self):
        """Return true if total sms for the secondary plan is supported."""
        if self.get_value(SMS, TOTAL, 1):
            return True
        return False

    #
    # DATA - Primary plan
    #

    # DATA - Primary plan - Name
    @property
    def primary_data_name(self):
        """Return name of the primary plan."""
        return self.get_value(DATA, NAME, 0)

    # DATA - Primary plan - Remaining
    @property
    def primary_data_remaining(self):
        """Return remaining data for the primary plan."""
        return self.get_value(DATA, REMAINING, 0)

    @property
    def primary_data_remaining_last_update(self):
        """Return remaining data for the primary plan last update timestamp."""
        return self.get_value(DATA, LAST_UPDATE, 0)

    @property
    def is_primary_data_remaining_supported(self):
        """Return true if remaining data for the primary plan is supported."""
        if self.get_value(DATA, REMAINING, 0):
            return True
        return False

    # DATA - Primary plan - Used
    @property
    def primary_data_used(self):
        """Return used data for the primary plan."""
        return self.get_value(DATA, USED, 0)

    @property
    def primary_data_used_last_update(self):
        """Return used data for the primary plan last update timestamp."""
        return self.get_value(DATA, LAST_UPDATE, 0)

    @property
    def is_primary_data_used_supported(self):
        """Return true if used data for the primary plan is supported."""
        if self.get_value(DATA, USED, 0):
            return True
        return False

    # DATA - Primary plan - Total
    @property
    def primary_data_total(self):
        """Return total data for the primary plan."""
        return self.get_value(DATA, TOTAL, 0)

    @property
    def primary_data_total_last_update(self):
        """Return total data for the primary plan last update timestamp."""
        return self.get_value(DATA, LAST_UPDATE, 0)

    @property
    def is_primary_data_total_supported(self):
        """Return true if total data for the primary plan is supported."""
        if self.get_value(DATA, TOTAL, 0):
            return True
        return False

    #
    # DATA - Secondary plan
    #

    # DATA - Secondary plan - Name
    @property
    def secondary_data_name(self):
        """Return name of the secondary plan."""
        return self.get_value(DATA, NAME, 1)

    # DATA - Secondary plan - Remaining
    @property
    def secondary_data_remaining(self):
        """Return remaining data for the secondary plan."""
        return self.get_value(DATA, REMAINING, 1)

    @property
    def secondary_data_remaining_last_update(self):
        """Return remaining data for the secondary plan last update timestamp."""
        return self.get_value(DATA, LAST_UPDATE, 1)

    @property
    def is_secondary_data_remaining_supported(self):
        """Return true if remaining data for the secondary plan is supported."""
        if self.get_value(DATA, REMAINING, 1):
            return True
        return False

    # DATA - Secondary contract - Used
    @property
    def secondary_data_used(self):
        """Return used data for the secondary plan."""
        return self.get_value(DATA, USED, 1)

    @property
    def secondary_data_used_last_update(self):
        """Return used data for the secondary plan last update timestamp."""
        return self.get_value(DATA, LAST_UPDATE, 1)

    @property
    def is_secondary_data_used_supported(self):
        """Return true if used data for the secondary plan is supported."""
        if self.get_value(DATA, USED, 1):
            return True
        return False

    # DATA - Secondary contract - Total
    @property
    def secondary_data_total(self):
        """Return total data for the secondary plan."""
        return self.get_value(DATA, TOTAL, 1)

    @property
    def secondary_data_total_last_update(self):
        """Return total data for the secondary plan last update timestamp."""
        return self.get_value(DATA, LAST_UPDATE, 1)

    @property
    def is_secondary_data_total_supported(self):
        """Return true if total data for the secondary plan is supported."""
        if self.get_value(DATA, TOTAL, 1):
            return True
        return False

    #
    # BILLING
    #

    # BILLING - Current Summary
    @property
    def billing_current_summary(self):
        """Return current billing summary."""
        return self.get_value(BILLING, CURRENT_SUMMARY)

    @property
    def billing_current_summary_last_update(self):
        """Return current billing summary last update timestamp."""
        return datetime.datetime.now(datetime.UTC)

    @property
    def is_billing_current_summary_supported(self):
        """Return true if current billing summary is supported."""
        if self.get_value(BILLING, CURRENT_SUMMARY):
            return True
        return False

    # BILLING - Last Summary
    @property
    def billing_last_summary(self):
        """Return last billing summary."""
        return self.get_value(BILLING, LAST_SUMMARY)

    @property
    def billing_last_summary_last_update(self):
        """Return last billing summary last update timestamp."""
        return datetime.datetime.now(datetime.UTC)

    @property
    def is_billing_last_summary_supported(self):
        """Return true if last billing summary is supported."""
        if self.get_value(BILLING, LAST_SUMMARY):
            return True
        return False

    # BILLING - Cycle Days
    @property
    def billing_cycle_days(self):
        """Return days until end of the billing cycle."""
        datetime_now = (
            datetime.datetime.now(datetime.UTC).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
        )
        cycle_end = datetime.datetime.strptime(self.billing_cycle_end, "%Y-%m-%d").replace(tzinfo=None)
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
        return self.get_value(BILLING, CYCLE_START)

    # BILLING - Cycle End Date
    @property
    def billing_cycle_end(self):
        """Return billing cycle end date."""
        return self.get_value(BILLING, CYCLE_END)
