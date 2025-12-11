"""Shared API session pool for MeinVodafone integration."""

from __future__ import annotations

import asyncio
import logging
import time

from .MeinVodafoneAPI import MeinVodafoneAPI
from .const import (
    MIN_LOGIN_DELAY,
)

_LOGGER = logging.getLogger(__name__)


class MeinVodafoneAPIPool:
    """Pool to manage shared API sessions by username."""

    def __init__(self) -> None:
        """Initialize the API pool."""
        self._sessions: dict[str, MeinVodafoneAPI] = {}
        self._login_locks: dict[str, asyncio.Lock] = {}
        self._last_login_time: dict[str, float] = {}

    def get_or_create(self, username: str, password: str) -> MeinVodafoneAPI:
        """Get existing API session or create new one.

        Args:
            username: The username for authentication
            password: The password for authentication

        Returns:
            Shared or new MeinVodafoneAPI instance
        """
        if username in self._sessions:
            _LOGGER.debug("Reusing existing API session for user: %s", username)
            return self._sessions[username]

        _LOGGER.debug("Creating new API session for user: %s", username)
        api = MeinVodafoneAPI(username, password)
        self._sessions[username] = api

        # Initialize lock for this username
        if username not in self._login_locks:
            self._login_locks[username] = asyncio.Lock()

        return api

    async def ensure_authenticated(self, api: MeinVodafoneAPI, username: str) -> bool:
        """Ensure API is authenticated, login only if needed.

        Args:
            api: The API instance to check/authenticate
            username: The username (used for tracking)

        Returns:
            True if authenticated, False otherwise
        """
        # Get or create lock for this username
        if username not in self._login_locks:
            self._login_locks[username] = asyncio.Lock()

        lock = self._login_locks[username]

        async with lock:
            # Check if already authenticated
            if api.is_authenticated:
                _LOGGER.debug("API session already authenticated for %s", username)
                return True

            # Check if we need to wait before next login
            last_login = self._last_login_time.get(username, 0)
            time_since_last = time.time() - last_login

            if time_since_last < MIN_LOGIN_DELAY:
                delay = MIN_LOGIN_DELAY - time_since_last
                _LOGGER.debug(
                    "Rate limiting login for %s: waiting %.1f seconds", username, delay
                )
                await asyncio.sleep(delay)

            # Perform login
            _LOGGER.debug("Performing login for user: %s", username)
            result = await api.login()

            # Update last login time
            self._last_login_time[username] = time.time()

            return result

    async def close_all(self) -> None:
        """Close all API sessions in the pool."""
        for username, api in self._sessions.items():
            _LOGGER.debug("Closing API session for user: %s", username)
            await api.close()
        self._sessions.clear()
        self._login_locks.clear()
        self._last_login_time.clear()

    async def remove(self, username: str) -> None:
        """Remove and close a specific API session.

        Args:
            username: The username of the session to remove
        """
        if username in self._sessions:
            _LOGGER.debug("Removing API session for user: %s", username)
            await self._sessions[username].close()
            del self._sessions[username]

        # Clean up locks and timing info
        if username in self._login_locks:
            del self._login_locks[username]
        if username in self._last_login_time:
            del self._last_login_time[username]
