"""Test fixtures and utilities for the Homevolt Local integration tests."""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
import aiohttp


@pytest.fixture
def mock_hass():
    """Return a mock Home Assistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.data = {}
    hass.config_entries = Mock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass


@pytest.fixture
def mock_config_entry():
    """Return a mock config entry."""
    return Mock(spec=ConfigEntry)


@pytest.fixture
def mock_session():
    """Return a mock aiohttp session."""
    session = Mock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def sample_homevolt_data():
    """Return sample HomevoltData in the correct format."""
    return {
        "$type": "homevolt_data",
        "ts": 1640995200,
        "ems": [
            {
                "ecu_id": 1,
                "ecu_host": "192.168.1.100",
                "ecu_version": "1.0.0",
                "error": 0,
                "error_str": "",
                "op_state": 1,
                "op_state_str": "Active",
                "ems_info": {
                    "protocol_version": 1,
                    "fw_version": "1.0.0",
                    "rated_capacity": 10000,
                    "rated_power": 5000
                },
                "bms_info": [
                    {
                        "fw_version": "1.0.0",
                        "serial_number": "BMS001",
                        "rated_cap": 10000,
                        "id": 1
                    }
                ],
                "inv_info": {
                    "fw_version": "1.0.0",
                    "serial_number": "INV001"
                }
            }
        ],
        "aggregated": {
            "ecu_id": 1,
            "ecu_host": "192.168.1.100",
            "ecu_version": "1.0.0",
            "error": 0,
            "error_str": "",
            "op_state": 1,
            "op_state_str": "Active"
        },
        "sensors": [
            {
                "type": "grid",
                "node_id": 1,
                "euid": "SENSOR001",
                "interface": 1,
                "available": True,
                "rssi": -50,
                "average_rssi": -52.5,
                "pdr": 98.5,
                "phase": [
                    {
                        "voltage": 230.0,
                        "amp": -2.17,
                        "power": -500.0,
                        "pf": 1.0
                    }
                ],
                "frequency": 50,
                "total_power": -500,
                "energy_imported": 100.5,
                "energy_exported": 50.2,
                "timestamp": 1640995200
            }
        ]
    }


@pytest.fixture 
def sample_config_data():
    """Return sample config entry data."""
    return {
        "resource": "http://192.168.1.100/ems.json",
        "username": "test_user",
        "password": "test_pass",
        "verify_ssl": True,
        "scan_interval": 30,
        "timeout": 30
    }


@pytest.fixture
def sample_multi_config_data():
    """Return sample config entry data with multiple hosts."""
    return {
        "resources": [
            "http://192.168.1.100/ems.json",
            "http://192.168.1.101/ems.json"
        ],
        "hosts": ["192.168.1.100", "192.168.1.101"],
        "main_host": "192.168.1.100",
        "username": "test_user", 
        "password": "test_pass",
        "verify_ssl": True,
        "scan_interval": 30,
        "timeout": 30
    }