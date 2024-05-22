"""MeinVodafone API."""

import logging
import time

from aiohttp import ClientSession

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


class MeinVodafoneAPI:
    """Main MeinVodafone API class to MeinVodafone services."""

    def __init__(self, username: str, password: str) -> None:
        """Init MeinVodafone API class."""
        self.username = username
        self.password = password
        self.contracts = {}
        self.random_string = ""
        self.code = ""
        self.session = ClientSession()

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
            url = MINT_HOST + "/rest/v60/session/start"
            headers = {
                "User-Agent": USER_AGENT,
            }

            async with self.session.post(
                url, headers=headers, json=payload
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", headers)
                _LOGGER.debug("Response headers: %s", response.headers)
                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.debug("Response: %s", response_data)
                    if response_data.get("userId", None):
                        return True
                else:
                    response_data = await response.text()
                    _LOGGER.error("Failed to login")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response_data,
                    )
                return False
        except Exception as error:
            _LOGGER.error("Error during the login proccess, error %s", error)
            return False

    async def get_contracts(self) -> list:
        """Get contracts API."""
        _LOGGER.debug("Getting contracts")

        contracts = []
        timestamp = "%d" % (time.time())

        try:
            url = API_HOST + "/vluxgate/vlux/hashing"

            headers = {
                "Referer": HEADER_REFERER,
                "User-Agent": USER_AGENT,
                "X-Vf-Api": timestamp,
                "X-Vf-Clientid": X_VF_CLIENT_ID,
            }

            async with self.session.get(
                url, headers=headers, allow_redirects=False
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", headers)
                _LOGGER.debug("Response headers: %s", response.headers)
                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.debug("Response: %s", response_data)
                    contracts_data = response_data.get("hashedIds", None)
                    if contracts_data:
                        for contract in contracts_data:
                            if contract.get("type", None) == "mobile":
                                contract_number = contract.get("id", None)
                                if contract_number:
                                    contracts.append(contract_number)
                else:
                    _LOGGER.error("Failed to retrieve contracts")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response.text,
                    )
        except Exception as error:
            _LOGGER.error(
                "Error during the contracts retrieval proccess, error %s", error
            )
        return contracts

    async def get_contract_usage(self, contract_number) -> dict:
        """Get usage data API."""
        _LOGGER.debug("Getting contract usage details")

        contract_usage_data = {
            BILLING: {},
            MINUTES: [],
            SMS: [],
            DATA: [],
        }

        try:
            url = API_HOST + f"/vluxgate/vlux/mobile/unbilledUsage/{contract_number}"

            timestamp = "%d" % (time.time())

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
            }

            async with self.session.get(
                url, headers=headers, allow_redirects=False
            ) as response:
                _LOGGER.debug("Request URL: %s", url)
                _LOGGER.debug("Request headers: %s", headers)
                _LOGGER.debug("Response headers: %s", response.headers)
                if response.status == 200:
                    response_data = await response.json()
                    _LOGGER.debug("Response: %s", response_data)
                    service_usage_vbo = response_data.get("serviceUsageVBO", {})
                    billing_details = service_usage_vbo.get("billDetails", {})

                    billing_currect_summary = billing_details.get(
                        "currentSummary", {}
                    ).get("amount")
                    billing_last_summary = billing_details.get("lastSummary", {}).get(
                        "amount"
                    )
                    billing_cycle_start = billing_details.get("billCycleStartDate")
                    billing_cycle_end = billing_details.get("billCycleEndDate")

                    contract_usage_data[BILLING] = {
                        CURRENT_SUMMARY: billing_currect_summary,
                        LAST_SUMMARY: billing_last_summary,
                        CYCLE_START: billing_cycle_start,
                        CYCLE_END: billing_cycle_end,
                    }

                    usage_accounts = service_usage_vbo.get("usageAccounts", [])
                    for account in usage_accounts:
                        usage_group = account.get("usageGroup", [])
                        for usage_data in usage_group:
                            container = usage_data.get("container", "")
                            if container in {"SMS", "Minuten", "Daten"}:
                                usage_details = usage_data.get("usage", [])
                                for usage_item in usage_details:
                                    data = {
                                        NAME: usage_item.get("name"),
                                        REMAINING: usage_item.get("remaining"),
                                        USED: usage_item.get("used"),
                                        TOTAL: usage_item.get("total"),
                                        LAST_UPDATE: usage_item.get("lastUpdateDate"),
                                    }
                                    container_name = name_mapping.get(container.lower())
                                    contract_usage_data[container_name].append(data)
                else:
                    if response.status == 401:
                        _LOGGER.debug("User appears unauthorized")
                    else:
                        _LOGGER.error("Failed to retrieve contract usage details")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response.text,
                    )
                    return {
                        "status_code": response.status,
                        "error_message": response.text,
                    }
        except Exception as error:
            _LOGGER.error(
                "Error during the contract usage details retrieval proccess, error %s",
                error,
            )
            return {
                "status_code": None,
                "error_message": error,
            }
        return {"status_code": response.status, "usage_data": contract_usage_data}
