"""Constants for the Homevolt Local integration."""

DOMAIN = "homevolt_local"

# Configuration constants
CONF_RESOURCE = "resource"
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_TIMEOUT = 30
DEFAULT_RESOURCE_PATH = "/ems.json"

# Attribute keys from the API response
ATTR_EMS = "ems"
ATTR_AGGREGATED = "aggregated"
ATTR_SENSORS = "sensors"
ATTR_EMS_DATA = "ems_data"
ATTR_STATE_STR = "state_str"
ATTR_SOC_AVG = "soc_avg"
ATTR_ERROR_STR = "error_str"
ATTR_POWER = "power"
ATTR_ENERGY_PRODUCED = "energy_produced"
ATTR_ENERGY_CONSUMED = "energy_consumed"

# Sensor data attributes
ATTR_TOTAL_POWER = "total_power"
ATTR_ENERGY_IMPORTED = "energy_imported"
ATTR_ENERGY_EXPORTED = "energy_exported"
ATTR_PHASE = "phase"
