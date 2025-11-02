"""
BLE GATT Server for Smart Glasses
Handles Bluetooth LE communication with iOS companion app
Uses BlueZ D-Bus API on Linux (Raspberry Pi)
"""

import logging
import json
import secrets
import threading
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

# Try to import BLE server library
try:
    # bless is a BLE server library for Python
    from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions
    BLESS_AVAILABLE = True
except ImportError:
    BLESS_AVAILABLE = False
    logger.warning("bless library not available. Install with: pip install bless")

from .ble_services import (
    BLEServices, BLECharacteristics, ALL_SERVICES,
    CharacteristicProperties
)


class BLEGATTServer:
    """
    Bluetooth LE GATT Server for Smart Glasses
    Provides services for pairing, settings, and data sync with iOS app
    """

    def __init__(self, managers=None):
        """
        Initialize BLE GATT server

        Args:
            managers: Dictionary of manager instances (camera, ai_assistant, etc.)
        """
        self.managers = managers or {}
        self.server = None
        self.is_running = False
        self.paired_devices = set()

        # Configuration
        self.config = self._load_config()
        self.device_name = "Smart Glasses"

        # API key for WiFi authentication
        self.api_key = self._load_or_generate_api_key()

        # Pairing code
        self.pairing_code = None
        self.pairing_in_progress = False

        # Characteristic values (cache)
        self.characteristic_values = {}

        # Notification subscribers
        self.subscribers = {}

        logger.info("BLE GATT Server initialized")

    def _load_config(self):
        """Load configuration from yaml file"""
        try:
            config_path = Path('./config/config.yaml')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        return {}

    def _load_or_generate_api_key(self):
        """Load existing API key or generate new one"""
        api_key_file = Path('./config/api_key.txt')

        try:
            if api_key_file.exists():
                with open(api_key_file, 'r') as f:
                    api_key = f.read().strip()
                    logger.info("Loaded existing API key")
                    return api_key
        except Exception as e:
            logger.error(f"Error loading API key: {e}")

        # Generate new API key
        api_key = secrets.token_urlsafe(32)
        try:
            api_key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(api_key_file, 'w') as f:
                f.write(api_key)
            logger.info("Generated new API key")
        except Exception as e:
            logger.error(f"Error saving API key: {e}")

        return api_key

    def _generate_pairing_code(self):
        """Generate 6-digit pairing code"""
        import random
        self.pairing_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        logger.info(f"Generated pairing code: {self.pairing_code}")

        # Speak the pairing code through TTS
        if 'audio_manager' in self.managers:
            audio_manager = self.managers['audio_manager']
            code_spoken = ' '.join(self.pairing_code)
            audio_manager.speak(f"Pairing code: {code_spoken}", blocking=True)

        return self.pairing_code

    async def start(self):
        """Start the BLE GATT server"""
        if not BLESS_AVAILABLE:
            logger.error("Cannot start BLE server: bless library not installed")
            logger.error("Install with: pip install bless")
            return False

        try:
            logger.info("Starting BLE GATT server...")

            # Create server
            self.server = BlessServer(name=self.device_name)

            # Add all services
            await self._setup_services()

            # Start advertising
            await self.server.start()

            self.is_running = True
            logger.info(f"BLE GATT server started - Device name: {self.device_name}")
            logger.info(f"iOS app can now discover and pair with this device")

            return True

        except Exception as e:
            logger.error(f"Error starting BLE server: {e}", exc_info=True)
            return False

    async def _setup_services(self):
        """Setup all GATT services and characteristics"""

        # Device Information Service
        await self._setup_device_info_service()

        # Battery Service
        await self._setup_battery_service()

        # Authentication Service
        await self._setup_authentication_service()

        # Settings Service
        await self._setup_settings_service()

        # Quick Actions Service
        await self._setup_quick_actions_service()

        # Data Sync Service
        await self._setup_data_sync_service()

        # WiFi Configuration Service
        await self._setup_wifi_config_service()

    async def _setup_device_info_service(self):
        """Setup Device Information Service"""
        logger.info("Setting up Device Information Service")

        # Add service
        await self.server.add_new_service(BLEServices.DEVICE_INFO)

        # Device Name
        await self.server.add_new_characteristic(
            BLEServices.DEVICE_INFO,
            BLECharacteristics.DEVICE_NAME,
            GATTCharacteristicProperties.read,
            self.device_name.encode(),
            GATTAttributePermissions.readable
        )

        # Manufacturer
        await self.server.add_new_characteristic(
            BLEServices.DEVICE_INFO,
            BLECharacteristics.MANUFACTURER,
            GATTCharacteristicProperties.read,
            b"DIY Smart Glasses",
            GATTAttributePermissions.readable
        )

        # Model Number
        await self.server.add_new_characteristic(
            BLEServices.DEVICE_INFO,
            BLECharacteristics.MODEL_NUMBER,
            GATTCharacteristicProperties.read,
            b"Pi Zero W v1.0",
            GATTAttributePermissions.readable
        )

        # Firmware Version
        await self.server.add_new_characteristic(
            BLEServices.DEVICE_INFO,
            BLECharacteristics.FIRMWARE_VERSION,
            GATTCharacteristicProperties.read,
            b"1.0.0",
            GATTAttributePermissions.readable
        )

    async def _setup_battery_service(self):
        """Setup Battery Service"""
        logger.info("Setting up Battery Service")

        await self.server.add_new_service(BLEServices.BATTERY_SERVICE)

        # Battery level (0-100%)
        battery_level = self._get_battery_level()

        await self.server.add_new_characteristic(
            BLEServices.BATTERY_SERVICE,
            BLECharacteristics.BATTERY_LEVEL,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            bytes([battery_level]),
            GATTAttributePermissions.readable
        )

    async def _setup_authentication_service(self):
        """Setup Authentication Service for pairing"""
        logger.info("Setting up Authentication Service")

        await self.server.add_new_service(BLEServices.AUTHENTICATION)

        # API Key (read-only)
        await self.server.add_new_characteristic(
            BLEServices.AUTHENTICATION,
            BLECharacteristics.API_KEY,
            GATTCharacteristicProperties.read,
            self.api_key.encode(),
            GATTAttributePermissions.readable
        )

        # Pairing Code (read + notify)
        pairing_code = self._generate_pairing_code()
        await self.server.add_new_characteristic(
            BLEServices.AUTHENTICATION,
            BLECharacteristics.PAIRING_CODE,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            pairing_code.encode(),
            GATTAttributePermissions.readable
        )

        # Pairing Status (read + write)
        def pairing_status_write_callback(value):
            # Value: 0=unpaired, 1=pairing, 2=paired
            status = int.from_bytes(value, byteorder='little')
            logger.info(f"Pairing status updated: {status}")
            if status == 2:
                logger.info("Device successfully paired!")
                self.pairing_in_progress = False

        await self.server.add_new_characteristic(
            BLEServices.AUTHENTICATION,
            BLECharacteristics.PAIRING_STATUS,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
            bytes([0]),  # 0 = unpaired
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
            write_callback=pairing_status_write_callback
        )

    async def _setup_settings_service(self):
        """Setup Settings Service"""
        logger.info("Setting up Settings Service")

        await self.server.add_new_service(BLEServices.SETTINGS)

        # Personality
        current_personality = self.config.get('assistant', {}).get('personality', 'friendly')

        def personality_write_callback(value):
            personality = value.decode('utf-8')
            logger.info(f"Personality changed to: {personality}")
            self._update_config('assistant', 'personality', personality)

        await self.server.add_new_characteristic(
            BLEServices.SETTINGS,
            BLECharacteristics.PERSONALITY,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
            current_personality.encode(),
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
            write_callback=personality_write_callback
        )

        # Assistant Name
        current_name = self.config.get('assistant', {}).get('name', 'Jarvis')

        def name_write_callback(value):
            name = value.decode('utf-8')
            logger.info(f"Assistant name changed to: {name}")
            self._update_config('assistant', 'name', name)

        await self.server.add_new_characteristic(
            BLEServices.SETTINGS,
            BLECharacteristics.ASSISTANT_NAME,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
            current_name.encode(),
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
            write_callback=name_write_callback
        )

        # Wake Word Config (JSON)
        wake_word_config = {
            'keyword': self.config.get('wake_word', {}).get('keyword', 'hey glasses'),
            'sensitivity': self.config.get('wake_word', {}).get('sensitivity', 0.5)
        }

        def wake_word_write_callback(value):
            config_data = json.loads(value.decode('utf-8'))
            logger.info(f"Wake word config changed: {config_data}")
            self._update_config('wake_word', 'keyword', config_data.get('keyword'))
            self._update_config('wake_word', 'sensitivity', config_data.get('sensitivity'))

        await self.server.add_new_characteristic(
            BLEServices.SETTINGS,
            BLECharacteristics.WAKE_WORD_CONFIG,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
            json.dumps(wake_word_config).encode(),
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
            write_callback=wake_word_write_callback
        )

        # Voice Settings (JSON)
        voice_settings = {
            'engine': self.config.get('tts', {}).get('engine', 'gtts'),
            'rate': self.config.get('tts', {}).get('rate', 150),
            'volume': self.config.get('tts', {}).get('volume', 0.6)
        }

        def voice_write_callback(value):
            settings_data = json.loads(value.decode('utf-8'))
            logger.info(f"Voice settings changed: {settings_data}")
            self._update_config('tts', 'engine', settings_data.get('engine'))
            self._update_config('tts', 'rate', settings_data.get('rate'))
            self._update_config('tts', 'volume', settings_data.get('volume'))

        await self.server.add_new_characteristic(
            BLEServices.SETTINGS,
            BLECharacteristics.VOICE_SETTINGS,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
            json.dumps(voice_settings).encode(),
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
            write_callback=voice_write_callback
        )

        # Status Mode (read + notify)
        current_mode = "active"  # Default
        await self.server.add_new_characteristic(
            BLEServices.SETTINGS,
            BLECharacteristics.STATUS_MODE,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            current_mode.encode(),
            GATTAttributePermissions.readable
        )

    async def _setup_quick_actions_service(self):
        """Setup Quick Actions Service"""
        logger.info("Setting up Quick Actions Service")

        await self.server.add_new_service(BLEServices.QUICK_ACTIONS)

        # Camera Control
        def camera_control_callback(value):
            command = value.decode('utf-8')
            logger.info(f"Camera command received: {command}")
            response = self._handle_camera_command(command)
            # Update response characteristic
            self._notify_characteristic(BLECharacteristics.ACTION_RESPONSE, response.encode())

        await self.server.add_new_characteristic(
            BLEServices.QUICK_ACTIONS,
            BLECharacteristics.CAMERA_CONTROL,
            GATTCharacteristicProperties.write,
            b"",
            GATTAttributePermissions.writeable,
            write_callback=camera_control_callback
        )

        # System Control
        def system_control_callback(value):
            command = value.decode('utf-8')
            logger.info(f"System command received: {command}")
            response = self._handle_system_command(command)
            # Update response characteristic
            self._notify_characteristic(BLECharacteristics.ACTION_RESPONSE, response.encode())

        await self.server.add_new_characteristic(
            BLEServices.QUICK_ACTIONS,
            BLECharacteristics.SYSTEM_CONTROL,
            GATTCharacteristicProperties.write,
            b"",
            GATTAttributePermissions.writeable,
            write_callback=system_control_callback
        )

        # Action Response (read + notify)
        await self.server.add_new_characteristic(
            BLEServices.QUICK_ACTIONS,
            BLECharacteristics.ACTION_RESPONSE,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            b"{}",
            GATTAttributePermissions.readable
        )

    async def _setup_data_sync_service(self):
        """Setup Data Sync Service"""
        logger.info("Setting up Data Sync Service")

        await self.server.add_new_service(BLEServices.DATA_SYNC)

        # Notes Data
        notes = self._get_notes()
        await self.server.add_new_characteristic(
            BLEServices.DATA_SYNC,
            BLECharacteristics.NOTES_DATA,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write | GATTCharacteristicProperties.notify,
            json.dumps(notes[:5]).encode(),  # Limit to 5 most recent
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        )

        # Todos Data
        todos = self._get_todos()
        await self.server.add_new_characteristic(
            BLEServices.DATA_SYNC,
            BLECharacteristics.TODOS_DATA,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write | GATTCharacteristicProperties.notify,
            json.dumps(todos[:5]).encode(),  # Limit to 5 most recent
            GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        )

        # Status Message
        await self.server.add_new_characteristic(
            BLEServices.DATA_SYNC,
            BLECharacteristics.STATUS_MESSAGE,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            b"Ready",
            GATTAttributePermissions.readable
        )

    async def _setup_wifi_config_service(self):
        """Setup WiFi Configuration Service"""
        logger.info("Setting up WiFi Configuration Service")

        await self.server.add_new_service(BLEServices.WIFI_CONFIG)

        # WiFi SSID (write-only)
        def wifi_ssid_callback(value):
            ssid = value.decode('utf-8')
            logger.info(f"WiFi SSID received: {ssid}")
            self.wifi_ssid = ssid

        await self.server.add_new_characteristic(
            BLEServices.WIFI_CONFIG,
            BLECharacteristics.WIFI_SSID,
            GATTCharacteristicProperties.write,
            b"",
            GATTAttributePermissions.writeable,
            write_callback=wifi_ssid_callback
        )

        # WiFi Password (write-only)
        def wifi_password_callback(value):
            password = value.decode('utf-8')
            logger.info("WiFi password received")
            self.wifi_password = password
            # Attempt to connect
            self._connect_to_wifi(self.wifi_ssid, password)

        await self.server.add_new_characteristic(
            BLEServices.WIFI_CONFIG,
            BLECharacteristics.WIFI_PASSWORD,
            GATTCharacteristicProperties.write,
            b"",
            GATTAttributePermissions.writeable,
            write_callback=wifi_password_callback
        )

        # WiFi Status (read + notify)
        await self.server.add_new_characteristic(
            BLEServices.WIFI_CONFIG,
            BLECharacteristics.WIFI_STATUS,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            b"disconnected",
            GATTAttributePermissions.readable
        )

        # Network Info (read-only)
        network_info = self._get_network_info()
        await self.server.add_new_characteristic(
            BLEServices.WIFI_CONFIG,
            BLECharacteristics.NETWORK_INFO,
            GATTCharacteristicProperties.read,
            json.dumps(network_info).encode(),
            GATTAttributePermissions.readable
        )

    def _update_config(self, section, key, value):
        """Update configuration file"""
        try:
            config_path = Path('./config/config.yaml')

            # Update in-memory config
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value

            # Save to file
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f)

            logger.info(f"Config updated: {section}.{key} = {value}")

        except Exception as e:
            logger.error(f"Error updating config: {e}")

    def _get_battery_level(self):
        """Get battery level (0-100)"""
        # TODO: Implement actual battery reading
        # For now, return 85% as placeholder
        return 85

    def _get_notes(self):
        """Get notes from productivity manager"""
        if 'productivity_manager' in self.managers:
            try:
                return self.managers['productivity_manager'].get_notes()
            except:
                pass
        return []

    def _get_todos(self):
        """Get todos from productivity manager"""
        if 'productivity_manager' in self.managers:
            try:
                return self.managers['productivity_manager'].get_todos()
            except:
                pass
        return []

    def _handle_camera_command(self, command):
        """Handle camera control commands"""
        try:
            if command == "photo":
                if 'camera_manager' in self.managers:
                    photo_path = self.managers['camera_manager'].take_photo()
                    return json.dumps({"success": True, "path": str(photo_path)})

            elif command.startswith("video:"):
                duration = int(command.split(":")[1])
                if 'camera_manager' in self.managers:
                    video_path = self.managers['camera_manager'].record_video(duration=duration)
                    return json.dumps({"success": True, "path": str(video_path)})

            return json.dumps({"success": False, "error": "Unknown command"})

        except Exception as e:
            logger.error(f"Error handling camera command: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def _handle_system_command(self, command):
        """Handle system control commands"""
        try:
            if command == "sleep":
                # TODO: Trigger sleep mode
                logger.info("Sleep command received")
                return json.dumps({"success": True, "message": "Going to sleep"})

            elif command == "wake":
                # TODO: Wake up system
                logger.info("Wake command received")
                return json.dumps({"success": True, "message": "Waking up"})

            elif command == "restart":
                # TODO: Restart application
                logger.info("Restart command received")
                return json.dumps({"success": True, "message": "Restarting"})

            return json.dumps({"success": False, "error": "Unknown command"})

        except Exception as e:
            logger.error(f"Error handling system command: {e}")
            return json.dumps({"success": False, "error": str(e)})

    def _connect_to_wifi(self, ssid, password):
        """Connect to WiFi network"""
        try:
            logger.info(f"Attempting to connect to WiFi: {ssid}")
            # TODO: Implement WiFi connection using nmcli or wpa_supplicant
            # This is a placeholder
            self._notify_characteristic(BLECharacteristics.WIFI_STATUS, b"connecting")

            # Simulate connection
            import time
            time.sleep(2)

            # Update status
            self._notify_characteristic(BLECharacteristics.WIFI_STATUS, b"connected")

            # Update network info
            network_info = self._get_network_info()
            self._update_characteristic(BLECharacteristics.NETWORK_INFO, json.dumps(network_info).encode())

        except Exception as e:
            logger.error(f"Error connecting to WiFi: {e}")
            self._notify_characteristic(BLECharacteristics.WIFI_STATUS, b"failed")

    def _get_network_info(self):
        """Get current network information"""
        try:
            import socket
            import subprocess

            # Get IP address
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            ip = result.stdout.strip().split()[0] if result.stdout else "0.0.0.0"

            return {
                "ip": ip,
                "subnet": "255.255.255.0",
                "gateway": "192.168.1.1"
            }
        except:
            return {"ip": "0.0.0.0", "subnet": "", "gateway": ""}

    def _notify_characteristic(self, characteristic_uuid, value):
        """Send notification for a characteristic"""
        try:
            if self.server:
                self.server.update_value(BLEServices.QUICK_ACTIONS, characteristic_uuid, value)
        except Exception as e:
            logger.error(f"Error notifying characteristic: {e}")

    def _update_characteristic(self, characteristic_uuid, value):
        """Update a characteristic value"""
        try:
            if self.server:
                # Update the value (implementation depends on the library)
                pass
        except Exception as e:
            logger.error(f"Error updating characteristic: {e}")

    async def stop(self):
        """Stop the BLE GATT server"""
        try:
            if self.server:
                await self.server.stop()
            self.is_running = False
            logger.info("BLE GATT server stopped")
        except Exception as e:
            logger.error(f"Error stopping BLE server: {e}")

    def run_in_thread(self):
        """Run BLE server in a background thread"""
        import asyncio

        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start())
            # Keep running
            loop.run_forever()

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
        logger.info("BLE server started in background thread")
        return thread
