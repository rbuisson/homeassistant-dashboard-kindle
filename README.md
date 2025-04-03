# Kindle Web Controller

A simple web interface to control Home Assistant entities, optimized for Kindle devices. This addon provides a high-contrast interface with buttons to toggle lights, switches, and relays.

## Features
- High-contrast design for better visibility on Kindle devices.
- Periodic updates to reflect the current state of entities.
- Simple buttons to toggle entity states (e.g., turn lights on/off).

## Installation
1. Copy the `my-addon` folder into your Home Assistant `addons` directory.
2. Restart Home Assistant to detect the new addon.
3. Install the addon from the **Add-on Store** in the Home Assistant UI.

## Usage
1. Start the addon from the Home Assistant **Add-on Store**.
2. Access the web interface at `http://<home_assistant_ip>:8080`.
3. Use the buttons to toggle the state of your entities.

## Configuration
No additional configuration is required. The addon uses the Home Assistant API to fetch and update entity states.

## Development
- The web interface is served using a simple Python HTTP server.
- The frontend is written in HTML, CSS, and JavaScript.

## Notes
- Ensure your Home Assistant instance allows API access with a valid long-lived access token.
- Update the `HA_URL` and `TOKEN` in `www/index.html` to match your Home Assistant setup.