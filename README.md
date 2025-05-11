# Homevolt Local Integration for Home Assistant

This is a custom integration for Home Assistant that connects to a Homevolt Energy Management System (EMS) and provides sensor data.

## Features

- Monitors the state of your Homevolt Local
- Displays battery level with dynamic icons
- Shows error information when available
- Configurable through the Home Assistant UI

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the three dots in the top right corner
   - Select "Custom repositories"
   - Add the URL of this repository and select "Integration" as the category
3. Click "Install" on the Homevolt Local integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/homevolt_local` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Homevolt Local"
4. Follow the configuration steps:
   - Enter the IP address or hostname of your Homevolt system
   - Enter your username and password
   - Configure optional settings (SSL verification, scan interval, timeout)

### Multiple IP Addresses

If your Homevolt system has multiple IP addresses (for example, if you have multiple controllers that are linked together), you can add each IP address as a separate integration. The integration will automatically detect and prevent duplicate devices and sensors for the same physical devices.

To add multiple IP addresses:

1. Add the first IP address as described above
2. Repeat the process for each additional IP address
3. The integration will use unique identifiers for each device based on their internal IDs, ensuring that the same physical device is represented only once in Home Assistant, regardless of which IP address it's accessed through

## Devices and Sensors

This integration detects and creates separate devices for each Energy Management System (EMS) unit and sensor found in your Homevolt Local system. Each device has its own set of sensors, and there are also aggregated sensors that show combined data from all devices.

### Aggregated Sensors

These sensors show combined data from all EMS units:

1. **Homevolt Status**: Shows the current state of the EMS with a dynamic icon that changes based on the battery level
2. **Homevolt Error**: Shows error information when available
3. **Homevolt Total SoC**: Shows the total state of charge as a percentage
4. **Homevolt effekt**: Shows the current power in watts
5. **Homevolt energi producerat**: Shows the energy produced in kilowatts
6. **Homevolt energi konsumerat**: Shows the energy consumed in kilowatts

### EMS Device-Specific Sensors

Each EMS device will have the following sensors:

1. **Homevolt battery SoC**: Shows the state of charge for the battery as a percentage
2. **Status**: Shows the current state of the specific EMS device
3. **Power**: Shows the power of the specific EMS device in watts
4. **Energy Produced**: Shows the energy produced by the specific EMS device in kilowatts
5. **Energy Consumed**: Shows the energy consumed by the specific EMS device in kilowatts
6. **Error**: Shows error information specific to the device when available

### Sensor Devices

The integration also creates separate devices for each sensor in the system:

#### Grid Sensor

The Grid sensor device provides information about the power flow to and from the grid:

1. **Power**: Shows the current power flow in watts (positive for import, negative for export)
2. **Energy Imported**: Shows the total energy imported from the grid in kilowatt-hours
3. **Energy Exported**: Shows the total energy exported to the grid in kilowatt-hours

#### Solar Sensor

The Solar sensor device provides information about your solar production:

1. **Power**: Shows the current solar power production in watts
2. **Energy Imported**: Shows the total energy imported from the solar system in kilowatt-hours
3. **Energy Exported**: Shows the total energy exported to the solar system in kilowatt-hours

#### Load Sensor

The Load sensor device provides information about your household consumption:

1. **Power**: Shows the current power consumption in watts
2. **Energy Imported**: Shows the total energy imported by the loads in kilowatt-hours
3. **Energy Exported**: Shows the total energy exported by the loads in kilowatt-hours

## Troubleshooting

- If you encounter connection issues, check your API URL and credentials
- Verify that your Homevolt Local is online and accessible from your Home Assistant instance
- Check the Home Assistant logs for detailed error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
