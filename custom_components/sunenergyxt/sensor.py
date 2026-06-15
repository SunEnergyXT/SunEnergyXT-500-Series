"""
Sensor entities for SunEnergyXT 500 Series integration.

This module implements sensor entities for the SunEnergyXT integration,
providing monitoring of various device parameters such as power, energy, and status.

Classes:
- SunlitSensor: Represents a sensor entity for monitoring SunEnergyXT device parameters

Constants:
- SENSOR_META: Metadata configuration for sensor entities, including units,
  state classes, and scaling factors
"""

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.BATTERY,
        "icon": "mdi:battery-outline",
    },
    "SC2": {
        "unit": "%",
        "entity_category": EntityCategory.DIAGNOSTIC,
        "state_class": SensorStateClass.MEASUREMENT,
        "device_class": SensorDeviceClass.BATTERY,
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

        icon = meta.get("icon")
        if icon:
            self._attr_icon = icon

        device_class = meta.get("device_class")
        if device_class:
            self._attr_device_class = device_class

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

    @property
    def extra_state_attributes(self) -> Any:
        """
        Get extra state attributes for the sensor entity.

        Returns:
            Dictionary of extra state attributes

        """
        attrs = {}
        if self.coordinator.last_success_time:
            attrs["last_report_time"] = self.coordinator.last_success_time.isoformat()
        return attrs
