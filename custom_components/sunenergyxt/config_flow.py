"""
Configuration flow for SunEnergyXT 500 Series integration.

This module handles the configuration process for the SunEnergyXT integration,
including user input validation, device discovery via Zeroconf, and device
information retrieval.

Classes:
- SunlitConfigFlow: Main configuration flow handler for the integration
- InvalidIP: Exception raised for invalid IP addresses
- CannotConnect: Exception raised when unable to connect to the device
- CannotGetSN: Exception raised when unable to retrieve device serial number
- CannotGetModel: Exception raised when unable to retrieve device model

Functions:
- _validate_input: Validates the provided IP address
- _get_device_info: Retrieves device information from the given host
"""

import ipaddress
import logging
from http import HTTPStatus
from typing import Any

import aiohttp
import async_timeout
import voluptuous as vol
from homeassistant import config_entries, exceptions
from homeassistant.core import callback
from homeassistant.data_entry_flow import AbortFlow, FlowResult
from homeassistant.helpers import selector
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from .const import (
    CONF_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    HOST_PREFIX,
    HOST_SUFFIX,
    MAX_POLLING_INTERVAL,
    MIN_POLLING_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def _validate_input(ip: str) -> None:
    """
    Validate the provided IP address.

    Args:
        ip: IP address to validate

    Raises:
        InvalidIP: If the IP address is invalid

    """
    try:
        ipaddress.ip_address(ip)
    except ValueError as err:
        raise InvalidIP from err


async def _get_device_info(host: str) -> dict[str, Any]:
    """
    Retrieve device information from the given host.

    Args:
        host: Hostname or IP address of the device

    Returns:
        Dictionary containing device serial number and model

    Raises:
        CannotConnect: If unable to connect to the device
        CannotGetSN: If unable to retrieve device serial number
        CannotGetModel: If unable to retrieve device model

    """
    try:
        async with async_timeout.timeout(5), aiohttp.ClientSession() as session:
            async with session.get(f"http://{host}/read") as resp:
                if resp.status != HTTPStatus.OK:
                    raise CannotConnect
                data = await resp.json()
                sn = data.get("state", {}).get("reported", {}).get("SN")
                model = data.get("state", {}).get("reported", {}).get("DevType")
                if not isinstance(sn, str):
                    raise CannotGetSN
                if not isinstance(model, str):
                    raise CannotGetModel
                return {"sn": sn, "model": model}
    except Exception:  # noqa: BLE001
        raise CannotConnect from None


class SunlitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """
    Configuration flow handler for SunEnergyXT integration.

    This class handles the configuration process for the SunEnergyXT integration,
    including:
    - User input validation for IP addresses
    - Device discovery via Zeroconf
    - Device information retrieval
    - Configuration entry creation
    - Error handling for various failure scenarios
    """

    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """
        Initialize the configuration flow.

        Sets up instance variables for discovered device information.
        """
        self._discovered_sn: str | None = None
        self._discovered_ip: str | None = None
        self._discovered_model: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Handle user input for SunEnergyXT configuration.

        Args:
            user_input: Dictionary containing user input

        Returns:
            FlowResult indicating the next step in the configuration flow

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                ip = user_input["IP"]
                _LOGGER.debug("user input ip: %s", ip)
                await _validate_input(ip)
                info = await _get_device_info(ip)
                sn = info["sn"]
                model = info["model"]
                _LOGGER.debug("get sn: %s, model: %s", sn, model)

                await self.async_set_unique_id(sn)
                self._abort_if_unique_id_configured(updates={"ip": ip})

            except InvalidIP:
                errors["base"] = "invalid_ip"

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except CannotGetSN:
                errors["base"] = "cannot_get_sn"

            except CannotGetModel:
                errors["base"] = "cannot_get_model"

            except AbortFlow as af:
                reason = getattr(af, "reason", str(af))
                if reason == "already_configured":
                    errors["base"] = "already_configured"
                elif reason == "already_in_progress":
                    errors["base"] = "already_in_progress"
                else:
                    raise

            except Exception as err:
                _LOGGER.exception("Unexpected error during user step: %s", err)
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title=model,
                    data={
                        "ip": ip,
                        "sn": sn,
                        "model": model,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("IP"): str}),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> FlowResult:
        """
        Handle zeroconf discovery for SunEnergyXT devices.

        Args:
            discovery_info: Zeroconf service information

        Returns:
            FlowResult indicating the next step in the configuration flow

        """
        hostname = (discovery_info.hostname or "").rstrip(".")
        if not (hostname.startswith(HOST_PREFIX) and hostname.endswith(HOST_SUFFIX)):
            return self.async_abort(reason="not_device")

        sn = hostname[len(HOST_PREFIX) : -len(HOST_SUFFIX)]
        ip = str(discovery_info.host)
        model = discovery_info.properties["model"]

        await self.async_set_unique_id(sn)
        self._abort_if_unique_id_configured(updates={"ip": ip})

        _LOGGER.debug("Zeroconf discovery: %s", discovery_info)

        self.context["title_placeholders"] = {"sn": sn}

        self._discovered_sn = sn
        self._discovered_ip = ip
        self._discovered_model = model

        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """
        Confirm zeroconf discovery for SunEnergyXT devices.

        Args:
            user_input: Dictionary containing user input

        Returns:
            FlowResult indicating the next step in the configuration flow

        """
        errors: dict[str, str] = {}

        if user_input is not None:
            sn = self._discovered_sn
            ip = self._discovered_ip
            model = self._discovered_model

            try:
                _LOGGER.debug("zeroconf discover ip: %s", ip)
                await _validate_input(ip)
                info = await _get_device_info(ip)
                sn = info["sn"]
                model = info["model"]
                _LOGGER.debug("get sn: %s, model: %s", sn, model)

                await self.async_set_unique_id(sn)
                self._abort_if_unique_id_configured(updates={"ip": ip})

            except CannotConnect:
                return self.async_abort(reason="cannot_connect")

            except CannotGetSN:
                return self.async_abort(reason="cannot_get_sn")

            except CannotGetModel:
                return self.async_abort(reason="cannot_get_model")

            except AbortFlow as af:
                reason = getattr(af, "reason", str(af))
                if reason == "already_configured":
                    return self.async_abort(reason="already_configured")
                raise

            except Exception as err:
                _LOGGER.exception("Unexpected error during zeroconf step: %s", err)
                return self.async_abort(reason="unknown")

            return self.async_create_entry(
                title=model,
                data={"ip": ip, "sn": sn, "model": model},
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema({}),
            description_placeholders={
                "sn": self._discovered_sn,
                "host": self._discovered_ip,
            },
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Return the options flow for an existing device."""
        return SunlitOptionsFlowHandler(config_entry)


class SunlitOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle SunEnergyXT integration options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.options = dict(config_entry.options)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage the polling interval option."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.options.get(
            CONF_POLLING_INTERVAL,
            DEFAULT_POLLING_INTERVAL,
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_POLLING_INTERVAL,
                        default=current_interval,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=MIN_POLLING_INTERVAL,
                            max=MAX_POLLING_INTERVAL,
                            step=1,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    )
                }
            ),
        )


class InvalidIP(exceptions.HomeAssistantError):
    """Input invalid IP."""


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class CannotGetSN(exceptions.HomeAssistantError):
    """Error to indicate we cannot get SN."""


class CannotGetModel(exceptions.HomeAssistantError):
    """Error to indicate we cannot get Model."""
