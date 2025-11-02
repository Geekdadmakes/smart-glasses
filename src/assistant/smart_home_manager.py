"""
Smart Home Manager - Control smart home devices, lights, thermostats, scenes
"""

import os
import json
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)


class SmartHomeManager:
    """Manage smart home device control and automation"""

    def __init__(self, config_dir='./smart_home'):
        """Initialize smart home manager"""
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / 'config.json'

        # Load configuration
        self.config = self._load_config()

        # Home Assistant settings
        self.ha_url = self.config.get('home_assistant_url') or os.getenv('HOME_ASSISTANT_URL')
        self.ha_token = self.config.get('home_assistant_token') or os.getenv('HOME_ASSISTANT_TOKEN')

        # Device mappings (friendly names to entity IDs)
        self.devices = self.config.get('devices', {})
        self.scenes = self.config.get('scenes', {})

        # Check if Home Assistant is configured
        self.ha_enabled = bool(self.ha_url and self.ha_token)

        if self.ha_enabled:
            logger.info(f"Smart Home Manager initialized - Home Assistant: {self.ha_url}")
        else:
            logger.info("Smart Home Manager initialized - No Home Assistant configured")

    def _load_config(self):
        """Load smart home configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading smart home config: {e}")

        # Default configuration
        return {
            'home_assistant_url': None,
            'home_assistant_token': None,
            'devices': {
                # Example device mappings
                # 'living room light': 'light.living_room',
                # 'bedroom light': 'light.bedroom',
                # 'thermostat': 'climate.main_thermostat',
            },
            'scenes': {
                # Example scene mappings
                # 'movie time': 'scene.movie_mode',
                # 'good morning': 'scene.morning_routine',
                # 'good night': 'scene.bedtime',
            }
        }

    def _save_config(self):
        """Save smart home configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving smart home config: {e}")

    def _ha_api_call(self, endpoint, method='GET', data=None):
        """Make API call to Home Assistant"""
        if not self.ha_enabled:
            return None

        try:
            url = f"{self.ha_url}/api/{endpoint}"
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json'
            }

            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=5)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=5)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Home Assistant API timeout")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Home Assistant API error: {e}")
            return None

    def _resolve_device_id(self, device_name):
        """Resolve friendly device name to entity ID"""
        device_name_lower = device_name.lower()

        # Direct match
        if device_name_lower in self.devices:
            return self.devices[device_name_lower]

        # Partial match
        for friendly_name, entity_id in self.devices.items():
            if device_name_lower in friendly_name or friendly_name in device_name_lower:
                return entity_id

        # If not in mappings, assume it's already an entity ID
        return device_name

    def turn_on_device(self, device_name):
        """Turn on a device (light, switch, etc.)"""
        if not self.ha_enabled:
            return "Smart home system not configured. Set HOME_ASSISTANT_URL and HOME_ASSISTANT_TOKEN."

        entity_id = self._resolve_device_id(device_name)

        logger.info(f"Turning on device: {device_name} ({entity_id})")

        result = self._ha_api_call(
            'services/homeassistant/turn_on',
            method='POST',
            data={'entity_id': entity_id}
        )

        if result is not None:
            return f"Turned on {device_name}"
        else:
            return f"Failed to turn on {device_name}"

    def turn_off_device(self, device_name):
        """Turn off a device"""
        if not self.ha_enabled:
            return "Smart home system not configured. Set HOME_ASSISTANT_URL and HOME_ASSISTANT_TOKEN."

        entity_id = self._resolve_device_id(device_name)

        logger.info(f"Turning off device: {device_name} ({entity_id})")

        result = self._ha_api_call(
            'services/homeassistant/turn_off',
            method='POST',
            data={'entity_id': entity_id}
        )

        if result is not None:
            return f"Turned off {device_name}"
        else:
            return f"Failed to turn off {device_name}"

    def set_brightness(self, device_name, brightness):
        """Set brightness of a light (0-100)"""
        if not self.ha_enabled:
            return "Smart home system not configured."

        entity_id = self._resolve_device_id(device_name)

        # Convert percentage to 0-255 range
        brightness_value = int((brightness / 100) * 255)

        logger.info(f"Setting brightness: {device_name} to {brightness}%")

        result = self._ha_api_call(
            'services/light/turn_on',
            method='POST',
            data={
                'entity_id': entity_id,
                'brightness': brightness_value
            }
        )

        if result is not None:
            return f"Set {device_name} brightness to {brightness}%"
        else:
            return f"Failed to set brightness for {device_name}"

    def set_temperature(self, device_name, temperature):
        """Set thermostat temperature"""
        if not self.ha_enabled:
            return "Smart home system not configured."

        entity_id = self._resolve_device_id(device_name)

        logger.info(f"Setting temperature: {device_name} to {temperature}°")

        result = self._ha_api_call(
            'services/climate/set_temperature',
            method='POST',
            data={
                'entity_id': entity_id,
                'temperature': temperature
            }
        )

        if result is not None:
            return f"Set {device_name} to {temperature} degrees"
        else:
            return f"Failed to set temperature for {device_name}"

    def activate_scene(self, scene_name):
        """Activate a scene"""
        if not self.ha_enabled:
            return "Smart home system not configured."

        scene_name_lower = scene_name.lower()

        # Resolve scene name to entity ID
        if scene_name_lower in self.scenes:
            entity_id = self.scenes[scene_name_lower]
        else:
            # Try partial match
            entity_id = None
            for friendly_name, scene_id in self.scenes.items():
                if scene_name_lower in friendly_name or friendly_name in scene_name_lower:
                    entity_id = scene_id
                    break

            if not entity_id:
                # Assume it's already an entity ID or construct it
                entity_id = f"scene.{scene_name.lower().replace(' ', '_')}"

        logger.info(f"Activating scene: {scene_name} ({entity_id})")

        result = self._ha_api_call(
            'services/scene/turn_on',
            method='POST',
            data={'entity_id': entity_id}
        )

        if result is not None:
            return f"Activated {scene_name} scene"
        else:
            return f"Failed to activate {scene_name} scene"

    def get_device_state(self, device_name):
        """Get the current state of a device"""
        if not self.ha_enabled:
            return "Smart home system not configured."

        entity_id = self._resolve_device_id(device_name)

        logger.info(f"Getting state for: {device_name} ({entity_id})")

        result = self._ha_api_call(f'states/{entity_id}')

        if result:
            state = result.get('state', 'unknown')
            attributes = result.get('attributes', {})

            # Build friendly response
            response = f"{device_name} is {state}"

            # Add relevant attributes
            if 'temperature' in attributes:
                response += f", temperature: {attributes['temperature']}°"
            if 'brightness' in attributes:
                brightness_pct = int((attributes['brightness'] / 255) * 100)
                response += f", brightness: {brightness_pct}%"
            if 'current_temperature' in attributes:
                response += f", current temp: {attributes['current_temperature']}°"

            return response
        else:
            return f"Could not get status for {device_name}"

    def list_devices(self):
        """List all configured devices"""
        if not self.devices:
            return "No devices configured. Add devices to smart_home/config.json"

        device_list = "Configured devices:\n"
        for friendly_name, entity_id in self.devices.items():
            device_list += f"• {friendly_name} ({entity_id})\n"

        return device_list.strip()

    def list_scenes(self):
        """List all configured scenes"""
        if not self.scenes:
            return "No scenes configured. Add scenes to smart_home/config.json"

        scene_list = "Configured scenes:\n"
        for friendly_name, entity_id in self.scenes.items():
            scene_list += f"• {friendly_name} ({entity_id})\n"

        return scene_list.strip()

    def add_device(self, friendly_name, entity_id):
        """Add a device mapping"""
        self.devices[friendly_name.lower()] = entity_id
        self.config['devices'] = self.devices
        self._save_config()
        return f"Added device: {friendly_name} -> {entity_id}"

    def add_scene(self, friendly_name, entity_id):
        """Add a scene mapping"""
        self.scenes[friendly_name.lower()] = entity_id
        self.config['scenes'] = self.scenes
        self._save_config()
        return f"Added scene: {friendly_name} -> {entity_id}"
