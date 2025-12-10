"""MeinVodafone API."""

import logging
import time
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    API_HOST,
    BILLING,
    CURRENT_SUMMARY,
    CYCLE_END,
    CYCLE_START,
    DATA,
    HEADER_REFERER,
    LAST_SUMMARY,
    LAST_UPDATE,
    MINT_HOST,
    MINUTES,
    NAME,
    REMAINING,
    SMS,
    TOTAL,
    USED,
    USER_AGENT,
    X_VF_CLIENT_ID,
)

_LOGGER = logging.getLogger(__name__)

API_TIMEOUT = 60  # seconds


class MeinVodafoneAPI:
    """Main MeinVodafone API class to MeinVodafone services."""

    def __init__(self, username: str, password: str) -> None:
        """Init MeinVodafone API class."""
        self.username = username
        self.password = password
        self.session = ClientSession()

    async def close(self) -> None:
        """Close the API session."""
        if self.session:
            await self.session.close()

    async def login(self) -> bool:
        """Start session API."""
        _LOGGER.debug("Initiating new login")

        try:
            payload = {
                "authnIdentifier": self.username,
                "credential": self.password,
                "context": "",
                "conversation": "",
                "targetURL": "",
            }
            url = f"{MINT_HOST}/rest/v60/session/start"
            headers = {
                "User-Agent": USER_AGENT,
            }

            async with self.session.post(
                url, headers=headers, json=payload, timeout=API_TIMEOUT
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", headers)
                _LOGGER.debug("Response headers: %s", response.headers)

                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.debug("Response: %s", response_data)
                    if response_data.get("userId"):
                        return True
                else:
                    response_text = await response.text()
                    _LOGGER.error("Failed to login")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response_text,
                    )
                return False
        except ClientError as error:
            _LOGGER.error("Network error during login: %s", error)
            return False
        except Exception as error:
            _LOGGER.error("Error during the login process: %s", error)
            return False

    async def get_contracts(self) -> list[str]:
        """Get contracts API."""
        _LOGGER.debug("Getting contracts")

        contracts: list[str] = []
        timestamp = f"{int(time.time())}"

        try:
            url = f"{API_HOST}/vluxgate/vlux/hashing"

            headers = {
                "Referer": HEADER_REFERER,
                "User-Agent": USER_AGENT,
                "X-Vf-Api": timestamp,
                "X-Vf-Clientid": X_VF_CLIENT_ID,
            }

            async with self.session.get(
                url, headers=headers, allow_redirects=False, timeout=API_TIMEOUT
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", headers)
                _LOGGER.debug("Response headers: %s", response.headers)

                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.debug("Response: %s", response_data)
                    contracts_data = response_data.get("hashedIds")

                    if contracts_data:
                        for contract in contracts_data:
                            if contract.get("type") == "mobile":
                                contract_number = contract.get("id")
                                if contract_number:
                                    contracts.append(contract_number)
                else:
                    response_text = await response.text()
                    _LOGGER.error("Failed to retrieve contracts")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response_text,
                    )
        except ClientError as error:
            _LOGGER.error("Network error during contract retrieval: %s", error)
        except Exception as error:
            _LOGGER.error("Error during the contract retrieval process: %s", error)

        return contracts

    async def get_contract_usage(self, contract_number: str) -> dict[str, Any]:
        """Get usage data API."""
        if not contract_number:
            _LOGGER.error("Contract number is required")
            return {
                "status_code": None,
                "error_message": "Contract number is required",
            }

        _LOGGER.debug("Getting contract usage details for %s", contract_number)

        contract_usage_data: dict[str, Any] = {
            BILLING: {},
            MINUTES: [],
            SMS: [],
            DATA: [],
        }

        try:
            url = f"{API_HOST}/vluxgate/vlux/mobile/unbilledUsage/{contract_number}"
            timestamp = f"{int(time.time())}"

            headers = {
                "Referer": HEADER_REFERER,
                "User-Agent": USER_AGENT,
                "X-Vf-Api": timestamp,
                "X-Vf-Clientid": X_VF_CLIENT_ID,
            }

            name_mapping = {
                "minuten": MINUTES,
                "sms": SMS,
                "daten": DATA,
                "d_eu_data": DATA,
                "d_eu_flat_allnet_units": MINUTES,
                "d_int_units": SMS,
            }

            async with self.session.get(
                url, headers=headers, allow_redirects=False, timeout=API_TIMEOUT
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", headers)
                _LOGGER.debug("Response headers: %s", response.headers)

                status_code = response.status

                if status_code == 200:
                    response_data = await response.json()
                    _LOGGER.debug("Response: %s", response_data)
                    service_usage_vbo = response_data.get("serviceUsageVBO", {})
                    billing_details = service_usage_vbo.get("billDetails")

                    if billing_details:
                        billing_current_summary = billing_details.get(
                            "currentSummary", {}
                        ).get("amount")
                        billing_last_summary = billing_details.get(
                            "lastSummary", {}
                        ).get("amount")
                        billing_cycle_start = billing_details.get("billCycleStartDate")
                        billing_cycle_end = billing_details.get("billCycleEndDate")

                        contract_usage_data[BILLING] = {
                            CURRENT_SUMMARY: billing_current_summary,
                            LAST_SUMMARY: billing_last_summary,
                            CYCLE_START: billing_cycle_start,
                            CYCLE_END: billing_cycle_end,
                        }
                    else:
                        _LOGGER.debug("No billing details found, skipping.")

                    usage_accounts = service_usage_vbo.get("usageAccounts", [])
                    for account in usage_accounts:
                        usage_group = account.get("usageGroup", [])
                        for usage_data in usage_group:
                            container = usage_data.get("container", "")
                            container_name = name_mapping.get(container.lower())
                            if container_name:
                                aggregation = usage_data.get("vluxgateAgg")
                                if aggregation:
                                    # Handle aggregated usage data
                                    last_update_time = None
                                    usage_details = usage_data.get("usage", [])
                                    unit_of_measure = "MB"

                                    if usage_details:
                                        last_update_time = usage_details[0].get(
                                            "lastUpdateDate"
                                        )
                                        unit_of_measure = usage_details[0].get(
                                            "unitOfMeasure", "MB"
                                        )

                                    remaining = aggregation.get("aggregateRemaining")
                                    used = aggregation.get("aggregateUsed")
                                    total = aggregation.get("aggregateTotal")

                                    # Validate aggregated values
                                    if not self._validate_usage_values(
                                        remaining, used, total, unit_of_measure
                                    ):
                                        _LOGGER.debug(
                                            "Skipping aggregated values with suspicious data"
                                        )
                                        continue

                                    data = {
                                        NAME: aggregation.get("name"),
                                        REMAINING: remaining,
                                        USED: used,
                                        TOTAL: total,
                                        LAST_UPDATE: last_update_time,
                                    }
                                    contract_usage_data[container_name].append(data)
                                else:
                                    # Handle individual usage items
                                    usage_details = usage_data.get("usage", [])
                                    for usage_item in usage_details:
                                        unit_of_measure = usage_item.get(
                                            "unitOfMeasure", "MB"
                                        )
                                        remaining = usage_item.get("remaining")
                                        used = usage_item.get("used")
                                        total = usage_item.get("total")

                                        # Validate individual item values
                                        if not self._validate_usage_values(
                                            remaining, used, total, unit_of_measure
                                        ):
                                            _LOGGER.debug(
                                                "Skipping usage item with suspicious values: %s",
                                                usage_item.get("name"),
                                            )
                                            continue

                                        data = {
                                            NAME: usage_item.get("name"),
                                            REMAINING: remaining,
                                            USED: used,
                                            TOTAL: total,
                                            LAST_UPDATE: usage_item.get(
                                                "lastUpdateDate"
                                            ),
                                        }
                                        contract_usage_data[container_name].append(data)

                    return {
                        "status_code": status_code,
                        "usage_data": contract_usage_data,
                    }
                else:
                    response_text = await response.text()
                    if status_code == 401:
                        _LOGGER.debug("User appears unauthorized")
                    else:
                        _LOGGER.error("Failed to retrieve contract usage details")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        status_code,
                        response_text,
                    )
                    return {
                        "status_code": status_code,
                        "error_message": response_text,
                    }
        except ClientError as error:
            _LOGGER.error("Network error during contract usage retrieval: %s", error)
            return {
                "status_code": None,
                "error_message": str(error),
            }
        except Exception as error:
            _LOGGER.error(
                "Error during the contract usage details retrieval: %s",
                error,
            )
            return {
                "status_code": None,
                "error_message": str(error),
            }

    def _validate_usage_values(
        self, remaining: Any, used: Any, total: Any, unit: str
    ) -> bool:
        """Validate remaining, used, and total usage values.

        Args:
            remaining: The remaining value
            used: The used value
            total: The total value
            unit: The unit of measure

        Returns:
            True if all values are valid, False otherwise
        """
        return all(
            [
                self._is_valid_data_value(remaining, unit),
                self._is_valid_data_value(used, unit),
                self._is_valid_data_value(total, unit),
            ]
        )

    def _is_valid_data_value(self, value: str | int | None, unit: str) -> bool:
        """Validate data values to detect incorrect/glitched values.

        Args:
            value: The numeric value as string or int
            unit: The reported unit of measure

        Returns:
            True if value seems valid, False if suspicious
        """
        if value is None:
            return True  # None is acceptable

        try:
            numeric_value = int(value)

            # Flag suspicious values: if reported as MB but > 500000 (~500GB)
            # it's likely a server glitch reporting KB as MB
            if unit == "MB" and numeric_value > 500000:
                _LOGGER.warning(
                    "Ignoring suspicious data value: %s %s (likely server glitch)",
                    numeric_value,
                    unit,
                )
                return False

            return True
        except (ValueError, TypeError):
            _LOGGER.warning("Invalid data value format: %s", value)
            return False
