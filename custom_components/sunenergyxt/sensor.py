"""
Sensor entities for SunEnergyXT 500 Series integration.

This module implements sensor entities for the SunEnergyXT integration,
providing monitoring of various device parameters such as power, energy, and status.

Classes:
- SunlitSensor: Represents a sensor entity for monitoring SunEnergyXT device parameters
- SunlitBatteryEnergySensor: Calculates battery charge or discharge energy from
  the battery power

Constants:
- SENSOR_META: Metadata configuration for sensor entities, including units,
  state classes, and scaling factors
- BATTERY_ENERGY_META: Metadata configuration for the calculated battery energy sensors
"""

import logging
import math
import time
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorExtraStoredData,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunlitDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_META: dict[str, dict[str, Any]] = {
    "WS": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:wifi",
    },
    "WR": {
        "unit": "dB",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "icon": "mdi:wifi-strength-2",
    },
    "ST": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:state-machine",
    },
    "IW": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:flash",
    },
    "OP": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:flash-outline",
    },
    "PV": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-power",
    },
    "PV1": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
    },
    "PV2": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
    },
    "PV3": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
    },
    "PV4": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:solar-panel",
    },
    "II1": {
        "unit": "A",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "II2": {
        "unit": "A",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "II3": {
        "unit": "A",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "II4": {
        "unit": "A",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.CURRENT,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:current-dc",
    },
    "VP1": {
        "unit": "V",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:sine-wave",
    },
    "VP2": {
        "unit": "V",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:sine-wave",
    },
    "VP3": {
        "unit": "V",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:sine-wave",
    },
    "VP4": {
        "unit": "V",
        "scale": 0.1,
        "precision": 1,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.VOLTAGE,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:sine-wave",
    },
    "GP": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:transmission-tower",
    },
    "LP": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:home-lightning-bolt",
    },
    "BP": {
        "unit": "W",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.POWER,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-charging",
    },
    "PD": {
        "unit": "kWh",
        "scale": 0.001,
        "precision": 3,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:solar-power",
    },
    "GD1": {
        "unit": "kWh",
        "scale": 0.001,
        "precision": 3,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:battery-charging",
    },
    "GD2": {
        "unit": "kWh",
        "scale": 0.001,
        "precision": 3,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:transmission-tower-export",
    },
    "LD": {
        "unit": "kWh",
        "scale": 0.001,
        "precision": 3,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.ENERGY,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "icon": "mdi:power-plug-battery-outline",
    },
    "SC": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery",
    },
    "SC0": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "SC1": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "SC2": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "SC3": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "SC4": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "SC5": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-outline",
    },
    "ON": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": SensorStateClass.MEASUREMENT,
        "icon": "mdi:battery-check",
    },
    "ES": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "BS0": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "BS1": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "BS2": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "BS3": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "BS4": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "BS5": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "AS": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "DS": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:chip",
    },
    "SN": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:information-variant-circle",
    },
    "MS": {
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:meter-electric",
    },
}

# The device does not report battery energy counters. These sensors integrate
# BP over time instead. BP is positive while charging and negative while discharging.
BATTERY_ENERGY_META: dict[str, dict[str, Any]] = {
    "battery_charge_energy": {
        "direction": 1,
        "icon": "mdi:battery-arrow-up",
    },
    "battery_discharge_energy": {
        "direction": -1,
        "icon": "mdi:battery-arrow-down",
    },
}

# Do not integrate across a longer time between two valid BP samples.
BATTERY_ENERGY_MAX_GAP = 300  # seconds


def _positive_energy_kwh(start: float, end: float, seconds: float) -> float:
    """
    Get the energy of the positive part of a linear power change.

    Args:
        start: Power at the start of the interval in W
        end: Power at the end of the interval in W
        seconds: Length of the interval in seconds

    Returns:
        Energy in kWh. The negative part of the interval gives no energy.

    """
    if start >= 0 and end >= 0:
        watt_seconds = (start + end) / 2 * seconds
    elif start <= 0 and end <= 0:
        return 0.0
    else:
        # The power crosses zero, so only the positive triangle counts.
        peak = max(start, end)
        watt_seconds = peak * peak / (2 * abs(end - start)) * seconds

    return watt_seconds / 3_600_000


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """
    Set up sensor entities for SunEnergyXT.

    Args:
        hass: Home Assistant instance
        entry: Config entry containing device information
        async_add_entities: Callback to add new entities

    """
    config = hass.data[DOMAIN][entry.entry_id]
    sn = config["sn"]
    model = config["model"]
    coordinator = config["coordinator"]

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=sn,
        manufacturer="SunEnergyXT",
        model=model,
        serial_number=sn,
    )

    entities: list[SensorEntity] = []

    keys = [
        "WS",
        "WR",
        "ST",
        "IW",
        "OP",
        "PV",
        "PV1",
        "PV2",
        "PV3",
        "PV4",
        "II1",
        "II2",
        "II3",
        "II4",
        "VP1",
        "VP2",
        "VP3",
        "VP4",
        "GP",
        "LP",
        "BP",
        "PD",
        "GD1",
        "GD2",
        "LD",
        "SC",
        "SC0",
        "SC1",
        "SC2",
        "SC3",
        "SC4",
        "SC5",
        "ON",
        "ES",
        "BS0",
        "BS1",
        "BS2",
        "BS3",
        "BS4",
        "BS5",
        "AS",
        "DS",
        "SN",
        "MS",
    ]

    for key in keys:
        entities.append(
            SunlitSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                key=key,
                device_info=device_info,
            )
        )

    for key in BATTERY_ENERGY_META:
        entities.append(
            SunlitBatteryEnergySensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                key=key,
                device_info=device_info,
            )
        )

    async_add_entities(entities, True)  # noqa: FBT003


