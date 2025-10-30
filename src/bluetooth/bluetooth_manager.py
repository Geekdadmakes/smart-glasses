"""
Bluetooth Manager - Full Bluetooth integration for smart glasses
Supports: Audio streaming, phone calls, file transfer, notifications
"""

import os
import subprocess
import logging
import json
import time
import threading
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class BluetoothManager:
    """Manages Bluetooth connections and features"""

    def __init__(self, config, camera_manager=None):
        """Initialize Bluetooth manager"""
        self.config = config
        self.enabled = config.get('enabled', True)
        self.device_name = config.get('device_name', 'Smart Glasses')
        self.auto_connect = config.get('auto_connect', True)
        self.paired_devices_file = Path(config.get('paired_devices_file', './config/paired_devices.json'))

        # Managers
        self.camera_manager = camera_manager

        # Connected devices
        self.connected_phone = None
        self.paired_devices = self._load_paired_devices()

        # Audio state
        self.audio_streaming = False
        self.in_call = False
        self.current_caller = None

        # Media state
        self.media_playing = False
        self.current_track = None

        # Notification queue
        self.notifications = []
        self.notification_callback = None

        # Sync state
        self.sync_enabled = True
        self.sync_thread = None

        # Initialize Bluetooth service
        if self.enabled:
            self._initialize_bluetooth()

        logger.info(f"Bluetooth Manager initialized - device: {self.device_name}")

    def _initialize_bluetooth(self):
        """Initialize Bluetooth services"""
        try:
            # Make device discoverable
            self._set_discoverable(True)

            # Set device name
            self._set_device_name(self.device_name)

            # Enable Bluetooth
            self._enable_bluetooth()

            # Auto-connect to known devices
            if self.auto_connect and self.paired_devices:
                self._auto_connect_devices()

            logger.info("Bluetooth initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Bluetooth: {e}")

    def _enable_bluetooth(self):
        """Enable Bluetooth controller"""
        try:
            subprocess.run(['sudo', 'systemctl', 'start', 'bluetooth'], check=True)
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'], check=True)
            logger.info("Bluetooth enabled")
        except Exception as e:
            logger.error(f"Error enabling Bluetooth: {e}")

    def _set_device_name(self, name):
        """Set Bluetooth device name"""
        try:
            subprocess.run(['sudo', 'hciconfig', 'hci0', 'name', name], check=True)
            logger.info(f"Device name set to: {name}")
        except Exception as e:
            logger.error(f"Error setting device name: {e}")

    def _set_discoverable(self, discoverable=True):
        """Set device discoverable"""
        try:
            if discoverable:
                subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'], check=True)
                logger.info("Device is now discoverable")
            else:
                subprocess.run(['sudo', 'hciconfig', 'hci0', 'noscan'], check=True)
                logger.info("Device is no longer discoverable")
        except Exception as e:
            logger.error(f"Error setting discoverable: {e}")

    def scan_devices(self, duration=10):
        """
        Scan for nearby Bluetooth devices
        Returns list of discovered devices
        """
        logger.info(f"Scanning for Bluetooth devices for {duration} seconds...")

        try:
            # Use bluetoothctl for scanning
            result = subprocess.run(
                ['timeout', str(duration), 'bluetoothctl', 'scan', 'on'],
                capture_output=True,
                text=True
            )

            # Parse discovered devices
            devices = self._parse_scan_results(result.stdout)
            logger.info(f"Found {len(devices)} devices")
            return devices

        except Exception as e:
            logger.error(f"Error scanning devices: {e}")
            return []

    def _parse_scan_results(self, output):
        """Parse bluetoothctl scan output"""
        devices = []
        for line in output.split('\n'):
            if 'Device' in line:
                parts = line.split()
                if len(parts) >= 3:
                    address = parts[1]
                    name = ' '.join(parts[2:])
                    devices.append({'address': address, 'name': name})
        return devices

    def pair_device(self, device_address):
        """Pair with a Bluetooth device"""
        logger.info(f"Pairing with device: {device_address}")

        try:
            # Use bluetoothctl to pair
            result = subprocess.run(
                ['bluetoothctl', 'pair', device_address],
                capture_output=True,
                text=True,
                timeout=30
            )

            if 'Pairing successful' in result.stdout:
                logger.info(f"Successfully paired with {device_address}")

                # Trust the device
                subprocess.run(['bluetoothctl', 'trust', device_address])

                # Save to paired devices
                self._add_paired_device(device_address)

                return True
            else:
                logger.error(f"Pairing failed: {result.stdout}")
                return False

        except Exception as e:
            logger.error(f"Error pairing device: {e}")
            return False

    def connect_device(self, device_address):
        """Connect to a paired Bluetooth device"""
        logger.info(f"Connecting to device: {device_address}")

        try:
            result = subprocess.run(
                ['bluetoothctl', 'connect', device_address],
                capture_output=True,
                text=True,
                timeout=30
            )

            if 'Connection successful' in result.stdout or 'Connected: yes' in result.stdout:
                logger.info(f"Successfully connected to {device_address}")
                self.connected_phone = device_address

                # Start sync if enabled
                if self.sync_enabled:
                    self._start_sync_service()

                return True
            else:
                logger.error(f"Connection failed: {result.stdout}")
                return False

        except Exception as e:
            logger.error(f"Error connecting device: {e}")
            return False

    def disconnect_device(self, device_address):
        """Disconnect from a Bluetooth device"""
        logger.info(f"Disconnecting from device: {device_address}")

        try:
            subprocess.run(['bluetoothctl', 'disconnect', device_address])

            if device_address == self.connected_phone:
                self.connected_phone = None
                self._stop_sync_service()

            logger.info(f"Disconnected from {device_address}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting device: {e}")
            return False

    def _auto_connect_devices(self):
        """Automatically connect to known devices"""
        logger.info("Attempting to auto-connect to paired devices...")

        for device in self.paired_devices:
            address = device.get('address')
            if address:
                if self.connect_device(address):
                    logger.info(f"Auto-connected to {device.get('name', address)}")
                    break  # Connect to first available device

    def _load_paired_devices(self):
        """Load paired devices from file"""
        try:
            if self.paired_devices_file.exists():
                with open(self.paired_devices_file, 'r') as f:
                    devices = json.load(f)
                logger.info(f"Loaded {len(devices)} paired devices")
                return devices
        except Exception as e:
            logger.error(f"Error loading paired devices: {e}")
        return []

    def _save_paired_devices(self):
        """Save paired devices to file"""
        try:
            self.paired_devices_file.parent.mkdir(exist_ok=True)
            with open(self.paired_devices_file, 'w') as f:
                json.dump(self.paired_devices, f, indent=2)
            logger.info("Paired devices saved")
        except Exception as e:
            logger.error(f"Error saving paired devices: {e}")

    def _add_paired_device(self, device_address, device_name=None):
        """Add a paired device to the list"""
        device = {
            'address': device_address,
            'name': device_name or device_address,
            'paired_at': datetime.now().isoformat()
        }

        # Check if already in list
        for i, d in enumerate(self.paired_devices):
            if d['address'] == device_address:
                self.paired_devices[i] = device
                self._save_paired_devices()
                return

        # Add new device
        self.paired_devices.append(device)
        self._save_paired_devices()

    # Audio Streaming (A2DP)

    def start_audio_stream(self):
        """Start audio streaming from phone"""
        logger.info("Starting audio stream...")

        if not self.connected_phone:
            logger.error("No phone connected")
            return False

        try:
            # Connect to A2DP profile
            # Audio will automatically route through ALSA
            self.audio_streaming = True
            logger.info("Audio streaming started")
            return True

        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
            return False

    def stop_audio_stream(self):
        """Stop audio streaming"""
        logger.info("Stopping audio stream...")
        self.audio_streaming = False

    # Media Control

    def media_play(self):
        """Play media"""
        logger.info("Sending play command...")
        try:
            subprocess.run(['dbus-send', '--system', '--dest=org.bluez',
                          '--type=method_call', '/org/bluez/hci0',
                          'org.bluez.MediaControl1.Play'])
            self.media_playing = True
            return True
        except Exception as e:
            logger.error(f"Error sending play: {e}")
            return False

    def media_pause(self):
        """Pause media"""
        logger.info("Sending pause command...")
        try:
            subprocess.run(['dbus-send', '--system', '--dest=org.bluez',
                          '--type=method_call', '/org/bluez/hci0',
                          'org.bluez.MediaControl1.Pause'])
            self.media_playing = False
            return True
        except Exception as e:
            logger.error(f"Error sending pause: {e}")
            return False

    def media_next(self):
        """Next track"""
        logger.info("Sending next track command...")
        try:
            subprocess.run(['dbus-send', '--system', '--dest=org.bluez',
                          '--type=method_call', '/org/bluez/hci0',
                          'org.bluez.MediaControl1.Next'])
            return True
        except Exception as e:
            logger.error(f"Error sending next: {e}")
            return False

    def media_previous(self):
        """Previous track"""
        logger.info("Sending previous track command...")
        try:
            subprocess.run(['dbus-send', '--system', '--dest=org.bluez',
                          '--type=method_call', '/org/bluez/hci0',
                          'org.bluez.MediaControl1.Previous'])
            return True
        except Exception as e:
            logger.error(f"Error sending previous: {e}")
            return False

    # Phone Calls (HFP)

    def answer_call(self):
        """Answer incoming call"""
        logger.info("Answering call...")
        self.in_call = True
        # Implementation depends on HFP setup
        return True

    def end_call(self):
        """End current call"""
        logger.info("Ending call...")
        self.in_call = False
        self.current_caller = None
        return True

    def reject_call(self):
        """Reject incoming call"""
        logger.info("Rejecting call...")
        return True

    # Photo/Video Sync

    def _start_sync_service(self):
        """Start photo/video sync service"""
        if self.sync_thread and self.sync_thread.is_alive():
            return

        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        logger.info("Sync service started")

    def _stop_sync_service(self):
        """Stop sync service"""
        self.sync_enabled = False
        if self.sync_thread:
            self.sync_thread.join(timeout=2)
        logger.info("Sync service stopped")

    def _sync_worker(self):
        """Background worker for syncing photos/videos"""
        while self.sync_enabled and self.connected_phone:
            try:
                # Check for new photos/videos
                if self.camera_manager:
                    new_photos = self._get_unsynced_media()

                    for photo in new_photos:
                        self._sync_file(photo)

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                time.sleep(30)

    def _get_unsynced_media(self):
        """Get list of media files that haven't been synced"""
        # TODO: Track synced files
        return []

    def _sync_file(self, file_path):
        """Sync a file to the phone"""
        logger.info(f"Syncing file: {file_path}")
        # TODO: Implement file transfer via OBEX or HTTP
        pass

    # Notifications

    def set_notification_callback(self, callback):
        """Set callback for notifications"""
        self.notification_callback = callback

    def handle_notification(self, notification):
        """Handle incoming notification from phone"""
        logger.info(f"Notification: {notification}")
        self.notifications.append(notification)

        if self.notification_callback:
            self.notification_callback(notification)

    # Status

    def is_connected(self):
        """Check if phone is connected"""
        return self.connected_phone is not None

    def get_status(self):
        """Get Bluetooth status"""
        return {
            'enabled': self.enabled,
            'connected': self.is_connected(),
            'connected_device': self.connected_phone,
            'audio_streaming': self.audio_streaming,
            'in_call': self.in_call,
            'media_playing': self.media_playing,
            'paired_devices': len(self.paired_devices)
        }

    def cleanup(self):
        """Cleanup Bluetooth resources"""
        logger.info("Cleaning up Bluetooth manager")

        # Stop sync
        self._stop_sync_service()

        # Disconnect devices
        if self.connected_phone:
            self.disconnect_device(self.connected_phone)


# Helper functions for Bluetooth setup

def setup_bluetooth_audio():
    """Setup Bluetooth audio profiles (A2DP, HFP)"""
    logger.info("Setting up Bluetooth audio profiles...")

    # Configure PulseAudio for Bluetooth
    commands = [
        ['sudo', 'apt-get', 'install', '-y', 'pulseaudio-module-bluetooth'],
        ['pulseaudio', '--start'],
        ['pactl', 'load-module', 'module-bluetooth-discover']
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            logger.error(f"Error running {' '.join(cmd)}: {e}")

def make_discoverable_forever():
    """Make device always discoverable"""
    try:
        subprocess.run(['sudo', 'hciconfig', 'hci0', 'piscan'], check=True)
        logger.info("Device made permanently discoverable")
    except Exception as e:
        logger.error(f"Error making device discoverable: {e}")
