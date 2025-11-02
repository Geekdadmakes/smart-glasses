import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/setup/setup_screen.dart';
import 'screens/main_screen.dart';
import 'services/bluetooth_manager.dart';
import 'services/connection_manager.dart';
import 'utils/app_preferences.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize app preferences
  await AppPreferences.init();

  runApp(const SmartGlassesApp());
}

class SmartGlassesApp extends StatelessWidget {
  const SmartGlassesApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => BluetoothManager()),
        ChangeNotifierProxyProvider<BluetoothManager, ConnectionManager>(
          create: (context) => ConnectionManager(
            bluetoothManager: context.read<BluetoothManager>(),
          ),
          update: (context, bluetoothManager, connectionManager) =>
              connectionManager ?? ConnectionManager(
                bluetoothManager: bluetoothManager,
              ),
        ),
      ],
      child: MaterialApp(
        title: 'Smart Glasses',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.light,
          ),
          useMaterial3: true,
        ),
        darkTheme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
        ),
        themeMode: ThemeMode.system,
        home: const AppRouter(),
      ),
    );
  }
}

class AppRouter extends StatelessWidget {
  const AppRouter({super.key});

  @override
  Widget build(BuildContext context) {
    // Check if device is already paired
    final isPaired = AppPreferences.isPaired();

    if (isPaired) {
      // Go directly to main app
      return const MainScreen();
    } else {
      // Show setup flow
      return const SetupScreen();
    }
  }
}
