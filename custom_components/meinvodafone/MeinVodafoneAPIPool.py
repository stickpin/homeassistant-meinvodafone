"""Shared API session pool for MeinVodafone integration."""

from __future__ import annotations

import logging

from .MeinVodafoneAPI import MeinVodafoneAPI

_LOGGER = logging.getLogger(__name__)


class MeinVodafoneAPIPool:
    """Pool to manage shared API sessions by username."""

    def __init__(self) -> None:
        """Initialize the API pool."""
        self._sessions: dict[str, MeinVodafoneAPI] = {}

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
        return api

    async def close_all(self) -> None:
        """Close all API sessions in the pool."""
        for username, api in self._sessions.items():
            _LOGGER.debug("Closing API session for user: %s", username)
            await api.close()
        self._sessions.clear()

    async def remove(self, username: str) -> None:
        """Remove and close a specific API session.

        Args:
            username: The username of the session to remove
        """
        if username in self._sessions:
            _LOGGER.debug("Removing API session for user: %s", username)
            await self._sessions[username].close()
            del self._sessions[username]
