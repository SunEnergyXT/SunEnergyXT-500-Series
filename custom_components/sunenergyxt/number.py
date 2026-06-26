"""
Number entities for SunEnergyXT 500 Series integration.

This module implements number entities for the SunEnergyXT integration,
allowing control of various device parameters such as power limits and percentages.

Classes:
- SunlitNumber: Represents a number entity for controlling SunEnergyXT device parameters

Constants:
- NUMBER_META: Metadata configuration for number entities, including min/max values,
  steps, and units
"""

import logging
from http import HTTPStatus
from typing import Any

import async_timeout
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunlitDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

NUMBER_META: dict[str, dict[str, Any]] = {
    "GS": {
        "min_value": -2400,
        "max_value": 2400,
        "step": 10,
        "unit": "W",
        "icon": "mdi:transmission-tower",
    },
    "IS": {
        "min_value": 1,
        "max_value": 2400,
        "step": 10,
        "unit": "W",
        "icon": "mdi:flash",
    },
    "SI": {
        "min_value": 1,
        "max_value": 30,
        "step": 1,
        "unit": "%",
        "icon": "mdi:battery-low",
    },
    "SA": {
        "min_value": 70,
        "max_value": 100,
        "step": 1,
        "unit": "%",
        "icon": "mdi:battery-high",
    },
    "SO": {
        "min_value": 1,
        "max_value": 30,
        "step": 1,
        "unit": "%",
        "icon": "mdi:battery-arrow-down-outline",
    },
    "PT": {
        "min_value": 30,
        "max_value": 1440,
        "step": 1,
        "unit": "min",
        "icon": "mdi:timer-outline",
    },
    "MG": {
        "min_value": 1,
        "max_value": 2400,
        "step": 1,
        "unit": "W",
        "icon": "mdi:flash",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up number entities for SunEnergyXT.

    Args:
        hass: Home Assistant instance
        entry: Config entry containing device information
        async_add_entities: Callback to add new entities

    """
    config = hass.data[DOMAIN][entry.entry_id]
    sn = config["sn"]
    ip = config["ip"]
    model = config["model"]
    coordinator = config["coordinator"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=sn,
        manufacturer="SunEnergyXT",
        model=model,
        serial_number=sn,
    )

    entities: list[NumberEntity] = []

    keys = [
        "GS",
        "IS",
        "SI",
        "SA",
        "SO",
        "PT",
        "MG",
    ]

    for key in keys:
        entities.append(
            SunlitNumber(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                key=key,
                sn=sn,
                ip=ip,
                device_info=device_info,
                hass=hass,
            )
        )

    async_add_entities(entities, True)  # noqa: FBT003


class SunlitNumber(CoordinatorEntity[SunlitDataUpdateCoordinator], NumberEntity):
    """
    Number entity for SunEnergyXT device parameters.

    Represents a number entity that controls various device parameters
    such as power limits and percentages.
    """

    _attr_has_entity_name = True
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: SunlitDataUpdateCoordinator,
        entry_id: str,
        key: str,
        sn: str,
        ip: str,
        device_info: DeviceInfo,
        hass: HomeAssistant,
    ) -> None:
        """
        Initialize the number entity.

        Args:
            coordinator: Data update coordinator
            entry_id: Config entry ID
            key: Parameter key
            sn: Device serial number
            ip: Device IP address
            device_info: Device information
            hass: Home Assistant instance

        """
        super().__init__(coordinator)
        self._key = key
        self._sn = sn
        self._ip = ip
        self._session = async_get_clientsession(hass)

        meta = NUMBER_META.get(key, {})

        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"
        self._attr_translation_key = key.lower()
        self._attr_device_info = device_info

        min_value = meta.get("min_value")
        if min_value:
            self._attr_native_min_value = min_value

        max_value = meta.get("max_value")
        if max_value:
            self._attr_native_max_value = max_value

        if device_info["model"] == "SunEnergyXT 500":
            if self._key == "GS":
                self._attr_native_max_value = 800
            if self._key == "MG":
                self._attr_native_max_value = 800

        step = meta.get("step")
        if step:
            self._attr_native_step = step

        unit = meta.get("unit")
        if unit:
            self._attr_native_unit_of_measurement = unit

        icon = meta.get("icon")
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> float:
        """
        Get the current value of the number entity.

        Returns:
            Current value as float, or None if value is invalid

        """
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            _LOGGER.warning("None value from device")
            return None

        try:
            return float(raw)
        except (TypeError, ValueError):
            _LOGGER.warning("Invalid value from device: %s", raw)
            return None

    async def async_set_native_value(self, value: float) -> None:
        """
        Set the value of the number entity.

        Args:
            value: New value to set

        Raises:
            RuntimeError: If there's an error setting the value

        """
        value_int = int(
            max(self._attr_native_min_value, min(self._attr_native_max_value, value))
        )
        payload = {"state": {self._key: value_int}}

        try:
            async with (
                async_timeout.timeout(5),
                self._session.post(
                    f"http://{self._ip}/write",
                    json=payload,
                ) as resp,
            ):
                if resp.status != HTTPStatus.OK:
                    text = await resp.text()
                    msg = f"HTTP {resp.status}: {text}"
                    raise RuntimeError(msg)
        except Exception as err:
            _LOGGER.exception(err)
            raise

        if isinstance(self.coordinator.data, dict):
            self.coordinator.data[self._key] = value_int

        self.async_write_ha_state()
