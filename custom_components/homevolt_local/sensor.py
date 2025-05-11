"""Sensor platform for Homevolt Local integration."""
from __future__ import annotations

import logging
from typing import Any, Callable, Dict

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import HomevoltDataUpdateCoordinator
from .const import (
    ATTR_AGGREGATED,
    ATTR_AVAILABLE,
    ATTR_EMS,
    ATTR_EMS_DATA,
    ATTR_ENERGY_CONSUMED,
    ATTR_ENERGY_EXPORTED,
    ATTR_ENERGY_IMPORTED,
    ATTR_ENERGY_PRODUCED,
    ATTR_ERROR_STR,
    ATTR_EUID,
    ATTR_NODE_ID,
    ATTR_PHASE,
    ATTR_POWER,
    ATTR_SENSORS,
    ATTR_SOC_AVG,
    ATTR_STATE_STR,
    ATTR_TIMESTAMP,
    ATTR_TOTAL_POWER,
    ATTR_TYPE,
    DOMAIN,
    SENSOR_TYPE_GRID,
    SENSOR_TYPE_LOAD,
    SENSOR_TYPE_SOLAR,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HomevoltSensorEntityDescription(SensorEntityDescription):
    """Describes Homevolt sensor entity."""

    value_fn: Callable[[Dict[str, Any]], Any] = None
    icon_fn: Callable[[Dict[str, Any]], str] = None
    attrs_fn: Callable[[Dict[str, Any]], Dict[str, Any]] = None
    device_specific: bool = False  # Whether this sensor is specific to a device in the ems array
    sensor_specific: bool = False  # Whether this sensor is specific to a device in the sensors array
    sensor_type: str = None  # The type of sensor this entity is for (grid, solar, load)


SENSOR_DESCRIPTIONS: tuple[HomevoltSensorEntityDescription, ...] = (
    # Aggregated device sensors
    HomevoltSensorEntityDescription(
        key="ems",
        name="Homevolt Status",
        value_fn=lambda data: data[ATTR_AGGREGATED][ATTR_EMS_DATA][ATTR_STATE_STR],
        icon_fn=lambda data: (
            "mdi:battery-outline"
            if float(data[ATTR_AGGREGATED][ATTR_EMS_DATA][ATTR_SOC_AVG]) < 5
            else f"mdi:battery-{int(round(float(data[ATTR_AGGREGATED][ATTR_EMS_DATA][ATTR_SOC_AVG]) / 10.0) * 10)}"
        ),
        attrs_fn=lambda data: {
            ATTR_EMS: data.get(ATTR_EMS, {}),
            ATTR_AGGREGATED: data.get(ATTR_AGGREGATED, {}),
            ATTR_SENSORS: data.get(ATTR_SENSORS, {}),
        },
    ),
    HomevoltSensorEntityDescription(
        key="ems_error",
        name="Homevolt Error",
        icon="mdi:battery-unknown",
        value_fn=lambda data: data[ATTR_AGGREGATED][ATTR_ERROR_STR][:255] if data[ATTR_AGGREGATED][ATTR_ERROR_STR] else None,
        attrs_fn=lambda data: {
            ATTR_ERROR_STR: data[ATTR_AGGREGATED][ATTR_ERROR_STR],
        },
    ),
    HomevoltSensorEntityDescription(
        key="battery_soc",
        name="Homevolt battery SoC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        value_fn=lambda data, idx=0: float(data[ATTR_EMS][idx]["bms_data"][0]["soc"]) / 100,
        device_specific=True,
    ),
    HomevoltSensorEntityDescription(
        key="total_soc",
        name="Homevolt Total SoC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        value_fn=lambda data: float(data[ATTR_AGGREGATED]["bms_data"][1]["soc"]) / 100,
    ),
    HomevoltSensorEntityDescription(
        key="power",
        name="Homevolt effekt",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="W",
        icon="mdi:battery-sync-outline",
        value_fn=lambda data: data[ATTR_AGGREGATED][ATTR_EMS_DATA][ATTR_POWER],
    ),
    HomevoltSensorEntityDescription(
        key="energy_produced",
        name="Homevolt energi producerat",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="kW",
        icon="mdi:battery-positive",
        value_fn=lambda data: float(data[ATTR_AGGREGATED][ATTR_EMS_DATA][ATTR_ENERGY_PRODUCED]) / 1000,
    ),
    HomevoltSensorEntityDescription(
        key="energy_consumed",
        name="Homevolt energi konsumerat",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="kW",
        icon="mdi:battery-negative",
        value_fn=lambda data: float(data[ATTR_AGGREGATED][ATTR_EMS_DATA][ATTR_ENERGY_CONSUMED]) / 1000,
    ),
    # Device-specific sensors for each EMS device
    HomevoltSensorEntityDescription(
        key="device_status",
        name="Status",
        value_fn=lambda data, idx=0: data[ATTR_EMS][idx][ATTR_EMS_DATA][ATTR_STATE_STR],
        icon_fn=lambda data, idx=0: (
            "mdi:battery-outline"
            if float(data[ATTR_EMS][idx][ATTR_EMS_DATA][ATTR_SOC_AVG]) < 5
            else f"mdi:battery-{int(round(float(data[ATTR_EMS][idx][ATTR_EMS_DATA][ATTR_SOC_AVG]) / 10.0) * 10)}"
        ),
        device_specific=True,
    ),
    HomevoltSensorEntityDescription(
        key="device_power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="W",
        icon="mdi:battery-sync-outline",
        value_fn=lambda data, idx=0: data[ATTR_EMS][idx][ATTR_EMS_DATA][ATTR_POWER],
        device_specific=True,
    ),
    HomevoltSensorEntityDescription(
        key="device_energy_produced",
        name="Energy Produced",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="kW",
        icon="mdi:battery-positive",
        value_fn=lambda data, idx=0: float(data[ATTR_EMS][idx][ATTR_EMS_DATA][ATTR_ENERGY_PRODUCED]) / 1000,
        device_specific=True,
    ),
    HomevoltSensorEntityDescription(
        key="device_energy_consumed",
        name="Energy Consumed",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement="kW",
        icon="mdi:battery-negative",
        value_fn=lambda data, idx=0: float(data[ATTR_EMS][idx][ATTR_EMS_DATA][ATTR_ENERGY_CONSUMED]) / 1000,
        device_specific=True,
    ),
    HomevoltSensorEntityDescription(
        key="device_error",
        name="Error",
        icon="mdi:battery-unknown",
        value_fn=lambda data, idx=0: data[ATTR_EMS][idx][ATTR_ERROR_STR][:255] if data[ATTR_EMS][idx][ATTR_ERROR_STR] else None,
        attrs_fn=lambda data, idx=0: {
            ATTR_ERROR_STR: data[ATTR_EMS][idx][ATTR_ERROR_STR],
        },
        device_specific=True,
    ),

    # Sensor-specific sensors for grid, solar, and load
    # Grid sensors
    HomevoltSensorEntityDescription(
        key="grid_power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="W",
        icon="mdi:transmission-tower",
        value_fn=lambda data, idx=0: data[ATTR_SENSORS][idx][ATTR_TOTAL_POWER],
        attrs_fn=lambda data, idx=0: {
            ATTR_PHASE: data[ATTR_SENSORS][idx][ATTR_PHASE],
        },
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_GRID,
    ),
    HomevoltSensorEntityDescription(
        key="grid_energy_imported",
        name="Energy Imported",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="kWh",
        icon="mdi:transmission-tower-import",
        value_fn=lambda data, idx=0: data[ATTR_SENSORS][idx][ATTR_ENERGY_IMPORTED],
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_GRID,
    ),
    HomevoltSensorEntityDescription(
        key="grid_energy_exported",
        name="Energy Exported",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="kWh",
        icon="mdi:transmission-tower-export",
        value_fn=lambda data, idx=0: data[ATTR_SENSORS][idx][ATTR_ENERGY_EXPORTED],
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_GRID,
    ),

    # Solar sensors
    HomevoltSensorEntityDescription(
        key="solar_power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="W",
        icon="mdi:solar-power",
        value_fn=lambda data, idx=1: data[ATTR_SENSORS][idx][ATTR_TOTAL_POWER],
        attrs_fn=lambda data, idx=1: {
            ATTR_PHASE: data[ATTR_SENSORS][idx][ATTR_PHASE],
        },
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_SOLAR,
    ),
    HomevoltSensorEntityDescription(
        key="solar_energy_imported",
        name="Energy Imported",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="kWh",
        icon="mdi:solar-power-variant",
        value_fn=lambda data, idx=1: data[ATTR_SENSORS][idx][ATTR_ENERGY_IMPORTED],
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_SOLAR,
    ),
    HomevoltSensorEntityDescription(
        key="solar_energy_exported",
        name="Energy Exported",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="kWh",
        icon="mdi:solar-power-variant-outline",
        value_fn=lambda data, idx=1: data[ATTR_SENSORS][idx][ATTR_ENERGY_EXPORTED],
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_SOLAR,
    ),

    # Load sensors
    HomevoltSensorEntityDescription(
        key="load_power",
        name="Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="W",
        icon="mdi:home-lightning-bolt",
        value_fn=lambda data, idx=2: data[ATTR_SENSORS][idx][ATTR_TOTAL_POWER],
        attrs_fn=lambda data, idx=2: {
            ATTR_PHASE: data[ATTR_SENSORS][idx][ATTR_PHASE],
        },
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_LOAD,
    ),
    HomevoltSensorEntityDescription(
        key="load_energy_imported",
        name="Energy Imported",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="kWh",
        icon="mdi:home-import-outline",
        value_fn=lambda data, idx=2: data[ATTR_SENSORS][idx][ATTR_ENERGY_IMPORTED],
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_LOAD,
    ),
    HomevoltSensorEntityDescription(
        key="load_energy_exported",
        name="Energy Exported",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        native_unit_of_measurement="kWh",
        icon="mdi:home-export-outline",
        value_fn=lambda data, idx=2: data[ATTR_SENSORS][idx][ATTR_ENERGY_EXPORTED],
        sensor_specific=True,
        sensor_type=SENSOR_TYPE_LOAD,
    ),
)


class HomevoltSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Homevolt sensor."""

    entity_description: HomevoltSensorEntityDescription

    def __init__(
        self, 
        coordinator: HomevoltDataUpdateCoordinator,
        description: HomevoltSensorEntityDescription,
        ems_index: int = None,
        sensor_index: int = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self.ems_index = ems_index
        self.sensor_index = sensor_index

        # Create a unique ID based on the device properties if available
        if ems_index is not None and coordinator.data and ATTR_EMS in coordinator.data:
            try:
                # Use the ecu_id for a consistent unique ID across different IP addresses
                ems_data = coordinator.data[ATTR_EMS][ems_index]
                ecu_id = ems_data.get(ATTR_ECU_ID, f"unknown_{ems_index}")
                self._attr_unique_id = f"{DOMAIN}_{description.key}_ems_{ecu_id}"
            except (KeyError, IndexError):
                # Fallback to a generic unique ID if we can't get the ecu_id
                self._attr_unique_id = f"{DOMAIN}_{description.key}_ems_{ems_index}"
        elif sensor_index is not None and coordinator.data and ATTR_SENSORS in coordinator.data:
            try:
                # Use the euid for a consistent unique ID across different IP addresses
                sensor_data = coordinator.data[ATTR_SENSORS][sensor_index]
                euid = sensor_data.get(ATTR_EUID, f"unknown_{sensor_index}")
                self._attr_unique_id = f"{DOMAIN}_{description.key}_sensor_{euid}"
            except (KeyError, IndexError):
                # Fallback to a generic unique ID if we can't get the euid
                self._attr_unique_id = f"{DOMAIN}_{description.key}_sensor_{sensor_index}"
        else:
            # For aggregated sensors, use the host from the resource URL for a consistent unique ID
            host = coordinator.resource.split("://")[1].split("/")[0]
            self._attr_unique_id = f"{DOMAIN}_{description.key}_{host}"

        self._attr_device_info = self.device_info

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Homevolt device."""
        # Main aggregated device ID - use the host from the resource URL to make it consistent
        # across different config entries for the same physical system
        host = self.coordinator.resource.split("://")[1].split("/")[0]
        main_device_id = f"homevolt_{host}"

        if self.ems_index is not None and self.coordinator.data:
            # Get device-specific information from the ems data
            try:
                ems_data = self.coordinator.data[ATTR_EMS][self.ems_index]
                ecu_id = ems_data.get(ATTR_ECU_ID, f"unknown_{self.ems_index}")
                serial_number = ems_data.get("inv_info", {}).get(ATTR_SERIAL_NUMBER, "")

                # Try to get more detailed information for the device name
                fw_version = ems_data.get("ems_info", {}).get(ATTR_FW_VERSION, "")

                # Use the ecu_id as the unique identifier, which should be consistent
                # across different IP addresses for the same physical device
                return DeviceInfo(
                    identifiers={(DOMAIN, f"ems_{ecu_id}")},
                    name=f"Homevolt EMS {ecu_id}",
                    manufacturer="Homevolt",
                    model=f"Energy Management System {fw_version}",
                    entry_type=DeviceEntryType.SERVICE,
                    via_device=(DOMAIN, main_device_id),  # Link to the main device
                    sw_version=fw_version,
                    hw_version=serial_number,
                )
            except (KeyError, IndexError):
                # Fallback to a generic device info if we can't get specific info
                return DeviceInfo(
                    identifiers={(DOMAIN, f"ems_unknown_{self.ems_index}")},
                    name=f"Homevolt EMS {self.ems_index + 1}",
                    manufacturer="Homevolt",
                    model="Energy Management System",
                    entry_type=DeviceEntryType.SERVICE,
                    via_device=(DOMAIN, main_device_id),  # Link to the main device
                )
        elif self.sensor_index is not None and self.coordinator.data and ATTR_SENSORS in self.coordinator.data:
            # Get device-specific information from the sensors data
            try:
                sensor_data = self.coordinator.data[ATTR_SENSORS][self.sensor_index]
                sensor_type = sensor_data.get(ATTR_TYPE, "unknown")
                node_id = sensor_data.get(ATTR_NODE_ID, 0)
                euid = sensor_data.get(ATTR_EUID, "unknown")

                # Capitalize the first letter of the sensor type for the name
                sensor_type_name = sensor_type.capitalize()

                # Use the euid as the unique identifier, which should be consistent
                # across different IP addresses for the same physical sensor
                return DeviceInfo(
                    identifiers={(DOMAIN, f"sensor_{euid}")},
                    name=f"Homevolt {sensor_type_name}",
                    manufacturer="Homevolt",
                    model=f"{sensor_type_name} Sensor (Node {node_id})",
                    entry_type=DeviceEntryType.SERVICE,
                    via_device=(DOMAIN, main_device_id),  # Link to the main device
                )
            except (KeyError, IndexError):
                # Fallback to a generic device info if we can't get specific info
                return DeviceInfo(
                    identifiers={(DOMAIN, f"sensor_unknown_{self.sensor_index}")},
                    name=f"Homevolt Sensor {self.sensor_index + 1}",
                    manufacturer="Homevolt",
                    model="Sensor",
                    entry_type=DeviceEntryType.SERVICE,
                    via_device=(DOMAIN, main_device_id),  # Link to the main device
                )
        else:
            # For aggregated sensors or if no ems_index or sensor_index is provided
            return DeviceInfo(
                identifiers={(DOMAIN, main_device_id)},
                name=f"Homevolt Local ({host})",
                manufacturer="Homevolt",
                model="Energy Management System",
                entry_type=DeviceEntryType.SERVICE,
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is None:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
            self.async_write_ha_state()
            return

        try:
            data = self.coordinator.data

            # Check if this is a device-specific sensor and if the device exists
            if self.ems_index is not None and ATTR_EMS in data:
                # Verify the device index is valid
                if len(data[ATTR_EMS]) <= self.ems_index:
                    _LOGGER.error(
                        "Device index %s is out of range for %s (only %s devices available)",
                        self.ems_index,
                        self.entity_description.name,
                        len(data[ATTR_EMS]),
                    )
                    self._attr_native_value = None
                    self._attr_extra_state_attributes = {}
                    self.async_write_ha_state()
                    return

            # Check if this is a sensor-specific sensor and if the sensor exists
            elif self.sensor_index is not None and ATTR_SENSORS in data:
                # Verify the sensor index is valid
                if len(data[ATTR_SENSORS]) <= self.sensor_index:
                    _LOGGER.error(
                        "Sensor index %s is out of range for %s (only %s sensors available)",
                        self.sensor_index,
                        self.entity_description.name,
                        len(data[ATTR_SENSORS]),
                    )
                    self._attr_native_value = None
                    self._attr_extra_state_attributes = {}
                    self.async_write_ha_state()
                    return

                # Verify the sensor type matches the expected type
                if self.entity_description.sensor_type:
                    sensor_type = data[ATTR_SENSORS][self.sensor_index].get(ATTR_TYPE)
                    if sensor_type != self.entity_description.sensor_type:
                        _LOGGER.error(
                            "Sensor type mismatch for %s: expected %s, got %s",
                            self.entity_description.name,
                            self.entity_description.sensor_type,
                            sensor_type,
                        )
                        self._attr_native_value = None
                        self._attr_extra_state_attributes = {}
                        self.async_write_ha_state()
                        return

            # Set value using the value_fn from the description
            if self.entity_description.value_fn:
                if self.ems_index is not None:
                    # For device-specific sensors, pass the device index to the value_fn
                    self._attr_native_value = self.entity_description.value_fn(data, self.ems_index)
                elif self.sensor_index is not None:
                    # For sensor-specific sensors, pass the sensor index to the value_fn
                    self._attr_native_value = self.entity_description.value_fn(data, self.sensor_index)
                else:
                    # For aggregated sensors, just pass the data
                    self._attr_native_value = self.entity_description.value_fn(data)

            # Set icon using the icon_fn from the description if available
            if self.entity_description.icon_fn:
                if self.ems_index is not None:
                    # For device-specific sensors, pass the device index to the icon_fn
                    self._attr_icon = self.entity_description.icon_fn(data, self.ems_index)
                elif self.sensor_index is not None:
                    # For sensor-specific sensors, pass the sensor index to the icon_fn
                    self._attr_icon = self.entity_description.icon_fn(data, self.sensor_index)
                else:
                    # For aggregated sensors, just pass the data
                    self._attr_icon = self.entity_description.icon_fn(data)

            # Set attributes using the attrs_fn from the description if available
            if self.entity_description.attrs_fn:
                if self.ems_index is not None:
                    # For device-specific sensors, pass the device index to the attrs_fn
                    self._attr_extra_state_attributes = self.entity_description.attrs_fn(data, self.ems_index)
                elif self.sensor_index is not None:
                    # For sensor-specific sensors, pass the sensor index to the attrs_fn
                    self._attr_extra_state_attributes = self.entity_description.attrs_fn(data, self.sensor_index)
                else:
                    # For aggregated sensors, just pass the data
                    self._attr_extra_state_attributes = self.entity_description.attrs_fn(data)

        except (KeyError, TypeError, IndexError, ValueError) as err:
            _LOGGER.error("Error extracting sensor data for %s: %s", self.entity_description.name, err)
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}

        self.async_write_ha_state()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Homevolt Local sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    # Create non-device-specific sensors (aggregated data)
    for description in SENSOR_DESCRIPTIONS:
        if not description.device_specific and not description.sensor_specific:
            sensors.append(HomevoltSensor(coordinator, description))

    # Check if we have data and if the ems array exists
    if coordinator.data and ATTR_EMS in coordinator.data:
        ems_data = coordinator.data[ATTR_EMS]

        # Create device-specific sensors for each device in the ems array
        for idx, _ in enumerate(ems_data):
            for description in SENSOR_DESCRIPTIONS:
                if description.device_specific:
                    # Create a modified value_fn that includes the device index
                    if description.value_fn:
                        # Create a copy of the description to avoid modifying the original
                        modified_description = HomevoltSensorEntityDescription(
                            key=description.key,
                            name=description.name,
                            device_class=description.device_class,
                            native_unit_of_measurement=description.native_unit_of_measurement,
                            icon=description.icon,
                            device_specific=description.device_specific,
                        )

                        # Create a wrapper function that passes the device index to the original value_fn
                        original_value_fn = description.value_fn
                        modified_description.value_fn = lambda data, orig_fn=original_value_fn, device_idx=idx: orig_fn(data, device_idx)

                        # If there's an icon_fn, create a wrapper for it too
                        if description.icon_fn:
                            original_icon_fn = description.icon_fn
                            modified_description.icon_fn = lambda data, orig_fn=original_icon_fn, device_idx=idx: orig_fn(data, device_idx)

                        # If there's an attrs_fn, create a wrapper for it too
                        if description.attrs_fn:
                            original_attrs_fn = description.attrs_fn
                            modified_description.attrs_fn = lambda data, orig_fn=original_attrs_fn, device_idx=idx: orig_fn(data, device_idx)

                        sensors.append(HomevoltSensor(coordinator, modified_description, idx))
                    else:
                        sensors.append(HomevoltSensor(coordinator, description, idx))

    # Check if we have data and if the sensors array exists
    if coordinator.data and ATTR_SENSORS in coordinator.data:
        sensors_data = coordinator.data[ATTR_SENSORS]

        # Create a mapping of sensor types to their indices
        sensor_type_to_index = {}
        for idx, sensor in enumerate(sensors_data):
            sensor_type = sensor.get(ATTR_TYPE)
            if sensor_type:
                sensor_type_to_index[sensor_type] = idx

        # Create sensor-specific sensors for each sensor in the sensors array
        for description in SENSOR_DESCRIPTIONS:
            if description.sensor_specific and description.sensor_type:
                # Check if we have a sensor of this type
                if description.sensor_type in sensor_type_to_index:
                    idx = sensor_type_to_index[description.sensor_type]

                    # Create a modified value_fn that includes the sensor index
                    if description.value_fn:
                        # Create a copy of the description to avoid modifying the original
                        modified_description = HomevoltSensorEntityDescription(
                            key=description.key,
                            name=description.name,
                            device_class=description.device_class,
                            state_class=description.state_class,
                            native_unit_of_measurement=description.native_unit_of_measurement,
                            icon=description.icon,
                            sensor_specific=description.sensor_specific,
                            sensor_type=description.sensor_type,
                        )

                        # Create a wrapper function that passes the sensor index to the original value_fn
                        original_value_fn = description.value_fn
                        modified_description.value_fn = lambda data, orig_fn=original_value_fn, sensor_idx=idx: orig_fn(data, sensor_idx)

                        # If there's an icon_fn, create a wrapper for it too
                        if description.icon_fn:
                            original_icon_fn = description.icon_fn
                            modified_description.icon_fn = lambda data, orig_fn=original_icon_fn, sensor_idx=idx: orig_fn(data, sensor_idx)

                        # If there's an attrs_fn, create a wrapper for it too
                        if description.attrs_fn:
                            original_attrs_fn = description.attrs_fn
                            modified_description.attrs_fn = lambda data, orig_fn=original_attrs_fn, sensor_idx=idx: orig_fn(data, sensor_idx)

                        sensors.append(HomevoltSensor(coordinator, modified_description, None, idx))
                    else:
                        sensors.append(HomevoltSensor(coordinator, description, None, idx))

    async_add_entities(sensors)
