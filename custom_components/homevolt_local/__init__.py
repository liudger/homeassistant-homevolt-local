"""The Homevolt Local integration."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union, cast

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
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    ATTR_ECU_ID,
    ATTR_EMS,
    ATTR_EUID,
    ATTR_SENSORS,
    CONF_HOST,
    CONF_HOSTS,
    CONF_MAIN_HOST,
    CONF_RESOURCE,
    CONF_RESOURCES,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    EMS_RESOURCE_PATH,
    CONSOLE_RESOURCE_PATH,
)
from .models import HomevoltData, ScheduleEntry

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Homevolt Local from a config entry."""
    # Handle both old and new config entry formats
    if CONF_RESOURCES in entry.data:
        # New format with multiple resources
        resources = entry.data[CONF_RESOURCES]
        hosts = entry.data[CONF_HOSTS]
        main_host = entry.data[CONF_MAIN_HOST]

        # Find the main host URL with protocol from resources
        main_host_url = None
        for resource in resources:
            # Extract host from resource URL
            if "://" in resource:
                host_from_url = resource.split("://")[1].split("/")[0]
                if host_from_url == main_host:
                    # Remove the path to get base URL
                    main_host_url = resource.replace("/ems.json", "")
                    break

        if main_host_url is None:
            # Fallback: construct from first resource
            if resources:
                main_host_url = resources[0].replace("/ems.json", "")
    else:
        # Old format with a single resource
        resources = [entry.data[CONF_RESOURCE]]

        # Extract host from resource URL if CONF_HOST is not available
        if CONF_HOST in entry.data:
            hosts = [entry.data[CONF_HOST]]
            main_host_url = entry.data[CONF_RESOURCE].replace("/ems.json", "")
        else:
            # Extract host from resource URL
            resource_url = entry.data[CONF_RESOURCE]
            main_host_url = resource_url.replace("/ems.json", "")
            try:
                # Remove protocol and path
                if "://" in resource_url:
                    host = resource_url.split("://")[1].split("/")[0]
                else:
                    host = resource_url.split("/")[0]
                hosts = [host]
            except (IndexError, ValueError):
                hosts = ["unknown"]

        main_host = hosts[0]

    username = (entry.data.get(CONF_USERNAME) or "").strip() or None
    password = (entry.data.get(CONF_PASSWORD) or "").strip() or None
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    timeout = entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

    session = async_get_clientsession(hass, verify_ssl=verify_ssl)

    coordinator = HomevoltDataUpdateCoordinator(
        hass,
        _LOGGER,
        entry_id=entry.entry_id,
        resources=resources,
        hosts=hosts,
        main_host=main_host,
        main_host_url=main_host_url,
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

    async def async_add_schedule(call: ServiceCall) -> None:
        """Handle the service call to add a schedule."""
        device_registry = async_get_device_registry(hass)
        device_id = call.data.get("device_id")

        if not device_id:
            _LOGGER.error("No device_id provided")
            return

        device_entry = device_registry.async_get(device_id)
        if not device_entry:
            _LOGGER.error("Device not found: %s", device_id)
            return

        # Find the config entry associated with this device
        config_entry_id = next(iter(device_entry.config_entries), None)
        if not config_entry_id:
            _LOGGER.error(
                "Device %s is not associated with a config entry", device_id)
            return

        config_entry = hass.config_entries.async_get_entry(config_entry_id)
        if not config_entry:
            _LOGGER.error("Config entry not found for device %s", device_id)
            return

        # Extract connection details from the config entry
        host = config_entry.data.get(CONF_MAIN_HOST)
        username = (config_entry.data.get(CONF_USERNAME) or "").strip() or None
        password = (config_entry.data.get(CONF_PASSWORD) or "").strip() or None
        verify_ssl = config_entry.data.get(CONF_VERIFY_SSL, True)

        if not host:
            _LOGGER.error("No host found for device %s", device_id)
            return

        mode = call.data["mode"]
        setpoint = call.data["setpoint"]
        from_time = call.data["from_time"].strftime("%Y-%m-%dT%H:%M:%S")
        to_time = call.data["to_time"].strftime("%Y-%m-%dT%H:%M:%S")

        command = (
            f"sched_add {mode} --setpoint {setpoint} --from={from_time} --to={to_time}"
        )

        # Construct the URL with proper protocol
        if CONF_RESOURCES in config_entry.data:
            main_resource = config_entry.data[CONF_RESOURCES][0]
            url = main_resource.replace("/ems.json", EMS_RESOURCE_PATH)
        elif CONF_RESOURCE in config_entry.data:
            url = config_entry.data[CONF_RESOURCE].replace(
                "/ems.json", EMS_RESOURCE_PATH
            )
        else:
            # Fallback to http
            url = f"http://{host}{EMS_RESOURCE_PATH}"

        try:
            session = async_get_clientsession(hass, verify_ssl=verify_ssl)
            form_data = aiohttp.FormData()
            form_data.add_field("cmd", command)

            auth = (
                aiohttp.BasicAuth(
                    username, password) if username and password else None
            )

            async with session.post(url, data=form_data, auth=auth) as response:
                response_text = await response.text()
                if response.status == 200:
                    _LOGGER.info(
                        "Successfully sent command to %s: %s", host, command)
                else:
                    _LOGGER.error(
                        "Failed to send command to %s. Status: %s, Response: %s",
                        host,
                        response.status,
                        response_text,
                    )
        except aiohttp.ClientError as e:
            _LOGGER.error("Error sending command to %s: %s", host, e)

    hass.services.async_register(DOMAIN, "add_schedule", async_add_schedule)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class HomevoltDataUpdateCoordinator(
    DataUpdateCoordinator[Union[HomevoltData, Dict[str, Any]]]
):
    """Class to manage fetching Homevolt data."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        entry_id: str,
        resources: List[str],
        hosts: List[str],
        main_host: str,
        main_host_url: Optional[str],
        username: Optional[str],
        password: Optional[str],
        session: aiohttp.ClientSession,
        update_interval: timedelta,
        timeout: int,
    ) -> None:
        """Initialize."""
        self.entry_id = entry_id
        self.resources = resources
        self.hosts = hosts
        self.main_host = main_host
        self.main_host_url = main_host_url
        self.username = username
        self.password = password
        self.session = session
        self.timeout = timeout

        # For backward compatibility
        self.resource = resources[0] if resources else ""

        super().__init__(hass, logger, name=DOMAIN, update_interval=update_interval)

    async def _fetch_resource_data(self, resource: str) -> Dict[str, Any]:
        """Fetch data from a single resource."""
        try:
            async with async_timeout.timeout(self.timeout):
                # Only use authentication if both username and password are provided
                auth = None
                if self.username and self.password:
                    auth = aiohttp.BasicAuth(self.username, self.password)

                async with self.session.get(resource, auth=auth) as resp:
                    if resp.status != 200:
                        raise UpdateFailed(
                            f"Error communicating with API: {resp.status}"
                        )
                    return await resp.json()
        except asyncio.TimeoutError as error:
            raise UpdateFailed(
                f"Timeout error fetching data from {resource}: {error}"
            ) from error
        except (aiohttp.ClientError, ValueError) as error:
            raise UpdateFailed(
                f"Error fetching data from {resource}: {error}"
            ) from error

    async def _fetch_schedule_data(self) -> Dict[str, Any]:
        """Fetch schedule data from the main host."""
        url = f"{self.main_host_url}{CONSOLE_RESOURCE_PATH}"
        command = "sched_list"
        schedule_info = {}

        try:
            form_data = aiohttp.FormData()
            form_data.add_field("cmd", command)
            auth = (
                aiohttp.BasicAuth(self.username, self.password)
                if self.username and self.password
                else None
            )

            async with self.session.post(url, data=form_data, auth=auth) as response:
                if response.status != 200:
                    self.logger.error(
                        "Failed to fetch schedule data. Status: %s", response.status
                    )
                    return {}

                response_text = await response.text()
                schedule_info = self._parse_schedule_data(response_text)

        except aiohttp.ClientError as e:
            self.logger.error("Error fetching schedule data: %s", e)

        return schedule_info

    def _parse_schedule_data(self, response_text: str) -> Dict[str, Any]:
        """Parse the schedule data from the text response."""
        schedules = []
        count = 0
        current_id = None
        lines = response_text.splitlines()

        summary_pattern = re.compile(
            r"Schedule get: (\d+) schedules. Current ID: '([^']*)'"
        )

        for line in lines:
            line = line.strip()

            summary_match = summary_pattern.match(line)
            if summary_match:
                count = int(summary_match.group(1))
                current_id = summary_match.group(2)
                continue

            if not line.startswith("id:"):
                continue

            parts = [p.strip() for p in line.split(",")]
            data = {}
            for part in parts:
                key_value = [kv.strip() for kv in part.split(":", 1)]
                if len(key_value) == 2:
                    data[key_value[0]] = key_value[1]

            if "id" not in data:
                continue

            # Safely parse setpoint - handle non-numeric values
            setpoint_value = data.get("setpoint")
            setpoint = None
            if setpoint_value is not None:
                try:
                    # Handle special values like '<max allowed>'
                    if setpoint_value.startswith("<") or setpoint_value.startswith(">"):
                        setpoint = setpoint_value  # Keep as string
                    else:
                        setpoint = int(setpoint_value)
                except ValueError:
                    # If conversion fails, keep as string
                    setpoint = setpoint_value

            # Safely parse id - handle non-numeric values
            id_value = data.get("id")
            if id_value is None:
                continue  # Skip entries without id
            try:
                schedule_id = int(id_value)
            except ValueError:
                continue  # Skip entries with invalid id

            schedule = ScheduleEntry(
                id=schedule_id,
                type=data.get("type"),
                from_time=data.get("from"),
                to_time=data.get("to"),
                setpoint=setpoint,
                offline=data.get("offline") == "true"
                if data.get("offline") is not None
                else None,
                max_discharge=data.get("max_discharge"),
                max_charge=data.get("max_charge"),
            )
            schedules.append(schedule)

        return {
            "entries": schedules,
            "count": count,
            "current_id": current_id,
        }

    async def _async_update_data(self) -> HomevoltData:
        """Fetch data from all Homevolt API resources."""
        if not self.resources:
            raise UpdateFailed("No resources configured")

        # Fetch sensor and schedule data in parallel
        tasks = [self._fetch_resource_data(resource)
                 for resource in self.resources]
        tasks.append(self._fetch_schedule_data())
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Separate schedule data from sensor data results
        schedule_result = results.pop()
        if isinstance(schedule_result, Exception):
            self.logger.error(
                "Error fetching schedule data: %s", schedule_result)
            schedule_info = {"entries": [], "count": 0, "current_id": None}
        else:
            # Cast to Dict since we know _fetch_schedule_data returns Dict[str, Any]
            schedule_info = cast(Dict[str, Any], schedule_result)

        # Process the sensor data results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(
                    "Error fetching data from %s: %s", self.resources[i], result
                )
            else:
                valid_results.append((self.hosts[i], result))

        if not valid_results:
            raise UpdateFailed("Failed to fetch data from any resource")

        # Find the main system's data
        main_data = None
        for host, data in valid_results:
            if host == self.main_host:
                main_data = data
                break

        # If main system's data is not available, use the first valid result
        if main_data is None:
            self.logger.warning(
                "Main system data not available, using first valid result"
            )
            main_data = valid_results[0][1]

        # Merge data from all systems
        merged_dict_data = self._merge_data(valid_results, main_data)

        # Add schedule data to the merged data
        merged_dict_data["schedules"] = schedule_info.get("entries", [])
        merged_dict_data["schedule_count"] = schedule_info.get("count")
        merged_dict_data["schedule_current_id"] = schedule_info.get(
            "current_id")

        # Convert the merged dictionary data to a HomevoltData object
        return HomevoltData.from_dict(merged_dict_data)

    def _merge_data(
        self, results: List[tuple[str, Dict[str, Any]]], main_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge data from multiple systems."""
        # Start with the main system's data
        merged_data = dict(main_data)

        # Collect all EMS devices and sensors from all systems
        all_ems = merged_data.get(ATTR_EMS, [])[:]
        all_sensors = merged_data.get(ATTR_SENSORS, [])[:]

        for _, data in results:
            # Add EMS devices
            if ATTR_EMS in data:
                for ems in data[ATTR_EMS]:
                    # Check if this EMS device is already in the list (based on ecu_id)
                    if ATTR_ECU_ID in ems:
                        ecu_id = ems[ATTR_ECU_ID]
                        if not any(e.get(ATTR_ECU_ID) == ecu_id for e in all_ems):
                            all_ems.append(ems)
                    else:
                        # If no ecu_id, just add it
                        all_ems.append(ems)

            # Add sensors
            if ATTR_SENSORS in data:
                for sensor in data[ATTR_SENSORS]:
                    # Check if this sensor is already in the list (based on euid)
                    if ATTR_EUID in sensor:
                        euid = sensor[ATTR_EUID]
                        if not any(s.get(ATTR_EUID) == euid for s in all_sensors):
                            all_sensors.append(sensor)
                    else:
                        # If no euid, just add it
                        all_sensors.append(sensor)

        # Update the merged data with all EMS devices and sensors
        merged_data[ATTR_EMS] = all_ems
        merged_data[ATTR_SENSORS] = all_sensors

        return merged_data
