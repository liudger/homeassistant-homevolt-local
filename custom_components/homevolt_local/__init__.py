"""The Homevolt Local integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_RESOURCE, DEFAULT_SCAN_INTERVAL, DEFAULT_TIMEOUT, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Homevolt Local from a config entry."""
    resource = entry.data[CONF_RESOURCE]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    timeout = entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    session = async_get_clientsession(hass, verify_ssl=verify_ssl)

    coordinator = HomevoltDataUpdateCoordinator(
        hass,
        _LOGGER,
        entry_id=entry.entry_id,
        resource=resource,
        username=username,
        password=password,
        session=session,
        update_interval=timedelta(seconds=scan_interval),
        timeout=timeout,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class HomevoltDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Homevolt data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        entry_id: str,
        resource: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
        update_interval: timedelta,
        timeout: int,
    ) -> None:
        """Initialize."""
        self.entry_id = entry_id
        self.resource = resource
        self.username = username
        self.password = password
        self.session = session
        self.timeout = timeout

        super().__init__(hass, logger, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Fetch data from Homevolt API."""
        try:
            async with async_timeout.timeout(self.timeout):
                auth = aiohttp.BasicAuth(self.username, self.password)
                async with self.session.get(self.resource, auth=auth) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(f"Error communicating with API: {resp.status}")
                    return await resp.json()
        except asyncio.TimeoutError as error:
            raise UpdateFailed(f"Timeout error fetching data: {error}") from error
        except (aiohttp.ClientError, ValueError) as error:
            raise UpdateFailed(f"Error fetching data: {error}") from error
