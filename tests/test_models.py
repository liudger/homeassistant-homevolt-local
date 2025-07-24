"""Test the data models."""
import pytest
from custom_components.homevolt_local.models import (
    EmsInfo,
    BmsInfo,
    InvInfo,
    EmsConfig,
    InvConfig,
    EmsData,
    PhaseData,
    SensorData,
    EmsDevice,
    HomevoltData,
)


def test_ems_info_creation():
    """Test EmsInfo creation."""
    ems_info = EmsInfo(
        protocol_version=1,
        fw_version="1.0.0",
        rated_capacity=10000,
        rated_power=5000
    )
    
    assert ems_info.protocol_version == 1
    assert ems_info.fw_version == "1.0.0"
    assert ems_info.rated_capacity == 10000
    assert ems_info.rated_power == 5000


def test_bms_info_creation():
    """Test BmsInfo creation."""
    bms_info = BmsInfo(
        fw_version="1.0.0",
        serial_number="BMS001",
        rated_cap=10000,
        id=1
    )
    
    assert bms_info.fw_version == "1.0.0"
    assert bms_info.serial_number == "BMS001"
    assert bms_info.rated_cap == 10000
    assert bms_info.id == 1


def test_inv_info_creation():
    """Test InvInfo creation."""
    inv_info = InvInfo(
        fw_version="1.0.0",
        serial_number="INV001"
    )
    
    assert inv_info.fw_version == "1.0.0"
    assert inv_info.serial_number == "INV001"


def test_ems_config_creation():
    """Test EmsConfig creation."""
    ems_config = EmsConfig(
        grid_code_preset=1,
        grid_code_preset_str="Test",
        control_timeout=False
    )
    
    assert ems_config.grid_code_preset == 1
    assert ems_config.grid_code_preset_str == "Test"
    assert ems_config.control_timeout is False


def test_inv_config_creation():
    """Test InvConfig creation."""
    inv_config = InvConfig(ffr_fstart_freq=50)
    
    assert inv_config.ffr_fstart_freq == 50


def test_ems_data_creation():
    """Test EmsData creation."""
    ems_data = EmsData(
        timestamp_ms=1640995200000,
        state=1,
        state_str="Active",
        info=0,
        info_str=[],
        warning=0,
        warning_str=[],
        alarm=0,
        alarm_str=[],
        phase_angle=0,
        frequency=50,
        phase_seq=1,
        power=1500,
        apparent_power=1550,
        reactive_power=100,
        energy_produced=25500,
        energy_consumed=18200,
        sys_temp=25,
        avail_cap=10000,
        freq_res_state=0,
        soc_avg=75
    )
    
    assert ems_data.timestamp_ms == 1640995200000
    assert ems_data.state == 1
    assert ems_data.state_str == "Active"
    assert ems_data.power == 1500
    assert ems_data.energy_produced == 25500
    assert ems_data.soc_avg == 75


def test_phase_data_creation():
    """Test PhaseData creation."""
    phase_data = PhaseData(
        voltage=230.0,
        amp=5.5,
        power=1265.0,
        pf=0.98
    )
    
    assert phase_data.voltage == 230.0
    assert phase_data.amp == 5.5
    assert phase_data.power == 1265.0
    assert phase_data.pf == 0.98


def test_sensor_data_creation():
    """Test SensorData creation."""
    phase_data = [PhaseData(voltage=230.0, amp=5.5, power=1265.0, pf=0.98)]
    
    sensor_data = SensorData(
        type="grid",
        node_id=1,
        euid="SENSOR001",
        interface=1,
        available=True,
        rssi=-50,
        average_rssi=-52.5,
        pdr=98.5,
        phase=phase_data,
        frequency=50,
        total_power=-500,
        energy_imported=100.5,
        energy_exported=50.2,
        timestamp=1640995200
    )
    
    assert sensor_data.type == "grid"
    assert sensor_data.node_id == 1
    assert sensor_data.euid == "SENSOR001"
    assert sensor_data.available is True
    assert sensor_data.total_power == -500
    assert len(sensor_data.phase) == 1


