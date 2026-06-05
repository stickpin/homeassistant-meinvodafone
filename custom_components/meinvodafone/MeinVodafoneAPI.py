"""MeinVodafone API."""

import base64
import hashlib
import logging
import secrets
import time
import asyncio
from typing import Any
from functools import wraps
from aiohttp import ClientError, ClientSession

from .const import (
    API_HOST,
    API_TIMEOUT,
    BILLING,
    CLIENT_ID,
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


def retry_on_server_error(max_retries: int = 3, delay: int = 10):
    """Decorator to retry API calls on server errors (5xx status codes)."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)

                    # Check if result contains a status_code key indicating server error
                    if isinstance(result, dict) and "status_code" in result:
                        status_code = result.get("status_code")
                        if status_code and 500 <= status_code < 600:
                            if attempt < max_retries - 1:
                                _LOGGER.warning(
                                    "Server error (status %s) on attempt %d/%d, retrying in %d seconds...",
                                    status_code,
                                    attempt + 1,
                                    max_retries,
                                    delay,
                                )
                                await asyncio.sleep(delay)
                                continue
                            else:
                                _LOGGER.warning(
                                    "Server error (status %s) after %d attempts, giving up",
                                    status_code,
                                    max_retries,
                                )

                    return result
                except Exception as error:
                    last_error = error
                    if attempt < max_retries - 1:
                        _LOGGER.warning(
                            "Error on attempt %d/%d: %s, retrying in %d seconds...",
                            attempt + 1,
                            max_retries,
                            error,
                            delay,
                        )
                        await asyncio.sleep(delay)
                    else:
                        _LOGGER.error("Error after %d attempts: %s", max_retries, error)
                        raise

            if last_error:
                raise last_error
            return result

        return wrapper

    return decorator


class MeinVodafoneAPI:
    """Main MeinVodafone API class to MeinVodafone services."""

    def __init__(self, username: str, password: str) -> None:
        """Init MeinVodafone API class."""
        self.username = username
        self.password = password
        self.session = ClientSession()
        self.is_authenticated = False

    def _generate_code_verifier(self) -> str:
        """Generate a random code verifier for PKCE.

        Returns:
            43-character random string using alphanumeric and special chars
        """
        # Characters allowed in code verifier (unreserved characters from RFC 3986)
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz-._~"
        # Generate 43 random characters
        code_verifier = "".join(secrets.choice(chars) for _ in range(43))
        _LOGGER.debug("Generated code_verifier: %s", code_verifier)
        return code_verifier

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """Generate code challenge from code verifier using SHA256.

        Args:
            code_verifier: The random code verifier string

        Returns:
            Base64-URL-encoded SHA256 hash of the code verifier
        """
        # SHA256 hash the code verifier
        sha256_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()

        # Base64 encode
        base64_encoded = base64.b64encode(sha256_hash).decode("utf-8")

        # URL-safe base64: replace +/= with -_
        code_challenge = (
            base64_encoded.replace("+", "-").replace("/", "_").replace("=", "")
        )

        _LOGGER.debug("Generated code_challenge: %s", code_challenge)
        return code_challenge

    async def close(self) -> None:
        """Close the API session."""
        if self.session:
            await self.session.close()
        self.is_authenticated = False

    async def login(self) -> bool:
        """Start session API with two-step authentication."""
        _LOGGER.debug("Initiating new login for %s", self.username)

        try:
            # Step 1: Call OIDC authorize to get cookies
            code_verifier = self._generate_code_verifier()
            code_challenge = self._generate_code_challenge(code_verifier)

            authorize_url = (
                f"{MINT_HOST}/oidc/authorize"
                f"?response_type=code"
                f"&client_id={CLIENT_ID}"
                f"&scope=openid%20profile%20validate-token%20offline_access%20webseal"
                f"&redirect_uri=mvapp://oidclogin"
                f"&code_challenge={code_challenge}"
                f"&code_challenge_method=S256"
                f"&prompt=none"
            )

            _LOGGER.debug("Step 1: Calling OIDC authorize to collect cookies")
            async with self.session.get(
                authorize_url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
                timeout=API_TIMEOUT,
                allow_redirects=False,
            ) as response:
                _LOGGER.debug("OIDC authorize status: %s", response.status)
                _LOGGER.debug("Cookies collected: %s", self.session.cookie_jar)

                if response.status not in (200, 302):
                    _LOGGER.error("Failed to call OIDC authorize: %s", response.status)
                    self.is_authenticated = False
                    return False

            # Step 2: Use collected cookies to authenticate via API
            _LOGGER.debug("Step 2: Authenticating with collected cookies")
            payload = {
                "authnIdentifier": self.username,
                "credential": self.password,
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
                        self.is_authenticated = True
                        _LOGGER.debug("Login successful for user: %s", self.username)
                        return True
                else:
                    response_text = await response.text()
                    _LOGGER.error("Failed to login")
                    _LOGGER.debug(
                        "Not success status code [%s] response: %s",
                        response.status,
                        response_text,
                    )
                self.is_authenticated = False
                return False
        except ClientError as error:
            _LOGGER.error("Network error during login: %s", error)
            self.is_authenticated = False
            return False
        except Exception as error:
            _LOGGER.error("Error during the login process: %s", error)
            self.is_authenticated = False
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

    @retry_on_server_error(max_retries=5, delay=10)
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
