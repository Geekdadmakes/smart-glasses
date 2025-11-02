# Smart Home Integration Setup Guide

## Overview
The smart glasses now support controlling your smart home devices using voice commands! This integration works with **Home Assistant**, the popular open-source smart home platform.

## Features
- Turn devices on/off (lights, switches, etc.)
- Set brightness levels for lights
- Control thermostat temperature
- Activate scenes/routines
- Check device status

## Setup Instructions

### Option 1: Home Assistant (Recommended)

#### Prerequisites
- Home Assistant installed and running (https://www.home-assistant.io/)
- Network access from your Raspberry Pi to Home Assistant

#### Steps

1. **Get a Long-Lived Access Token from Home Assistant:**
   - Log into your Home Assistant web interface
   - Click your profile (bottom left)
   - Scroll down to "Long-Lived Access Tokens"
   - Click "Create Token"
   - Give it a name (e.g., "Smart Glasses")
   - Copy the token (you'll only see it once!)

2. **Set Environment Variables on Your Pi:**
   ```bash
   # Add to ~/.bashrc or ~/.profile
   export HOME_ASSISTANT_URL="http://YOUR_HA_IP:8123"
   export HOME_ASSISTANT_TOKEN="your_long_lived_token_here"

   # Reload environment
   source ~/.bashrc
   ```

3. **Configure Device Mappings:**
   Edit the config file at `~/smart-glasses/memory/smart_home/config.json`:

   ```json
   {
     "home_assistant_url": "http://192.168.1.100:8123",
     "home_assistant_token": "your_token_here",
     "devices": {
       "living room light": "light.living_room",
       "bedroom light": "light.bedroom",
       "kitchen light": "light.kitchen",
       "thermostat": "climate.main_thermostat",
       "tv": "switch.tv_power"
     },
     "scenes": {
       "movie time": "scene.movie_mode",
       "good morning": "scene.morning_routine",
       "good night": "scene.bedtime",
       "relax": "scene.relax"
     }
   }
   ```

4. **Find Your Entity IDs in Home Assistant:**
   - Go to Developer Tools → States
   - Search for your devices
   - Copy the entity IDs (e.g., `light.living_room`)

### Option 2: Without Home Assistant

If you don't have Home Assistant, the smart home features will report that they're not configured. You can either:
- Set up Home Assistant (free, powerful, supports 1000+ devices)
- Wait for future updates with direct device control

## Voice Commands

Once configured, you can use these voice commands:

### Lights & Switches
- "Turn on the living room light"
- "Turn off the bedroom light"
- "Switch on the kitchen light"

### Brightness Control
- "Set living room light to 50 percent"
- "Dim the bedroom light to 20 percent"
- "Brighten the kitchen light to 100 percent"

### Thermostat
- "Set the thermostat to 72 degrees"
- "Set temperature to 68"
- "Make it warmer" (AI will interpret and set appropriate temp)

### Scenes/Routines
- "Activate movie time"
- "Run good morning scene"
- "Start bedtime routine"

### Status Check
- "Is the living room light on?"
- "What's the temperature?"
- "Check the thermostat status"

## Troubleshooting

### "Smart home system not configured"
- Check that HOME_ASSISTANT_URL and HOME_ASSISTANT_TOKEN are set
- Verify the environment variables: `echo $HOME_ASSISTANT_URL`
- Make sure Home Assistant is accessible: `curl $HOME_ASSISTANT_URL`

### "Failed to turn on device"
- Check that the entity ID is correct in config.json
- Verify the device exists in Home Assistant
- Check Home Assistant logs for errors
- Test the API manually:
  ```bash
  curl -X POST \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"entity_id": "light.living_room"}' \
    http://YOUR_HA_IP:8123/api/services/homeassistant/turn_on
  ```

### Connection timeout
- Ensure Raspberry Pi can reach Home Assistant on the network
- Check firewall settings
- Verify the URL and port (default is 8123)

## Security Notes

- Keep your access token secure - it has full control of your smart home!
- Use HTTPS if Home Assistant is exposed to the internet
- Consider using a dedicated user/token for the smart glasses
- Regularly rotate your access tokens

## Advanced Configuration

### Adding Devices Dynamically
You can add devices through voice (future feature) or by editing the config file.

### Multiple Home Assistant Instances
Currently supports one instance. Edit the config file to switch between instances.

### Custom Scenes
Create scenes in Home Assistant, then add them to the config file for voice control.

## Example Home Assistant Setup

If you're new to Home Assistant, here's a quick start:

1. Install Home Assistant OS on a Raspberry Pi 4 (or run in Docker)
2. Add your smart devices (Philips Hue, TP-Link, etc.)
3. Create some scenes for common routines
4. Generate access token for smart glasses
5. Start controlling everything with your voice!

## Support

For issues or questions:
- Home Assistant: https://www.home-assistant.io/docs/
- Smart Glasses Issues: Create an issue in your GitHub repo
