import 'package:flutter/foundation.dart';
import 'bluetooth_manager.dart';
import 'api_client.dart';
import '../utils/app_preferences.dart';

enum ConnectionType { bluetooth, wifi, none }

class ConnectionManager extends ChangeNotifier {
  final BluetoothManager bluetoothManager;
  ApiClient? _apiClient;

  ConnectionType _currentConnection = ConnectionType.none;
  bool _isConnecting = false;

  ConnectionType get currentConnection => _currentConnection;
  bool get isConnecting => _isConnecting;
  bool get isConnected => _currentConnection != ConnectionType.none;
  ApiClient? get apiClient => _apiClient;

  ConnectionManager({required this.bluetoothManager}) {
    // Listen to Bluetooth connection changes
    bluetoothManager.addListener(_onBluetoothChanged);

    // Try to restore previous connection
    _restoreConnection();
  }

  void _onBluetoothChanged() {
    if (bluetoothManager.isConnected && _currentConnection == ConnectionType.none) {
      _currentConnection = ConnectionType.bluetooth;
      notifyListeners();
    } else if (!bluetoothManager.isConnected && _currentConnection == ConnectionType.bluetooth) {
      _currentConnection = ConnectionType.none;
      notifyListeners();
    }
  }

  Future<void> _restoreConnection() async {
    // Check if we have saved WiFi connection info
    final ipAddress = AppPreferences.getIpAddress();
    final apiKey = AppPreferences.getApiKey();

    if (ipAddress != null && apiKey != null) {
      // Try WiFi connection first
      await _connectWifi(ipAddress, apiKey);
    }
  }

  Future<bool> _connectWifi(String ipAddress, String apiKey) async {
    try {
      _apiClient = ApiClient(
        baseUrl: 'http://$ipAddress:5000',
        apiKey: apiKey,
      );

      // Test the connection
      await _apiClient!.getStatus();

      _currentConnection = ConnectionType.wifi;
      notifyListeners();
      return true;
    } catch (e) {
      debugPrint('WiFi connection failed: $e');
      _apiClient = null;
      return false;
    }
  }

  /// Complete pairing process via Bluetooth
  Future<bool> pair(String pairingCode) async {
    if (!bluetoothManager.isConnected) {
      throw Exception('Bluetooth not connected');
    }

    _isConnecting = true;
    notifyListeners();

    try {
      // 1. Verify pairing code
      final verified = await bluetoothManager.verifyPairingCode(pairingCode);
      if (!verified) {
        throw Exception('Invalid pairing code');
      }

      // 2. Get API key from Bluetooth
      final apiKey = await bluetoothManager.readApiKey();
      if (apiKey == null) {
        throw Exception('Failed to get API key');
      }

      // 3. Save to preferences
      await AppPreferences.setApiKey(apiKey);
      await AppPreferences.setPaired(true);

      // 4. Try to get WiFi connection info
      final connectionInfo = await _tryGetWifiInfo();
      if (connectionInfo != null) {
        await AppPreferences.setIpAddress(connectionInfo['ip']);
        await _connectWifi(connectionInfo['ip'], apiKey);
      }

      _isConnecting = false;
      notifyListeners();
      return true;
    } catch (e) {
      debugPrint('Pairing failed: $e');
      _isConnecting = false;
      notifyListeners();
      return false;
    }
  }

  /// Try to get WiFi connection info from smart glasses
  Future<Map<String, String>?> _tryGetWifiInfo() async {
    if (_apiClient == null) {
      // We don't have WiFi yet, try to get it via Bluetooth if available
      // For now, we'll need to set this manually or discover it
      return null;
    }

    try {
      final info = await _apiClient!.getConnectionInfo();
      return {
        'ip': info['ip_address'],
        'port': info['port'].toString(),
      };
    } catch (e) {
      debugPrint('Failed to get WiFi info: $e');
      return null;
    }
  }

  /// Send WiFi credentials via Bluetooth so glasses can connect to network
  Future<bool> sendWifiCredentials(String ssid, String password) async {
    if (!bluetoothManager.isConnected) {
      throw Exception('Bluetooth not connected');
    }

    return await bluetoothManager.sendWifiCredentials(ssid, password);
  }

  /// Manually set WiFi connection (after discovering IP)
  Future<bool> connectWifi(String ipAddress) async {
    final apiKey = AppPreferences.getApiKey();
    if (apiKey == null) {
      throw Exception('No API key available. Please pair first.');
    }

    _isConnecting = true;
    notifyListeners();

    final success = await _connectWifi(ipAddress, apiKey);

    if (success) {
      await AppPreferences.setIpAddress(ipAddress);
    }

    _isConnecting = false;
    notifyListeners();
    return success;
  }

  /// Disconnect from all connections
  Future<void> disconnect() async {
    await bluetoothManager.disconnect();
    _apiClient = null;
    _currentConnection = ConnectionType.none;
    notifyListeners();
  }

  /// Unpair device (clear all saved data)
  Future<void> unpair() async {
    await disconnect();
    await AppPreferences.clearAll();
    notifyListeners();
  }

  /// Choose which connection to use for an operation
  /// WiFi is preferred for high-bandwidth operations (camera, media)
  /// Bluetooth is used for low-bandwidth operations (settings, quick actions)
  ConnectionType getPreferredConnection(OperationType operation) {
    // If only one connection is available, use it
    if (_currentConnection == ConnectionType.wifi && _apiClient != null) {
      return ConnectionType.wifi;
    }
    if (_currentConnection == ConnectionType.bluetooth && bluetoothManager.isConnected) {
      return ConnectionType.bluetooth;
    }

    // If both available, choose based on operation
    if (_apiClient != null && bluetoothManager.isConnected) {
      switch (operation) {
        case OperationType.camera:
        case OperationType.media:
        case OperationType.conversation:
          return ConnectionType.wifi; // High bandwidth
        case OperationType.settings:
        case OperationType.quickAction:
          return ConnectionType.bluetooth; // Low bandwidth, more reliable
      }
    }

    return _currentConnection;
  }

  @override
  void dispose() {
    bluetoothManager.removeListener(_onBluetoothChanged);
    super.dispose();
  }
}

enum OperationType {
  camera,
  media,
  conversation,
  settings,
  quickAction,
}
