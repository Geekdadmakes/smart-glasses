import 'package:shared_preferences/shared_preferences.dart';

class AppPreferences {
  static SharedPreferences? _prefs;

  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  // Pairing status
  static bool isPaired() {
    return _prefs?.getBool('is_paired') ?? false;
  }

  static Future<void> setPaired(bool paired) async {
    await _prefs?.setBool('is_paired', paired);
  }

  // Device info
  static String? getDeviceId() {
    return _prefs?.getString('device_id');
  }

  static Future<void> setDeviceId(String id) async {
    await _prefs?.setString('device_id', id);
  }

  static String? getDeviceName() {
    return _prefs?.getString('device_name');
  }

  static Future<void> setDeviceName(String name) async {
    await _prefs?.setString('device_name', name);
  }

  // Network info
  static String? getIpAddress() {
    return _prefs?.getString('ip_address');
  }

  static Future<void> setIpAddress(String ip) async {
    await _prefs?.setString('ip_address', ip);
  }

  static String? getApiKey() {
    return _prefs?.getString('api_key');
  }

  static Future<void> setApiKey(String key) async {
    await _prefs?.setString('api_key', key);
  }

  // Connection preference
  static String getPreferredConnection() {
    return _prefs?.getString('preferred_connection') ?? 'auto';
  }

  static Future<void> setPreferredConnection(String type) async {
    await _prefs?.setString('preferred_connection', type);
  }

  // Clear all data (unpair)
  static Future<void> clearAll() async {
    await _prefs?.clear();
  }
}
