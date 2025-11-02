import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';

class BluetoothManager extends ChangeNotifier {
  // BLE Service UUIDs (matching Python backend)
  static const String authServiceUuid = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String settingsServiceUuid = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String quickActionsServiceUuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String dataSyncServiceUuid = "6E400004-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String wifiConfigServiceUuid = "6E400005-B5A3-F393-E0A9-E50E24DCCA9E";

  // Characteristic UUIDs - Authentication
  static const String pairingCodeCharUuid = "6E400011-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String apiKeyCharUuid = "6E400012-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String pairingStatusCharUuid = "6E400013-B5A3-F393-E0A9-E50E24DCCA9E";

  // Characteristic UUIDs - Settings
  static const String personalityCharUuid = "6E400021-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String nameCharUuid = "6E400022-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String wakeWordCharUuid = "6E400023-B5A3-F393-E0A9-E50E24DCCA9E";
  static const String voiceEngineCharUuid = "6E400024-B5A3-F393-E0A9-E50E24DCCA9E";

  BluetoothDevice? _connectedDevice;
  List<BluetoothDevice> _discoveredDevices = [];
  bool _isScanning = false;
  bool _isConnected = false;

  BluetoothDevice? get connectedDevice => _connectedDevice;
  List<BluetoothDevice> get discoveredDevices => _discoveredDevices;
  bool get isScanning => _isScanning;
  bool get isConnected => _isConnected;

  Future<void> startScan() async {
    _discoveredDevices.clear();
    _isScanning = true;
    notifyListeners();

    try {
      // Start scanning
      await FlutterBluePlus.startScan(timeout: const Duration(seconds: 10));

      // Listen to scan results
      FlutterBluePlus.scanResults.listen((results) {
        for (ScanResult r in results) {
          // Look for our smart glasses device
          if (r.device.platformName.contains('Smart Glasses') ||
              r.device.platformName.contains('Raspberry Pi')) {
            if (!_discoveredDevices.contains(r.device)) {
              _discoveredDevices.add(r.device);
              notifyListeners();
            }
          }
        }
      });

      // Wait for scan to complete
      await Future.delayed(const Duration(seconds: 10));
      await FlutterBluePlus.stopScan();
    } catch (e) {
      debugPrint('Error scanning: $e');
    }

    _isScanning = false;
    notifyListeners();
  }

  Future<void> connect(BluetoothDevice device) async {
    try {
      await device.connect();
      _connectedDevice = device;
      _isConnected = true;
      notifyListeners();

      // Discover services
      await device.discoverServices();
    } catch (e) {
      debugPrint('Error connecting: $e');
      rethrow;
    }
  }

  Future<void> disconnect() async {
    if (_connectedDevice != null) {
      await _connectedDevice!.disconnect();
      _connectedDevice = null;
      _isConnected = false;
      notifyListeners();
    }
  }

  // Read pairing code from smart glasses
  Future<String?> readPairingCode() async {
    if (_connectedDevice == null) return null;

    try {
      List<BluetoothService> services = await _connectedDevice!.discoverServices();

      for (BluetoothService service in services) {
        if (service.uuid.toString().toUpperCase() == authServiceUuid.toUpperCase()) {
          for (BluetoothCharacteristic char in service.characteristics) {
            if (char.uuid.toString().toUpperCase() == pairingCodeCharUuid.toUpperCase()) {
              List<int> value = await char.read();
              return utf8.decode(value);
            }
          }
        }
      }
    } catch (e) {
      debugPrint('Error reading pairing code: $e');
    }
    return null;
  }

  // Write pairing code to verify
  Future<bool> verifyPairingCode(String code) async {
    if (_connectedDevice == null) return false;

    try {
      List<BluetoothService> services = await _connectedDevice!.discoverServices();

      for (BluetoothService service in services) {
        if (service.uuid.toString().toUpperCase() == authServiceUuid.toUpperCase()) {
          for (BluetoothCharacteristic char in service.characteristics) {
            if (char.uuid.toString().toUpperCase() == pairingStatusCharUuid.toUpperCase()) {
              await char.write(utf8.encode(code));
              // Read response to verify
              List<int> value = await char.read();
              String response = utf8.decode(value);
              return response == 'paired';
            }
          }
        }
      }
    } catch (e) {
      debugPrint('Error verifying pairing code: $e');
    }
    return false;
  }

