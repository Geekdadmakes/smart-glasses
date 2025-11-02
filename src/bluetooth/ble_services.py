"""
BLE GATT Services and Characteristics Definitions
Defines all services, characteristics, and UUIDs for smart glasses BLE communication
"""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class BLEServices:
    """GATT Service UUIDs"""
    # Custom base UUID: 6E400000-B5A3-F393-E0A9-E50E24DCCA9E
    DEVICE_INFO = "0000180a-0000-1000-8000-00805f9b34fb"  # Standard Device Info
    BATTERY_SERVICE = "0000180f-0000-1000-8000-00805f9b34fb"  # Standard Battery

    # Custom services
    AUTHENTICATION = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    SETTINGS = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
    QUICK_ACTIONS = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
    DATA_SYNC = "6E400004-B5A3-F393-E0A9-E50E24DCCA9E"
    WIFI_CONFIG = "6E400005-B5A3-F393-E0A9-E50E24DCCA9E"


class BLECharacteristics:
    """GATT Characteristic UUIDs"""

    # Device Information Service (standard)
    DEVICE_NAME = "00002a00-0000-1000-8000-00805f9b34fb"
    MANUFACTURER = "00002a29-0000-1000-8000-00805f9b34fb"
    MODEL_NUMBER = "00002a24-0000-1000-8000-00805f9b34fb"
    FIRMWARE_VERSION = "00002a26-0000-1000-8000-00805f9b34fb"

    # Battery Service (standard)
    BATTERY_LEVEL = "00002a19-0000-1000-8000-00805f9b34fb"

    # Authentication Service
    API_KEY = "6E400101-B5A3-F393-E0A9-E50E24DCCA9E"
    PAIRING_CODE = "6E400102-B5A3-F393-E0A9-E50E24DCCA9E"
    PAIRING_STATUS = "6E400103-B5A3-F393-E0A9-E50E24DCCA9E"

    # Settings Service
    PERSONALITY = "6E400201-B5A3-F393-E0A9-E50E24DCCA9E"
    ASSISTANT_NAME = "6E400202-B5A3-F393-E0A9-E50E24DCCA9E"
    WAKE_WORD_CONFIG = "6E400203-B5A3-F393-E0A9-E50E24DCCA9E"
    VOICE_SETTINGS = "6E400204-B5A3-F393-E0A9-E50E24DCCA9E"
    STATUS_MODE = "6E400205-B5A3-F393-E0A9-E50E24DCCA9E"  # SLEEP/ACTIVE

    # Quick Actions Service
    CAMERA_CONTROL = "6E400301-B5A3-F393-E0A9-E50E24DCCA9E"
    SYSTEM_CONTROL = "6E400302-B5A3-F393-E0A9-E50E24DCCA9E"
    ACTION_RESPONSE = "6E400303-B5A3-F393-E0A9-E50E24DCCA9E"

    # Data Sync Service
    NOTES_DATA = "6E400401-B5A3-F393-E0A9-E50E24DCCA9E"
    TODOS_DATA = "6E400402-B5A3-F393-E0A9-E50E24DCCA9E"
    STATUS_MESSAGE = "6E400403-B5A3-F393-E0A9-E50E24DCCA9E"

    # WiFi Configuration Service
    WIFI_SSID = "6E400501-B5A3-F393-E0A9-E50E24DCCA9E"
    WIFI_PASSWORD = "6E400502-B5A3-F393-E0A9-E50E24DCCA9E"
    WIFI_STATUS = "6E400503-B5A3-F393-E0A9-E50E24DCCA9E"
    NETWORK_INFO = "6E400504-B5A3-F393-E0A9-E50E24DCCA9E"


class CharacteristicProperties(Enum):
    """BLE Characteristic property flags"""
    READ = 0x02
    WRITE_WITHOUT_RESPONSE = 0x04
    WRITE = 0x08
    NOTIFY = 0x10
    INDICATE = 0x20


class ServiceDefinition:
    """Helper class to define a GATT service"""
    def __init__(self, uuid, characteristics):
        self.uuid = uuid
        self.characteristics = characteristics


class CharacteristicDefinition:
    """Helper class to define a GATT characteristic"""
    def __init__(self, uuid, properties, description="", max_length=512):
        self.uuid = uuid
        self.properties = properties
        self.description = description
        self.max_length = max_length
        self.value = None


# Service Definitions with their characteristics
DEVICE_INFO_SERVICE = ServiceDefinition(
    uuid=BLEServices.DEVICE_INFO,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.DEVICE_NAME,
            CharacteristicProperties.READ,
            "Device name"
        ),
        CharacteristicDefinition(
            BLECharacteristics.MANUFACTURER,
            CharacteristicProperties.READ,
            "Manufacturer name"
        ),
        CharacteristicDefinition(
            BLECharacteristics.MODEL_NUMBER,
            CharacteristicProperties.READ,
            "Model number"
        ),
        CharacteristicDefinition(
            BLECharacteristics.FIRMWARE_VERSION,
            CharacteristicProperties.READ,
            "Firmware version"
        ),
    ]
)

