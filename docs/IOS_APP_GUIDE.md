# iOS Companion App - Complete Development Guide

## Table of Contents
1. [Overview](#overview)
2. [Backend Setup](#backend-setup)
3. [BLE Services Reference](#ble-services-reference)
4. [WiFi REST API Reference](#wifi-rest-api-reference)
5. [iOS App Architecture](#ios-app-architecture)
6. [Connection Flow](#connection-flow)
7. [Example Code](#example-code)

---

## Overview

The Smart Glasses iOS companion app uses a **hybrid Bluetooth LE + WiFi architecture** for optimal performance:

- **Bluetooth LE**: Initial pairing, setup, and low-bandwidth operations
- **WiFi**: High-bandwidth operations (camera streaming, media downloads)
- **Automatic Switching**: Intelligently routes requests based on availability and bandwidth requirements

### Key Features
- Bluetooth pairing with spoken pairing code
- WiFi credential provisioning via BLE
- Complete settings control (personality, voice, wake word)
- Real-time camera viewfinder (live stream + snapshot modes)
- Photo/video gallery management
- Notes and todos synchronization
- Conversation history viewer
- Remote camera controls (rotate, flip)

---

## Backend Setup

### 1. Start the Smart Glasses Application

The connection manager starts automatically when you run the smart glasses app:

```bash
cd ~/smart-glasses
python3 src/main.py
```

You should see:
```
Starting iOS companion app servers...
✓ BLE server started successfully
✓ WiFi API server started successfully
✓ WiFi API available at: http://192.168.1.XXX:5000/api/status
✓ Connection Manager started (2/2 servers running)
```

### 2. Verify Services

**Check BLE is advertising:**
```bash
# On the Pi
sudo hcitool lescan
```

**Check WiFi API is accessible:**
```bash
# From your computer on the same network
curl http://YOUR_PI_IP:5000/api/connection/test
```

Should return:
```json
{
  "status": "ok",
  "message": "Connection successful"
}
```

### 3. Get API Key

The API key is automatically generated and stored at:
```
~/smart-glasses/config/api_key.txt
```

To view it:
```bash
cat ~/smart-glasses/config/api_key.txt
```

You'll need this key for WiFi API authentication.

---

## BLE Services Reference

### Service UUIDs

| Service | UUID | Purpose |
|---------|------|---------|
| Device Information | `0000180a-0000-1000-8000-00805f9b34fb` | Standard device info |
| Battery | `0000180f-0000-1000-8000-00805f9b34fb` | Battery level |
| Authentication | `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | Pairing and API key |
| Settings | `6E400002-B5A3-F393-E0A9-E50E24DCCA9E` | AI configuration |
| Quick Actions | `6E400003-B5A3-F393-E0A9-E50E24DCCA9E` | Camera, system control |
| Data Sync | `6E400004-B5A3-F393-E0A9-E50E24DCCA9E` | Notes, todos |
| WiFi Config | `6E400005-B5A3-F393-E0A9-E50E24DCCA9E` | WiFi provisioning |

### Authentication Service Characteristics

#### API Key (Read)
- **UUID**: `6E400101-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read
- **Format**: UTF-8 string
- **Purpose**: Get API key for WiFi authentication

#### Pairing Code (Read + Notify)
- **UUID**: `6E400102-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Notify
- **Format**: 6-digit string (e.g., "123456")
- **Purpose**: Get pairing code (also spoken via TTS)

#### Pairing Status (Read + Write)
- **UUID**: `6E400103-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write
- **Format**: Single byte (0=unpaired, 1=pairing, 2=paired)
- **Purpose**: Confirm pairing completion

### Settings Service Characteristics

#### Personality (Read + Write)
- **UUID**: `6E400201-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write
- **Format**: UTF-8 string
- **Values**: "friendly", "professional", "witty", "jarvis", "casual"

#### Assistant Name (Read + Write)
- **UUID**: `6E400202-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write
- **Format**: UTF-8 string
- **Example**: "Jarvis"

#### Wake Word Config (Read + Write)
- **UUID**: `6E400203-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write
- **Format**: JSON
- **Example**: `{"keyword": "hey glasses", "sensitivity": 0.5}`

#### Voice Settings (Read + Write)
- **UUID**: `6E400204-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write
- **Format**: JSON
- **Example**: `{"engine": "gtts", "rate": 150, "volume": 0.6}`

#### Status Mode (Read + Notify)
- **UUID**: `6E400205-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Notify
- **Format**: UTF-8 string
- **Values**: "sleep", "active"

### Quick Actions Service Characteristics

#### Camera Control (Write)
- **UUID**: `6E400301-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Write
- **Format**: UTF-8 string
- **Commands**:
  - "photo" - Take a photo
  - "video:10" - Record 10 second video

#### System Control (Write)
- **UUID**: `6E400302-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Write
- **Format**: UTF-8 string
- **Commands**: "sleep", "wake", "restart"

#### Action Response (Read + Notify)
- **UUID**: `6E400303-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Notify
- **Format**: JSON
- **Example**: `{"success": true, "path": "/home/pi/photos/photo_001.jpg"}`

### Data Sync Service Characteristics

#### Notes Data (Read + Write + Notify)
- **UUID**: `6E400401-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write, Notify
- **Format**: JSON array (max 512 bytes)
- **Note**: Returns 5 most recent notes

#### Todos Data (Read + Write + Notify)
- **UUID**: `6E400402-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Write, Notify
- **Format**: JSON array (max 512 bytes)
- **Note**: Returns 5 most recent todos

### WiFi Config Service Characteristics

#### WiFi SSID (Write)
- **UUID**: `6E400501-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Write
- **Format**: UTF-8 string
- **Purpose**: Set WiFi network name

#### WiFi Password (Write)
- **UUID**: `6E400502-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Write
- **Format**: UTF-8 string
- **Purpose**: Set WiFi password

#### WiFi Status (Read + Notify)
- **UUID**: `6E400503-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read, Notify
- **Format**: UTF-8 string
- **Values**: "disconnected", "connecting", "connected", "failed"

#### Network Info (Read)
- **UUID**: `6E400504-B5A3-F393-E0A9-E50E24DCCA9E`
- **Properties**: Read
- **Format**: JSON
- **Example**: `{"ip": "192.168.1.100", "subnet": "255.255.255.0", "gateway": "192.168.1.1"}`

---

## WiFi REST API Reference

### Base URL
```
http://YOUR_PI_IP:5000/api
```

### Authentication
All endpoints (except `/connection/test`) require API key authentication:

**Header:**
```
X-API-Key: YOUR_API_KEY_HERE
```

### Status & Connection Endpoints

#### GET /status
Get current system status.

**Response:**
```json
{
  "mode": "active",
  "personality": "jarvis",
  "name": "Jarvis",
  "battery": 85,
  "connected": true,
  "timestamp": "2025-11-01T15:30:00"
}
```

#### GET /connection/test
Test connection (no auth required).

**Response:**
```json
{
  "status": "ok",
  "message": "Connection successful"
}
```

#### GET /connection/type
Get connection type.

**Response:**
```json
{
  "type": "wifi"
}
```

### Settings Endpoints

#### GET /settings
Get all settings.

**Response:**
```json
{
  "personality": "jarvis",
  "name": "Jarvis",
  "wake_word": {
    "keyword": "hey glasses",
    "sensitivity": 0.5
  },
  "voice": {
    "engine": "gtts",
    "rate": 150,
    "volume": 0.6
  },
  "camera": {
    "resolution": {"width": 1920, "height": 1080},
    "rotation": 0,
    "flip_horizontal": false,
    "flip_vertical": false
  }
}
```

#### PUT /settings/personality
Update AI personality.

**Request Body:**
```json
{
  "personality": "witty"
}
```

**Response:**
```json
{
  "success": true,
  "personality": "witty"
}
```

#### PUT /settings/name
Update assistant name.

**Request Body:**
```json
{
  "name": "Alfred"
}
```

**Response:**
```json
{
  "success": true,
  "name": "Alfred"
}
```

#### PUT /settings/wake-word
Update wake word configuration.

**Request Body:**
```json
{
  "keyword": "computer",
  "sensitivity": 0.7
}
```

**Response:**
```json
{
  "success": true
}
```

#### PUT /settings/voice
Update voice settings.

**Request Body:**
```json
{
  "engine": "elevenlabs",
  "rate": 160,
  "volume": 0.7
}
```

**Response:**
```json
{
  "success": true
}
```

### Camera Endpoints

#### GET /camera/stream
MJPEG live camera stream (not yet implemented).

**Response:** MJPEG stream

#### GET /camera/snapshot
Get single camera snapshot.

**Response:** JPEG image

#### POST /camera/capture
Capture photo remotely.

**Response:**
```json
{
  "success": true,
  "path": "/home/pi/photos/photo_001.jpg",
  "filename": "photo_001.jpg"
}
```

#### POST /camera/record
Record video remotely.

**Request Body:**
```json
{
  "duration": 15
}
```

**Response:**
```json
{
  "success": true,
  "path": "/home/pi/videos/video_001.h264",
  "filename": "video_001.h264"
}
```

### Media Endpoints

#### GET /photos
List all photos.

**Response:**
```json
[
  {
    "id": "photo_001",
    "filename": "photo_001.jpg",
    "size": 1024000,
    "timestamp": "2025-11-01T14:30:00"
  }
]
```

#### GET /photos/:id
Download specific photo.

**Response:** JPEG image file

#### DELETE /photos/:id
Delete photo.

**Response:**
```json
{
  "success": true
}
```

#### GET /videos
List all videos.

**Response:**
```json
[
  {
    "id": "video_001",
    "filename": "video_001.h264",
    "size": 5120000,
    "timestamp": "2025-11-01T14:35:00"
  }
]
```

#### GET /videos/:id
Download specific video.

**Response:** H264 video file

#### DELETE /videos/:id
Delete video.

**Response:**
```json
{
  "success": true
}
```

### Productivity Endpoints

#### GET /notes
Get all notes.

**Response:**
```json
[
  {
    "id": "1",
    "content": "Remember to buy milk",
    "timestamp": "2025-11-01T10:00:00"
  }
]
```

#### POST /notes
Add new note.

**Request Body:**
```json
{
  "content": "Call mom at 5pm"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Note added successfully"
}
```

#### GET /todos
Get all todos.

**Response:**
```json
[
  {
    "id": "1",
    "task": "Finish project report",
    "priority": "high",
    "completed": false,
    "timestamp": "2025-11-01T09:00:00"
  }
]
```

#### POST /todos
Add new todo.

**Request Body:**
```json
{
  "task": "Buy groceries",
  "priority": "medium"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Todo added successfully"
}
```

### Conversation Endpoints

#### GET /conversation
Get conversation history.

**Response:**
```json
[
  {
    "role": "user",
    "content": "What time is it?",
    "timestamp": "2025-11-01T14:00:00"
  },
  {
    "role": "assistant",
    "content": "It's 2 PM.",
    "timestamp": "2025-11-01T14:00:01"
  }
]
```

#### DELETE /conversation
Clear conversation history.

**Response:**
```json
{
  "success": true,
  "message": "Conversation history cleared"
}
```

### System Control Endpoints

#### POST /control/sleep
Put system to sleep mode.

**Response:**
```json
{
  "success": true,
  "message": "Going to sleep"
}
```

#### POST /control/wake
Wake system up.

**Response:**
```json
{
  "success": true,
  "message": "Waking up"
}
```

---

## iOS App Architecture

### Recommended Structure

```
SmartGlassesApp/
├── Models/
│   ├── Status.swift
│   ├── Settings.swift
│   ├── Photo.swift, Video.swift
│   ├── Note.swift, Todo.swift
│   └── ConnectionType.swift
├── Bluetooth/
│   ├── BluetoothManager.swift
│   └── BLEServices.swift
├── Network/
│   ├── APIClient.swift
│   ├── ConnectionManager.swift
│   └── NetworkError.swift
├── ViewModels/
│   ├── DashboardViewModel.swift
│   ├── CameraViewModel.swift
│   ├── GalleryViewModel.swift
│   ├── SettingsViewModel.swift
│   └── ConnectionViewModel.swift
├── Views/
│   ├── Setup/
│   │   └── SetupView.swift
│   ├── Dashboard/
│   │   └── DashboardView.swift
│   ├── Camera/
│   │   └── CameraView.swift
│   ├── Gallery/
│   │   └── GalleryView.swift
│   ├── Settings/
│   │   └── SettingsView.swift
│   └── ContentView.swift
└── Utilities/
    ├── KeychainHelper.swift
    └── UserDefaultsKeys.swift
```

---

## Connection Flow

### Initial Setup Flow

```
1. User opens iOS app for first time
   ↓
2. App scans for BLE devices
   ↓
3. "Smart Glasses" appears in list
   ↓
4. User taps to connect
   ↓
5. App connects to BLE
   ↓
6. App reads pairing code from BLE characteristic
   ↓
7. Pi speaks pairing code via TTS
   ↓
8. User enters code in app
   ↓
9. App writes "2" (paired) to pairing status characteristic
   ↓
10. App reads API key from BLE characteristic
    ↓
11. App saves API key to Keychain
    ↓
12. Optional: Send WiFi credentials via BLE
    ↓
13. Pi connects to WiFi
    ↓
14. App discovers Pi on WiFi (via network info characteristic)
    ↓
15. Connection upgrades to WiFi automatically
```

### Daily Use Flow

```
1. App launches
   ↓
2. ConnectionManager checks for WiFi (tries saved IP)
   ↓
3. If WiFi available → Use WiFi
   ↓
4. If WiFi unavailable → Connect via BLE
   ↓
5. User requests operation
   ↓
6. High bandwidth (camera, photos)? → Requires WiFi
   ↓
7. Low bandwidth (settings, notes)? → Works on BLE or WiFi
   ↓
8. ConnectionManager routes request accordingly
```

---

## Example Code

### iOS Bluetooth Manager

```swift
import CoreBluetooth

class BluetoothManager: NSObject, ObservableObject {
    @Published var discoveredDevices: [CBPeripheral] = []
    @Published var connectedDevice: CBPeripheral?
    @Published var connectionState: ConnectionState = .disconnected
    @Published var pairingCode: String?
    @Published var apiKey: String?

    private var centralManager: CBCentralManager!
    private var characteristics: [CBUUID: CBCharacteristic] = [:]

    enum ConnectionState {
        case disconnected, scanning, connecting, connected, paired
    }

    override init() {
        super.init()
        centralManager = CBCentralManager(delegate: self, queue: nil)
    }

    func startScanning() {
        guard centralManager.state == .poweredOn else {
            print("Bluetooth is not available")
            return
        }

        discoveredDevices.removeAll()
        connectionState = .scanning

        // Scan for devices advertising smart glasses service
        centralManager.scanForPeripherals(
            withServices: [CBUUID(string: "6E400001-B5A3-F393-E0A9-E50E24DCCA9E")],
            options: nil
        )
    }

    func stopScanning() {
        centralManager.stopScan()
    }

    func connect(to peripheral: CBPeripheral) {
        stopScanning()
        connectionState = .connecting
        centralManager.connect(peripheral, options: nil)
    }

    func readPairingCode() async throws -> String {
        guard let char = characteristics[BLECharacteristics.pairingCode] else {
            throw BLEError.characteristicNotFound
        }

        guard let device = connectedDevice else {
            throw BLEError.notConnected
        }

        // Read pairing code
        device.readValue(for: char)

        // Wait for response (simplified - use proper async handling)
        try await Task.sleep(nanoseconds: 1_000_000_000)

        guard let value = char.value, let code = String(data: value, encoding: .utf8) else {
            throw BLEError.invalidData
        }

        pairingCode = code
        return code
    }

    func confirmPairing() async throws {
        guard let char = characteristics[BLECharacteristics.pairingStatus] else {
            throw BLEError.characteristicNotFound
        }

        guard let device = connectedDevice else {
            throw BLEError.notConnected
        }

        // Write "2" (paired)
        let data = Data([2])
        device.writeValue(data, for: char, type: .withResponse)

        connectionState = .paired
    }

    func readAPIKey() async throws -> String {
        guard let char = characteristics[BLECharacteristics.apiKey] else {
            throw BLEError.characteristicNotFound
        }

        guard let device = connectedDevice else {
            throw BLEError.notConnected
        }

        device.readValue(for: char)

        try await Task.sleep(nanoseconds: 1_000_000_000)

        guard let value = char.value, let key = String(data: value, encoding: .utf8) else {
            throw BLEError.invalidData
        }

        apiKey = key

        // Save to Keychain
        KeychainHelper.save(apiKey: key)

        return key
    }

    func updatePersonality(_ personality: String) async throws {
        guard let char = characteristics[BLECharacteristics.personality] else {
            throw BLEError.characteristicNotFound
        }

        guard let device = connectedDevice else {
            throw BLEError.notConnected
        }

        let data = personality.data(using: .utf8)!
        device.writeValue(data, for: char, type: .withResponse)
    }
}

// MARK: - CBCentralManagerDelegate
extension BluetoothManager: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state == .poweredOn {
            print("Bluetooth is ready")
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        if !discoveredDevices.contains(peripheral) {
            discoveredDevices.append(peripheral)
        }
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        connectionState = .connected
        connectedDevice = peripheral
        peripheral.delegate = self

        // Discover services
        peripheral.discoverServices([
            CBUUID(string: "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"),  // Auth
            CBUUID(string: "6E400002-B5A3-F393-E0A9-E50E24DCCA9E")   // Settings
        ])
    }
}

// MARK: - CBPeripheralDelegate
extension BluetoothManager: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = peripheral.services else { return }

        for service in services {
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        guard let characteristics = service.characteristics else { return }

        for characteristic in characteristics {
            self.characteristics[characteristic.uuid] = characteristic

            // Subscribe to notifications
            if characteristic.properties.contains(.notify) {
                peripheral.setNotifyValue(true, for: characteristic)
            }
        }
    }
}

enum BLEError: Error {
    case characteristicNotFound
    case notConnected
    case invalidData
}

struct BLECharacteristics {
    static let apiKey = CBUUID(string: "6E400101-B5A3-F393-E0A9-E50E24DCCA9E")
    static let pairingCode = CBUUID(string: "6E400102-B5A3-F393-E0A9-E50E24DCCA9E")
    static let pairingStatus = CBUUID(string: "6E400103-B5A3-F393-E0A9-E50E24DCCA9E")
    static let personality = CBUUID(string: "6E400201-B5A3-F393-E0A9-E50E24DCCA9E")
    static let assistantName = CBUUID(string: "6E400202-B5A3-F393-E0A9-E50E24DCCA9E")
}
```

### iOS API Client

```swift
import Foundation

class APIClient {
    static let shared = APIClient()

    var baseURL: URL {
        let ip = UserDefaults.standard.string(forKey: "glassesIP") ?? "192.168.1.100"
        return URL(string: "http://\(ip):5000/api")!
    }

    var apiKey: String {
        KeychainHelper.load(key: "apiKey") ?? ""
    }

    func getStatus() async throws -> Status {
        let url = baseURL.appendingPathComponent("status")
        var request = URLRequest(url: url)
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(Status.self, from: data)
    }

    func updatePersonality(_ personality: String) async throws {
        let url = baseURL.appendingPathComponent("settings/personality")
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = ["personality": personality]
        request.httpBody = try JSONEncoder().encode(body)

        let (_, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw APIError.requestFailed
        }
    }

    func getPhotos() async throws -> [Photo] {
        let url = baseURL.appendingPathComponent("photos")
        var request = URLRequest(url: url)
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")

        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode([Photo].self, from: data)
    }

    func downloadPhoto(id: String) async throws -> UIImage {
        let url = baseURL.appendingPathComponent("photos/\(id)")
        var request = URLRequest(url: url)
        request.setValue(apiKey, forHTTPHeaderField: "X-API-Key")

        let (data, _) = try await URLSession.shared.data(for: request)

        guard let image = UIImage(data: data) else {
            throw APIError.invalidImage
        }

        return image
    }
}

enum APIError: Error {
    case requestFailed
    case invalidImage
}
```

### iOS Connection Manager

```swift
@MainActor
class ConnectionManager: ObservableObject {
    @Published var connectionType: ConnectionType = .none
    @Published var isConnected = false

    let bluetoothManager = BluetoothManager()
    let apiClient = APIClient()

    enum ConnectionType {
        case none, bluetooth, wifi, both
    }

    func connect() async {
        // Try WiFi first
        do {
            let _ = try await apiClient.getStatus()
            connectionType = .wifi
            isConnected = true
            print("Connected via WiFi")
            return
        } catch {
            print("WiFi not available, trying Bluetooth...")
        }

        // Fallback to Bluetooth
        bluetoothManager.startScanning()
        connectionType = .bluetooth
        // Wait for BLE connection...
    }

    func getStatus() async throws -> Status {
        switch connectionType {
        case .wifi, .both:
            return try await apiClient.getStatus()
        case .bluetooth:
            // Get status via BLE
            throw ConnectionError.notImplemented
        case .none:
            throw ConnectionError.notConnected
        }
    }

    func updatePersonality(_ personality: String) async throws {
        // Works on both WiFi and BLE
        switch connectionType {
        case .wifi, .both:
            try await apiClient.updatePersonality(personality)
        case .bluetooth:
            try await bluetoothManager.updatePersonality(personality)
        case .none:
            throw ConnectionError.notConnected
        }
    }

    func downloadPhoto(id: String) async throws -> UIImage {
        // Requires WiFi
        guard connectionType == .wifi || connectionType == .both else {
            throw ConnectionError.wifiRequired
        }

        return try await apiClient.downloadPhoto(id: id)
    }
}

enum ConnectionError: Error {
    case notConnected
    case wifiRequired
    case notImplemented
}
```

---

## Next Steps

1. **Start Smart Glasses App**: Run `python3 src/main.py` and verify both BLE and WiFi servers start
2. **Test BLE**: Use a BLE scanner app (e.g., LightBlue) to verify services are advertising
3. **Test WiFi API**: Use curl or Postman to test endpoints
4. **Build iOS App**: Start with connection setup, then add features progressively
5. **Test Integration**: Verify automatic switching between BLE and WiFi

---

## Troubleshooting

### BLE Not Advertising
```bash
# Check Bluetooth status
sudo systemctl status bluetooth

# Restart Bluetooth
sudo systemctl restart bluetooth

# Check if bless is installed
pip3 list | grep bless
```

### WiFi API Not Accessible
```bash
# Check if Flask is running
ps aux | grep python

# Check network interface
ip addr show

# Test locally on Pi
curl http://localhost:5000/api/connection/test
```

### Can't Connect from iOS
- Ensure iOS device and Pi are on same WiFi network
- Check firewall isn't blocking port 5000
- Verify API key is correct
- Check API server logs for errors

---

**Happy Coding! 🚀**
