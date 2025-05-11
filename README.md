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

1. Copy the `custom_components/homevolt` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Homevolt Local"
4. Follow the configuration steps:
   - Enter the API URL
   - Enter your username and password
   - Configure optional settings (SSL verification, scan interval, timeout)

## Sensors

This integration provides the following sensors:

1. **Homevolt Status**: Shows the current state of the EMS with a dynamic icon that changes based on the battery level
2. **Homevolt Error**: Shows error information when available
3. **Homevolt battery 1 SoC**: Shows the state of charge for battery 1 as a percentage
4. **Homevolt battery 2 SoC**: Shows the state of charge for battery 2 as a percentage
5. **Homevolt Total SoC**: Shows the total state of charge as a percentage
6. **Homevolt effekt**: Shows the current power in watts
7. **Homevolt energi producerat**: Shows the energy produced in kilowatts
8. **Homevolt energi konsumerat**: Shows the energy consumed in kilowatts

## Troubleshooting

- If you encounter connection issues, check your API URL and credentials
- Verify that your Homevolt Local is online and accessible from your Home Assistant instance
- Check the Home Assistant logs for detailed error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