BATTERY_SERVICE_DEF = ServiceDefinition(
    uuid=BLEServices.BATTERY_SERVICE,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.BATTERY_LEVEL,
            CharacteristicProperties.READ | CharacteristicProperties.NOTIFY,
            "Battery level (0-100%)"
        ),
    ]
)

AUTHENTICATION_SERVICE = ServiceDefinition(
    uuid=BLEServices.AUTHENTICATION,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.API_KEY,
            CharacteristicProperties.READ,
            "API key for WiFi connection"
        ),
        CharacteristicDefinition(
            BLECharacteristics.PAIRING_CODE,
            CharacteristicProperties.READ | CharacteristicProperties.NOTIFY,
            "6-digit pairing code"
        ),
        CharacteristicDefinition(
            BLECharacteristics.PAIRING_STATUS,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE,
            "Pairing status: 0=unpaired, 1=pairing, 2=paired"
        ),
    ]
)

SETTINGS_SERVICE = ServiceDefinition(
    uuid=BLEServices.SETTINGS,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.PERSONALITY,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE,
            "AI personality: friendly, professional, witty, jarvis, casual"
        ),
        CharacteristicDefinition(
            BLECharacteristics.ASSISTANT_NAME,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE,
            "Assistant name (e.g., Jarvis)"
        ),
        CharacteristicDefinition(
            BLECharacteristics.WAKE_WORD_CONFIG,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE,
            "JSON: {keyword, sensitivity}"
        ),
        CharacteristicDefinition(
            BLECharacteristics.VOICE_SETTINGS,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE,
            "JSON: {engine, rate, volume}"
        ),
        CharacteristicDefinition(
            BLECharacteristics.STATUS_MODE,
            CharacteristicProperties.READ | CharacteristicProperties.NOTIFY,
            "Current mode: sleep or active"
        ),
    ]
)

QUICK_ACTIONS_SERVICE = ServiceDefinition(
    uuid=BLEServices.QUICK_ACTIONS,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.CAMERA_CONTROL,
            CharacteristicProperties.WRITE,
            "Commands: photo, video:10 (duration in seconds)"
        ),
        CharacteristicDefinition(
            BLECharacteristics.SYSTEM_CONTROL,
            CharacteristicProperties.WRITE,
            "Commands: sleep, wake, restart"
        ),
        CharacteristicDefinition(
            BLECharacteristics.ACTION_RESPONSE,
            CharacteristicProperties.READ | CharacteristicProperties.NOTIFY,
            "Result of last action (JSON)"
        ),
    ]
)

DATA_SYNC_SERVICE = ServiceDefinition(
    uuid=BLEServices.DATA_SYNC,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.NOTES_DATA,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE | CharacteristicProperties.NOTIFY,
            "Notes data (JSON array, chunked if >512 bytes)",
            max_length=512
        ),
        CharacteristicDefinition(
            BLECharacteristics.TODOS_DATA,
            CharacteristicProperties.READ | CharacteristicProperties.WRITE | CharacteristicProperties.NOTIFY,
            "Todos data (JSON array, chunked if >512 bytes)",
            max_length=512
        ),
        CharacteristicDefinition(
            BLECharacteristics.STATUS_MESSAGE,
            CharacteristicProperties.READ | CharacteristicProperties.NOTIFY,
            "Latest status update message"
        ),
    ]
)

WIFI_CONFIG_SERVICE = ServiceDefinition(
    uuid=BLEServices.WIFI_CONFIG,
    characteristics=[
        CharacteristicDefinition(
            BLECharacteristics.WIFI_SSID,
            CharacteristicProperties.WRITE,
            "WiFi network SSID to connect to"
        ),
        CharacteristicDefinition(
            BLECharacteristics.WIFI_PASSWORD,
            CharacteristicProperties.WRITE,
            "WiFi network password (encrypted)"
        ),
        CharacteristicDefinition(
            BLECharacteristics.WIFI_STATUS,
            CharacteristicProperties.READ | CharacteristicProperties.NOTIFY,
            "WiFi connection status: disconnected, connecting, connected, failed"
        ),
        CharacteristicDefinition(
            BLECharacteristics.NETWORK_INFO,
            CharacteristicProperties.READ,
            "JSON: {ip, subnet, gateway} - current network info"
        ),
    ]
)


# All service definitions
ALL_SERVICES = [
    DEVICE_INFO_SERVICE,
    BATTERY_SERVICE_DEF,
    AUTHENTICATION_SERVICE,
    SETTINGS_SERVICE,
    QUICK_ACTIONS_SERVICE,
    DATA_SYNC_SERVICE,
    WIFI_CONFIG_SERVICE,
]


def get_service_by_uuid(uuid):
    """Get service definition by UUID"""
    for service in ALL_SERVICES:
        if service.uuid.lower() == uuid.lower():
            return service
    return None


def get_characteristic_by_uuid(uuid):
    """Get characteristic definition by UUID"""
    for service in ALL_SERVICES:
        for char in service.characteristics:
            if char.uuid.lower() == uuid.lower():
                return char
    return None
