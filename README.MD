# Home Assistant Users Integration

Creates sensors for each Home Assistant user account with their details, this is useful for a number of reasons:

- Provides a clear list of users and permissions to be able to audit access levels
- Assist with troubleshooting access issues
- Most notably, provides a way to map a user ID to a username i.e. userid of the user who triggered a script

## Installation

### HACS (Recommended)
1. Open HACS
2. Go to Integrations
3. Click the three dots in the top right
4. Select "Custom repositories"
5. Add this repository URL ( https://github.com/lukegackle/Home-Assistant-User-Info-Integration )
6. Select "Integration" as the category
7. Click "Install"
8. Restart Home Assistant

### Manual
1. Copy the `ha_users` folder to your `custom_components` directory
2. Restart Home Assistant

## Configuration

Add to your `configuration.yaml`:
```yaml
ha_users:
```

Then restart Home Assistant.

## Features

- Automatically creates a sensor for each user
- Updates every 6 hours
- Includes user attributes:
  - User ID
  - Is Owner
  - Is Active
  - Local Only
  - System Generated
  - Group IDs
  - Has Credentials

## Sensors

Sensors will be created with the format: `sensor.ha_user_<username>`

Example: `sensor.ha_user_luke`

## Support

Please note that this integration has been developed with the use of AI, though it has passed all of my testing and code review, I am not a Home Assistant developer and I make no guarantees about the quality of the code, you are welcome to perform your own review of the code before use, use at your own risk. 
If you have any issues with this integration feel free to report them and any detailed information about how to reproduce the issue and I will do my best to investigate.
Report issues at: https://github.com/lukegackle/Home-Assistant-User-Info-Integration/issues