class SunlitSensor(
    CoordinatorEntity[SunlitDataUpdateCoordinator],
    SensorEntity,
):
    """
    Sensor entity for SunEnergyXT device parameters.

    Represents a sensor entity that monitors various device parameters
    such as power, energy, and status.
    """

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: SunlitDataUpdateCoordinator,
        entry_id: str,
        key: str,
        device_info: DeviceInfo,
    ) -> None:
        """
        Initialize the sensor entity.

        Args:
            coordinator: Data update coordinator
            entry_id: Config entry ID
            key: Parameter key
            device_info: Device information

        """
        super().__init__(coordinator)

        self._key = key
        meta = SENSOR_META.get(key, {})
        self._scale: float | None = meta.get("scale")
        self._precision: int | None = meta.get("precision")

        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"
        self._attr_translation_key = key.lower()
        self._attr_device_info = device_info

        state_class = meta.get("state_class")
        if state_class:
            self._attr_state_class = state_class

        precision = meta.get("precision")
        if precision:
            self._attr_suggested_display_precision = precision

        unit = meta.get("unit")
        if unit:
            self._attr_native_unit_of_measurement = unit

        device_class = meta.get("device_class")
        if device_class:
            self._attr_device_class = device_class

        icon = meta.get("icon")
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self) -> Any:
        """
        Get the current value of the sensor entity.

        Returns:
            Current value, optionally scaled and rounded

        """
        raw = self.coordinator.data.get(self._key)
        if raw is None:
            return None

        if self._scale is None:
            return raw

        try:
            val = float(raw) * self._scale
            return round(val, self._precision) if self._precision is not None else val
        except (TypeError, ValueError):
            return raw


class SunlitBatteryEnergySensor(
    CoordinatorEntity[SunlitDataUpdateCoordinator],
    RestoreSensor,
):
    """
    Battery energy sensor calculated from the battery power.

    The device does not report battery energy counters. This sensor integrates
    the battery power (BP) over time and counts only one direction, charge or
    discharge. The total is restored after a restart of Home Assistant, so it
    can be used in the "Home battery storage" section of the Energy Dashboard.
    """

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = "kWh"
    _attr_suggested_display_precision = 3

    def __init__(
        self,
        coordinator: SunlitDataUpdateCoordinator,
        entry_id: str,
        key: str,
        device_info: DeviceInfo,
    ) -> None:
        """
        Initialize the battery energy sensor entity.

        Args:
            coordinator: Data update coordinator
            entry_id: Config entry ID
            key: Sensor key in BATTERY_ENERGY_META
            device_info: Device information

        """
        super().__init__(coordinator)

        meta = BATTERY_ENERGY_META[key]
        self._direction: int = meta["direction"]
        self._total_kwh = 0.0
        # Monotonic time and BP value of the last valid sample
        self._last_sample: tuple[float, float] | None = None

        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = device_info
        self._attr_icon = meta["icon"]

    async def async_added_to_hass(self) -> None:
        """Restore the last total and take the first sample before updates start."""
        last_data = await self.async_get_last_sensor_data()
        if last_data is not None and last_data.native_value is not None:
            try:
                restored = float(last_data.native_value)
            except (TypeError, ValueError, OverflowError):
                restored = None

            if restored is not None and math.isfinite(restored) and restored >= 0:
                self._total_kwh = restored
            else:
                _LOGGER.warning(
                    "Cannot restore %s from value %s",
                    self.entity_id,
                    last_data.native_value,
                )

        # Use the data from the setup refresh as the first sample
        power = self._read_power() if self.coordinator.last_update_success else None
        if power is not None:
            self._last_sample = (time.monotonic(), power)

        await super().async_added_to_hass()

    @property
    def available(self) -> bool:
        """
        Get the availability of the sensor entity.

        Returns:
            True if the device is reachable and reports BP

        """
        return super().available and self._read_power() is not None

    @property
    def native_value(self) -> float:
        """
        Get the current value of the sensor entity.

        Returns:
            Total energy in kWh, rounded to Wh

        """
        return round(self._total_kwh, 3)

    @property
    def extra_restore_state_data(self) -> SensorExtraStoredData:
        """
        Get the data to restore after a restart.

        Returns:
            Total energy in kWh without rounding

        """
        return SensorExtraStoredData(self._total_kwh, self.native_unit_of_measurement)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Add the energy since the last sample, then write the state."""
        self._integrate(time.monotonic())
        super()._handle_coordinator_update()

    def _integrate(self, now: float) -> None:
        """
        Add the energy between the last sample and this sample to the total.

        Args:
            now: Monotonic time of this sample in seconds

        """
        power = self._read_power() if self.coordinator.last_update_success else None
        if power is None:
            # Do not integrate across the gap when data is missing
            self._last_sample = None
            return

        if self._last_sample is not None:
            last_time, last_power = self._last_sample
            elapsed = now - last_time
            if 0 < elapsed <= BATTERY_ENERGY_MAX_GAP:
                total = self._total_kwh + _positive_energy_kwh(
                    last_power * self._direction,
                    power * self._direction,
                    elapsed,
                )
                # Home Assistant does not accept a non-finite energy state
                if math.isfinite(total):
                    self._total_kwh = total

        self._last_sample = (now, power)

    def _read_power(self) -> float | None:
        """
        Get the battery power from the coordinator data.

        Returns:
            Battery power in W, or None if BP is missing or not a valid number

        """
        if not self.coordinator.data:
            return None

        raw = self.coordinator.data.get("BP")
        if raw is None:
            return None

        try:
            power = float(raw)
        except (TypeError, ValueError):
            return None

        return power if math.isfinite(power) else None
