"""Test the constants module."""
import pytest
from custom_components.homevolt_local.const import (
    DOMAIN,
    CONF_RESOURCE,
    CONF_HOST,
    CONF_HOSTS,
    CONF_MAIN_HOST,
    CONF_RESOURCES,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_RESOURCE_PATH,
    ATTR_EMS,
    ATTR_AGGREGATED,
    ATTR_SENSORS,
    ATTR_ECU_ID,
    ATTR_EUID,
    SENSOR_TYPE_GRID,
    SENSOR_TYPE_SOLAR,
    SENSOR_TYPE_LOAD,
)


def test_domain_constant():
    """Test that the domain constant is correct."""
    assert DOMAIN == "homevolt_local"


def test_configuration_constants():
    """Test configuration constants."""
    assert CONF_RESOURCE == "resource"
    assert CONF_HOST == "host"
    assert CONF_HOSTS == "hosts"
    assert CONF_MAIN_HOST == "main_host"
    assert CONF_RESOURCES == "resources"


def test_default_values():
    """Test default values."""
    assert DEFAULT_SCAN_INTERVAL == 30
    assert DEFAULT_TIMEOUT == 30
    assert DEFAULT_RESOURCE_PATH == "/ems.json"


def test_attribute_constants():
    """Test API attribute constants."""
    assert ATTR_EMS == "ems"
    assert ATTR_AGGREGATED == "aggregated"
    assert ATTR_SENSORS == "sensors"
    assert ATTR_ECU_ID == "ecu_id"
    assert ATTR_EUID == "euid"


def test_sensor_type_constants():
    """Test sensor type constants."""
    assert SENSOR_TYPE_GRID == "grid"
    assert SENSOR_TYPE_SOLAR == "solar"
    assert SENSOR_TYPE_LOAD == "load"


def test_constants_are_strings():
    """Test that string constants are indeed strings."""
    string_constants = [
        DOMAIN,
        CONF_RESOURCE,
        CONF_HOST,
        DEFAULT_RESOURCE_PATH,
        ATTR_EMS,
        ATTR_AGGREGATED,
        SENSOR_TYPE_GRID,
    ]
    
    for constant in string_constants:
        assert isinstance(constant, str)
        assert len(constant) > 0


def test_constants_are_integers():
    """Test that integer constants are indeed integers."""
    integer_constants = [
        DEFAULT_SCAN_INTERVAL,
        DEFAULT_TIMEOUT,
    ]
    
    for constant in integer_constants:
        assert isinstance(constant, int)
        assert constant > 0