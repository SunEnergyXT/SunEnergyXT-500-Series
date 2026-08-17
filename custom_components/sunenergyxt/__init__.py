"""
SunEnergyXT 500 Series integration for Home Assistant.

This module handles the setup and configuration of the SunEnergyXT integration,
including device connection testing, coordinator initialization, and platform setup.

Modules:
- const: Contains constant definitions for the integration
- coordinator: Handles data updates from the SunEnergyXT device
- sensor: Implements sensor entities
- number: Implements number entities
- button: Implements button entities
- switch: Implements switch entities
- text: Implements text entities
"""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

import aiohttp
import async_timeout
from homeassistant.const import Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    MAX_POLLING_INTERVAL,
    MIN_POLLING_INTERVAL,
)
from .coordinator import SunlitDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.TEXT,
]
CONFIG_SCHEMA = cv.empty_config_schema(domain=DOMAIN)


async def _test_connection(ip: str) -> None:
    """
    Test connection to the SunEnergyXT device.

    Args:
        ip: IP address of the device

    Raises:
        RuntimeError: If connection fails or device returns an error

    """
    try:
        async with async_timeout.timeout(5), aiohttp.ClientSession() as session:
            async with session.get(f"http://{ip}/read") as resp:
                if resp.status != HTTPStatus.OK:
                    msg = f"HTTP status {resp.status}"
                    raise RuntimeError(msg)
                await resp.json()
    except Exception as err:
        msg = f"Cannot connect to device at {ip}: {err}"
        raise RuntimeError(msg) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Set up SunEnergyXT from a config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry containing device information

    Returns:
        True if setup was successful

    Raises:
        ConfigEntryNotReady: If the device is not ready

    """
    hass.data.setdefault(DOMAIN, {})
    sn = entry.data.get("sn")
    ip = entry.data.get("ip")
    model = entry.data.get("model")

    try:
        await _test_connection(ip)
    except Exception as err:
        _LOGGER.warning("Device %s (%s) not ready: %s", sn, ip, err)
        msg = f"Device not ready: {err}"
        raise ConfigEntryNotReady(msg) from err

    try:
        polling_interval = int(
            entry.options.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)
        )
    except (TypeError, ValueError):
        polling_interval = DEFAULT_POLLING_INTERVAL
    polling_interval = max(
        MIN_POLLING_INTERVAL,
        min(MAX_POLLING_INTERVAL, polling_interval),
    )
    coordinator = SunlitDataUpdateCoordinator(
        hass=hass,
        sn=sn,
        ip=ip,
        polling_interval=polling_interval,
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "sn": sn,
        "ip": ip,
        "model": model,
        "coordinator": coordinator,
    }
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """
    Unload a SunEnergyXT config entry.

    Args:
        hass: Home Assistant instance
        entry: Config entry to unload

    Returns:
        True if unload was successful

    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration after an options change."""
    await hass.config_entries.async_reload(entry.entry_id)
