"""Test the sensor platform."""
import pytest
from unittest.mock import Mock, AsyncMock
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPower,
    UnitOfEnergy,
)

from custom_components.homevolt_local.const import DOMAIN
from custom_components.homevolt_local.sensor import (
    HomevoltSensor,
    HomevoltSensorEntityDescription,
    SENSOR_DESCRIPTIONS,
)


class TestHomevoltSensors:
    """Test Homevolt sensor entities."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_coordinator = Mock()
        self.mock_coordinator.data = Mock()
        self.mock_coordinator.data.aggregated = Mock()
        self.mock_coordinator.data.aggregated.op_state_str = "Active"
        self.mock_coordinator.data.aggregated.error_str = ""
        self.mock_coordinator.data.aggregated.ems_data = Mock()
        self.mock_coordinator.data.aggregated.ems_data.state_str = "Active"
        self.mock_coordinator.data.aggregated.ems_data.soc_avg = 75
        self.mock_coordinator.data.aggregated.ems_data.power = 1500
        self.mock_coordinator.data.aggregated.ems_data.energy_produced = 25500
        self.mock_coordinator.data.aggregated.ems_data.energy_consumed = 18200
        self.mock_coordinator.resource = "http://192.168.1.100/ems.json"

    def test_sensor_creation(self):
        """Test HomevoltSensor creation."""
        # Get the first sensor description (status sensor)
        description = SENSOR_DESCRIPTIONS[0]
        sensor = HomevoltSensor(self.mock_coordinator, description)
        
        assert sensor.entity_description == description
        assert sensor.unique_id is not None
        assert DOMAIN in sensor.unique_id

    def test_sensor_descriptions_exist(self):
        """Test that sensor descriptions are defined."""
        assert len(SENSOR_DESCRIPTIONS) > 0
        
        # Check that the first description is the status sensor
        status_desc = SENSOR_DESCRIPTIONS[0]
        assert status_desc.key == "ems"
        assert status_desc.name == "Homevolt Status"
        assert status_desc.value_fn is not None

    def test_status_sensor_value(self):
        """Test status sensor value function."""
        description = SENSOR_DESCRIPTIONS[0]  # Status sensor
        sensor = HomevoltSensor(self.mock_coordinator, description)
        
        # Test the value function directly
        value = description.value_fn(self.mock_coordinator.data)
        assert value == "Active"

    def test_error_sensor_value(self):
        """Test error sensor value function."""
        error_desc = None
        for desc in SENSOR_DESCRIPTIONS:
            if desc.key == "ems_error":
                error_desc = desc
                break
        
        assert error_desc is not None
        assert error_desc.name == "Homevolt Error"
        
        # Test with no error
        value = error_desc.value_fn(self.mock_coordinator.data)
        assert value is None
        
        # Test with error
        self.mock_coordinator.data.aggregated.error_str = "Test error"
        value = error_desc.value_fn(self.mock_coordinator.data)
        assert value == "Test error"

    def test_soc_sensor_value(self):
        """Test SoC sensor value function."""
        soc_desc = None
        for desc in SENSOR_DESCRIPTIONS:
            if "soc" in desc.key.lower():
                soc_desc = desc
                break
        
        # SoC sensor should exist
        assert soc_desc is not None
        
        # Create proper mock data for SoC test
        self.mock_coordinator.data.ems = []  # Empty list to trigger the fallback path
        
        # Test the value function with empty data
        value = soc_desc.value_fn(self.mock_coordinator.data)
        # Should return None for empty data
        assert value is None

    def test_icon_function(self):
        """Test dynamic icon function for status sensor."""
        description = SENSOR_DESCRIPTIONS[0]  # Status sensor
        
        # Test low battery icon
        self.mock_coordinator.data.aggregated.ems_data.soc_avg = 3
        icon = description.icon_fn(self.mock_coordinator.data)
        assert "battery-outline" in icon
        
        # Test medium battery icon  
        self.mock_coordinator.data.aggregated.ems_data.soc_avg = 50
        icon = description.icon_fn(self.mock_coordinator.data)
        assert "battery-50" in icon
        
        # Test high battery icon
        self.mock_coordinator.data.aggregated.ems_data.soc_avg = 90
        icon = description.icon_fn(self.mock_coordinator.data)
        assert "battery-90" in icon

    def test_sensor_available(self):
        """Test sensor availability."""
        description = SENSOR_DESCRIPTIONS[0]
        sensor = HomevoltSensor(self.mock_coordinator, description)
        
        # Mock coordinator to be available
        self.mock_coordinator.last_update_success = True
        assert sensor.available is True
        
        # Mock coordinator to be unavailable
        self.mock_coordinator.last_update_success = False
        assert sensor.available is False

    def test_device_info(self):
        """Test sensor device info."""
        description = SENSOR_DESCRIPTIONS[0]
        sensor = HomevoltSensor(self.mock_coordinator, description)
        
        device_info = sensor.device_info
        assert "identifiers" in device_info
        assert device_info["manufacturer"] == "Homevolt"
        assert "Homevolt" in device_info["name"]

    def test_entity_description_dataclass(self):
        """Test HomevoltSensorEntityDescription dataclass."""
        desc = HomevoltSensorEntityDescription(
            key="test",
            name="Test Sensor",
            value_fn=lambda data: "test_value"
        )
        
        assert desc.key == "test"
        assert desc.name == "Test Sensor"
        assert desc.value_fn("dummy") == "test_value"
        assert desc.device_specific is False
        assert desc.sensor_specific is False

    def test_sensor_with_missing_data(self):
        """Test sensor behavior when data is missing."""
        description = SENSOR_DESCRIPTIONS[0]
        
        # Create coordinator with no data
        mock_coordinator = Mock()
        mock_coordinator.data = None
        mock_coordinator.last_update_success = False
        mock_coordinator.resource = "http://192.168.1.100/ems.json"
        
        sensor = HomevoltSensor(mock_coordinator, description)
        
        # Should handle missing data gracefully
        assert sensor.available is False
        assert sensor.unique_id is not None


class TestSensorConstants:
    """Test sensor-related constants."""
    
    def test_units_imported(self):
        """Test that required units are properly imported."""
        assert PERCENTAGE == "%"
        assert UnitOfPower.WATT == "W"
        assert UnitOfEnergy.KILO_WATT_HOUR == "kWh"
    
    def test_domain_constant(self):
        """Test domain constant."""
        assert DOMAIN == "homevolt_local"