def test_ems_device_creation():
    """Test EmsDevice creation."""
    ems_info = EmsInfo(1, "1.0.0", 10000, 5000)
    bms_info = [BmsInfo("1.0.0", "BMS001", 10000, 1)]
    inv_info = InvInfo("1.0.0", "INV001")
    
    # Create simple configs for the device
    ems_config = EmsConfig(
        grid_code_preset=1,
        grid_code_preset_str="Test",
        control_timeout=False
    )
    
    inv_config = InvConfig(ffr_fstart_freq=50)
    
    # Create a minimal EmsDevice using from_dict to avoid complex construction
    device_data = {
        "ecu_id": 1,
        "ecu_host": "192.168.1.100",
        "ecu_version": "1.0.0",
        "error": 0,
        "error_str": "",
        "op_state": 1,
        "op_state_str": "Active"
    }
    
    ems_device = EmsDevice.from_dict(device_data)
    
    assert ems_device.ecu_id == 1
    assert ems_device.ecu_host == "192.168.1.100"
    assert ems_device.ecu_version == "1.0.0"
    assert ems_device.op_state_str == "Active"


def test_homevolt_data_creation():
    """Test HomevoltData creation using from_dict."""
    minimal_data = {
        "$type": "homevolt_data", 
        "ts": 1640995200,
        "ems": [],
        "aggregated": {},
        "sensors": []
    }
    
    homevolt_data = HomevoltData.from_dict(minimal_data)
    
    assert homevolt_data.type == "homevolt_data"
    assert homevolt_data.ts == 1640995200
    assert len(homevolt_data.ems) == 0
    assert len(homevolt_data.sensors) == 0
    assert homevolt_data.aggregated is not None


def test_homevolt_data_from_dict(sample_homevolt_data):
    """Test HomevoltData.from_dict method with sample data."""
    homevolt_data = HomevoltData.from_dict(sample_homevolt_data)
    
    assert homevolt_data.type == "homevolt_data"
    assert homevolt_data.ts == 1640995200
    assert len(homevolt_data.ems) == 1
    assert len(homevolt_data.sensors) == 1
    
    # Test EMS device
    ems = homevolt_data.ems[0]
    assert ems.ecu_id == 1
    assert ems.ecu_host == "192.168.1.100"
    
    # Test sensor data
    sensor = homevolt_data.sensors[0]
    assert sensor.type == "grid"
    assert sensor.euid == "SENSOR001"
    assert sensor.total_power == -500


def test_homevolt_data_from_dict_missing_data():
    """Test HomevoltData.from_dict with missing data."""
    minimal_data = {
        "ems": [],
        "sensors": []
    }
    
    homevolt_data = HomevoltData.from_dict(minimal_data)
    
    assert homevolt_data.type == ""
    assert homevolt_data.ts == 0
    assert len(homevolt_data.ems) == 0
    assert len(homevolt_data.sensors) == 0


def test_ems_info_from_dict():
    """Test EmsInfo.from_dict method."""
    data = {
        "protocol_version": 2,
        "fw_version": "2.0.0",
        "rated_capacity": 15000,
        "rated_power": 7500
    }
    
    ems_info = EmsInfo.from_dict(data)
    
    assert ems_info.protocol_version == 2
    assert ems_info.fw_version == "2.0.0"
    assert ems_info.rated_capacity == 15000
    assert ems_info.rated_power == 7500


def test_sensor_data_from_dict():
    """Test SensorData.from_dict method."""
    data = {
        "type": "solar",
        "node_id": 2,
        "euid": "SENSOR002",
        "interface": 1,
        "available": True,
        "rssi": -45,
        "average_rssi": -47.2,
        "pdr": 99.1,
        "phase": [
            {
                "voltage": 235.0,
                "amp": 8.5,
                "power": 1997.5,
                "pf": 0.99
            }
        ],
        "frequency": 50,
        "total_power": 2000,
        "energy_imported": 0.0,
        "energy_exported": 200.5,
        "timestamp": 1640995200
    }
    
    sensor_data = SensorData.from_dict(data)
    
    assert sensor_data.type == "solar"
    assert sensor_data.node_id == 2
    assert sensor_data.euid == "SENSOR002"
    assert sensor_data.total_power == 2000
    assert len(sensor_data.phase) == 1
    assert sensor_data.phase[0].voltage == 235.0