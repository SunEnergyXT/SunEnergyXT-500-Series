"""
Data update coordinator for SunEnergyXT 500 Series integration.

This module implements the data update coordinator for the SunEnergyXT integration,
responsible for fetching and updating data from the device at regular intervals.

Classes:
- SunlitDataUpdateCoordinator: Handles data updates from SunEnergyXT devices
"""

import logging
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from typing import Any

import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)


class SunlitDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """
    Data update coordinator for SunEnergyXT devices.

    Handles fetching and updating data from the device at regular intervals.
    """

    def __init__(self, hass: HomeAssistant, sn: str, ip: str) -> None:
        """
        Initialize the data update coordinator.

        Args:
            hass: Home Assistant instance
            sn: Device serial number
            ip: Device IP address

        """
        self._sn = sn
        self._ip = ip
        self._session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=f"SunlitMonitor-{sn}",
            update_interval=timedelta(seconds=3),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """
        Fetch data from the SunEnergyXT device.

        Returns:
            Dictionary containing the reported device data

        Raises:
            RuntimeError: If there's an error fetching or processing the data

        """
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(f"http://{self._ip}/read") as resp:
                    if resp.status != HTTPStatus.OK:
                        msg = f"HTTP status {resp.status}"
                        raise RuntimeError(msg)

                    data = await resp.json()

                    reported = data.get("state", {}).get("reported", {})

                    if not isinstance(reported, dict):
                        msg = "Invalid 'reported' structure in JSON"
                        raise TypeError(msg)

                    self.last_success_time = datetime.now(UTC)
                    _LOGGER.debug("Get raw data: %s", str(data))
                    return reported
        except (aiohttp.ClientConnectorError, TimeoutError, OSError) as err:
            _LOGGER.warning("Cannot connect to device (%s): %s", self._ip, err)
            msg = "Cannot connect"
            raise UpdateFailed(msg) from None
        except Exception as err:
            _LOGGER.exception("Error updating SunEnergyXT Monitor data: %s", err)
            raise