  // Read API key for WiFi authentication
  Future<String?> readApiKey() async {
    if (_connectedDevice == null) return null;

    try {
      List<BluetoothService> services = await _connectedDevice!.discoverServices();

      for (BluetoothService service in services) {
        if (service.uuid.toString().toUpperCase() == authServiceUuid.toUpperCase()) {
          for (BluetoothCharacteristic char in service.characteristics) {
            if (char.uuid.toString().toUpperCase() == apiKeyCharUuid.toUpperCase()) {
              List<int> value = await char.read();
              return utf8.decode(value);
            }
          }
        }
      }
    } catch (e) {
      debugPrint('Error reading API key: $e');
    }
    return null;
  }

  // Write WiFi credentials to smart glasses
  Future<bool> sendWifiCredentials(String ssid, String password) async {
    if (_connectedDevice == null) return false;

    try {
      List<BluetoothService> services = await _connectedDevice!.discoverServices();

      for (BluetoothService service in services) {
        if (service.uuid.toString().toUpperCase() == wifiConfigServiceUuid.toUpperCase()) {
          for (BluetoothCharacteristic char in service.characteristics) {
            // SSID characteristic: 6E400051
            if (char.uuid.toString().contains('6E400051')) {
              await char.write(utf8.encode(ssid));
            }
            // Password characteristic: 6E400052
            if (char.uuid.toString().contains('6E400052')) {
              await char.write(utf8.encode(password));
            }
          }
        }
      }
      return true;
    } catch (e) {
      debugPrint('Error sending WiFi credentials: $e');
      return false;
    }
  }

  // Read personality setting
  Future<String?> readPersonality() async {
    return await _readCharacteristic(settingsServiceUuid, personalityCharUuid);
  }

  // Write personality setting
  Future<bool> writePersonality(String personality) async {
    return await _writeCharacteristic(settingsServiceUuid, personalityCharUuid, personality);
  }

  // Read name setting
  Future<String?> readName() async {
    return await _readCharacteristic(settingsServiceUuid, nameCharUuid);
  }

  // Write name setting
  Future<bool> writeName(String name) async {
    return await _writeCharacteristic(settingsServiceUuid, nameCharUuid, name);
  }

  // Read wake word setting
  Future<String?> readWakeWord() async {
    return await _readCharacteristic(settingsServiceUuid, wakeWordCharUuid);
  }

  // Write wake word setting
  Future<bool> writeWakeWord(String wakeWord) async {
    return await _writeCharacteristic(settingsServiceUuid, wakeWordCharUuid, wakeWord);
  }

  // Helper method to read characteristic
  Future<String?> _readCharacteristic(String serviceUuid, String charUuid) async {
    if (_connectedDevice == null) return null;

    try {
      List<BluetoothService> services = await _connectedDevice!.discoverServices();

      for (BluetoothService service in services) {
        if (service.uuid.toString().toUpperCase() == serviceUuid.toUpperCase()) {
          for (BluetoothCharacteristic char in service.characteristics) {
            if (char.uuid.toString().toUpperCase() == charUuid.toUpperCase()) {
              List<int> value = await char.read();
              return utf8.decode(value);
            }
          }
        }
      }
    } catch (e) {
      debugPrint('Error reading characteristic: $e');
    }
    return null;
  }

  // Helper method to write characteristic
  Future<bool> _writeCharacteristic(String serviceUuid, String charUuid, String value) async {
    if (_connectedDevice == null) return false;

    try {
      List<BluetoothService> services = await _connectedDevice!.discoverServices();

      for (BluetoothService service in services) {
        if (service.uuid.toString().toUpperCase() == serviceUuid.toUpperCase()) {
          for (BluetoothCharacteristic char in service.characteristics) {
            if (char.uuid.toString().toUpperCase() == charUuid.toUpperCase()) {
              await char.write(utf8.encode(value));
              return true;
            }
          }
        }
      }
    } catch (e) {
      debugPrint('Error writing characteristic: $e');
    }
    return false;
  }
}
