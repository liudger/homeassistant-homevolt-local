"""Config flow for Homevolt Local integration."""
from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urlparse

import aiohttp
import voluptuous as vol

class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""


class InvalidResource(Exception):
    """Error to indicate the resource URL is invalid."""

from homeassistant import config_entries
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_RESOURCE, DEFAULT_RESOURCE_PATH, DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

# Define a new configuration constant for the host
CONF_HOST = "host"

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_VERIFY_SSL, default=True): bool,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): int,
    }
)


def is_valid_host(host: str) -> bool:
    """Check if the host is valid."""
    # Simple validation: host should not be empty and should not contain spaces
    return bool(host) and " " not in host


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]

    # Validate the host
    if not is_valid_host(host):
        raise InvalidResource("Invalid IP or hostname format")

    # Construct the full URL from the host
    # Check if the host already includes a protocol (http:// or https://)
    if not host.startswith(("http://", "https://")):
        # Default to https if no protocol is specified
        resource_url = f"https://{host}{DEFAULT_RESOURCE_PATH}"
    else:
        # If protocol is already included, just append the path
        resource_url = f"{host}{DEFAULT_RESOURCE_PATH}"

    session = async_get_clientsession(hass, verify_ssl=data[CONF_VERIFY_SSL])

    try:
        auth = aiohttp.BasicAuth(data[CONF_USERNAME], data[CONF_PASSWORD])
        async with session.get(resource_url, auth=auth) as response:
            if response.status == 401:
                raise InvalidAuth("Invalid authentication")
            elif response.status != 200:
                raise CannotConnect(f"Invalid response from API: {response.status}")

            try:
                response_data = await response.json()
            except ValueError:
                raise CannotConnect("Invalid response format (not JSON)")

            # Check if the response has the expected structure
            if "aggregated" not in response_data:
                raise CannotConnect("Invalid API response format: 'aggregated' key missing")

    except aiohttp.ClientError as err:
        raise CannotConnect(f"Connection error: {err}")
    except (InvalidAuth, CannotConnect, InvalidResource) as err:
        raise
    except Exception as err:
        raise Exception(f"Error validating API: {err}") from err

    # Return info that you want to store in the config entry.
    return {
        "title": "Homevolt Local", 
        "host": host,
        "resource_url": resource_url
    }


class HomevoltConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Homevolt Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Check if we already have an entry with this host
                host = info["host"]
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except InvalidResource:
                errors["base"] = "invalid_resource"
            except Exception as err:
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"
            else:
                # Create a new data dictionary with the constructed resource URL
                entry_data = {
                    CONF_RESOURCE: info["resource_url"],
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_VERIFY_SSL: user_input.get(CONF_VERIFY_SSL, True),
                    CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    CONF_TIMEOUT: user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                }
                return self.async_create_entry(title=info["title"], data=entry_data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
