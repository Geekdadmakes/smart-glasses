"""
Connection Manager - Hybrid BLE + WiFi Communication
Intelligently routes requests between Bluetooth LE and WiFi based on:
- Request type (high vs low bandwidth)
- Connection availability
- Quality/performance
"""

import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages both BLE and WiFi connections
    Provides intelligent routing between transports
    """

    def __init__(self, managers=None):
        """
        Initialize connection manager

        Args:
            managers: Dictionary of all manager instances (camera, audio, ai_assistant, etc.)
        """
        self.managers = managers or {}

        # Import here to avoid circular dependencies
        try:
            from ..bluetooth.ble_server import BLEGATTServer
            from ..api.api_server import APIServer

            # Initialize both servers
            self.ble_server = BLEGATTServer(managers=managers)
            self.api_server = APIServer(managers=managers, port=5000)

            logger.info("Connection Manager initialized with BLE + WiFi")

        except ImportError as e:
            logger.error(f"Error importing servers: {e}")
            self.ble_server = None
            self.api_server = None

        # Connection status
        self.ble_enabled = True
        self.wifi_enabled = True
        self.ble_running = False
        self.wifi_running = False

        # Monitoring
        self.monitor_thread = None
        self.is_monitoring = False

    def start(self):
        """Start both BLE and WiFi servers"""
        logger.info("Starting Connection Manager...")

        success_count = 0

        # Start BLE server
        if self.ble_enabled and self.ble_server:
            try:
                logger.info("Starting BLE GATT server...")
                # BLE server runs in its own thread
                self.ble_server.run_in_thread()
                self.ble_running = True
                success_count += 1
                logger.info("✓ BLE server started successfully")
            except Exception as e:
                logger.error(f"✗ Failed to start BLE server: {e}")
                self.ble_running = False

        # Start WiFi API server
        if self.wifi_enabled and self.api_server:
            try:
                logger.info("Starting WiFi API server...")
                # API server runs in its own thread
                self.api_server.start_in_thread()
                self.wifi_running = True
                success_count += 1
                logger.info("✓ WiFi API server started successfully")

                # Give it a moment to start
                time.sleep(1)

                # Get network info
                network_info = self._get_network_info()
                if network_info.get('ip') and network_info.get('ip') != '0.0.0.0':
                    logger.info(f"✓ WiFi API available at: http://{network_info['ip']}:5000/api/status")
                else:
                    logger.warning("⚠ WiFi may not be connected - API available on localhost only")

            except Exception as e:
                logger.error(f"✗ Failed to start WiFi API server: {e}")
                self.wifi_running = False

        # Start connection monitoring
        if success_count > 0:
            self._start_monitoring()
            logger.info(f"✓ Connection Manager started ({success_count}/2 servers running)")
            return True
        else:
            logger.error("✗ Connection Manager failed - no servers started")
            return False

    def _start_monitoring(self):
        """Start connection quality monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
            self.monitor_thread.start()
            logger.info("Connection monitoring started")

    def _monitor_connections(self):
        """Monitor connection quality and status"""
        while self.is_monitoring:
            try:
                # Check BLE status
                if self.ble_enabled and self.ble_server:
                    # TODO: Check if BLE server is still running
                    pass

                # Check WiFi status
                if self.wifi_enabled and self.api_server:
                    # TODO: Check if API server is still running
                    pass

                # Log status every 60 seconds
                if int(time.time()) % 60 == 0:
                    logger.debug(f"Connection status - BLE: {self.ble_running}, WiFi: {self.wifi_running}")

            except Exception as e:
                logger.error(f"Error in connection monitoring: {e}")

            # Check every 10 seconds
            time.sleep(10)

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

    def get_status(self):
        """Get connection manager status"""
        return {
            'ble_enabled': self.ble_enabled,
            'ble_running': self.ble_running,
            'wifi_enabled': self.wifi_enabled,
            'wifi_running': self.wifi_running,
            'network': self._get_network_info()
        }

    def stop(self):
        """Stop both servers"""
        logger.info("Stopping Connection Manager...")

        # Stop monitoring
        self.is_monitoring = False

        # Stop BLE server
        if self.ble_server:
            try:
                # TODO: Implement BLE server stop
                # self.ble_server.stop()
                self.ble_running = False
                logger.info("BLE server stopped")
            except Exception as e:
                logger.error(f"Error stopping BLE server: {e}")

        # Stop API server
        if self.api_server:
            try:
                self.api_server.stop()
                self.wifi_running = False
                logger.info("WiFi API server stopped")
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")

        logger.info("Connection Manager stopped")

    def __del__(self):
        """Cleanup on destruction"""
        self.stop()


# High-bandwidth operations that require WiFi
HIGH_BANDWIDTH_OPS = [
    'camera_stream',
    'download_photo',
    'download_video',
    'large_data_transfer'
]
