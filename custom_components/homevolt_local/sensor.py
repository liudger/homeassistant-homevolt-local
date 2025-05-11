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
    ATTR_EMS,
    ATTR_EMS_DATA,
    ATTR_ENERGY_CONSUMED,
    ATTR_ENERGY_EXPORTED,
    ATTR_ENERGY_IMPORTED,
    ATTR_ENERGY_PRODUCED,
    ATTR_ERROR_STR,
    ATTR_PHASE,
    ATTR_POWER,
    ATTR_SENSORS,
    ATTR_SOC_AVG,
    ATTR_STATE_STR,
    ATTR_TOTAL_POWER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HomevoltSensorEntityDescription(SensorEntityDescription):
    """Describes Homevolt sensor entity."""

    value_fn: Callable[[Dict[str, Any]], Any] = None
    icon_fn: Callable[[Dict[str, Any]], str] = None
    attrs_fn: Callable[[Dict[str, Any]], Dict[str, Any]] = None


SENSOR_DESCRIPTIONS: tuple[HomevoltSensorEntityDescription, ...] = (
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
        key="battery_1_soc",
        name="Homevolt battery 1 SoC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        value_fn=lambda data: float(data[ATTR_EMS][0]["bms_data"][0]["soc"]) / 100,
    ),
    HomevoltSensorEntityDescription(
        key="battery_2_soc",
        name="Homevolt battery 2 SoC",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement="%",
        value_fn=lambda data: float(data[ATTR_EMS][1]["bms_data"][0]["soc"]) / 100,
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
)


class HomevoltSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Homevolt sensor."""

    entity_description: HomevoltSensorEntityDescription

    def __init__(
        self, 
        coordinator: HomevoltDataUpdateCoordinator,
        description: HomevoltSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = self.device_info

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this Homevolt device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry_id)},
            name="Homevolt Local",
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

            # Set value using the value_fn from the description
            if self.entity_description.value_fn:
                self._attr_native_value = self.entity_description.value_fn(data)

            # Set icon using the icon_fn from the description if available
            if self.entity_description.icon_fn:
                self._attr_icon = self.entity_description.icon_fn(data)

            # Set attributes using the attrs_fn from the description if available
            if self.entity_description.attrs_fn:
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

    sensors = [
        HomevoltSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(sensors)
