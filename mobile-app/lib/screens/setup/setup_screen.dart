import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/bluetooth_manager.dart';
import '../../services/connection_manager.dart';
import '../main_screen.dart';

class SetupScreen extends StatefulWidget {
  const SetupScreen({super.key});

  @override
  State<SetupScreen> createState() => _SetupScreenState();
}

class _SetupScreenState extends State<SetupScreen> {
  int _currentStep = 0;
  String? _selectedDeviceId;
  final _pairingCodeController = TextEditingController();
  final _ssidController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _pairingCodeController.dispose();
    _ssidController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _startScan() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final bluetoothManager = context.read<BluetoothManager>();
    await bluetoothManager.startScan();

    setState(() {
      _isLoading = false;
    });
  }

  Future<void> _connectToDevice(String deviceId) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final bluetoothManager = context.read<BluetoothManager>();
      final device = bluetoothManager.discoveredDevices.firstWhere(
        (d) => d.remoteId.toString() == deviceId,
      );

      await bluetoothManager.connect(device);

      // Read pairing code from device
      final pairingCode = await bluetoothManager.readPairingCode();
      if (pairingCode != null) {
        _pairingCodeController.text = pairingCode;
      }

      setState(() {
        _selectedDeviceId = deviceId;
        _currentStep = 1;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to connect: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _verifyPairingCode() async {
    if (_pairingCodeController.text.isEmpty) {
      setState(() {
        _errorMessage = 'Please enter pairing code';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final connectionManager = context.read<ConnectionManager>();
      final success = await connectionManager.pair(_pairingCodeController.text);

      if (success) {
        setState(() {
          _currentStep = 2;
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = 'Invalid pairing code';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Pairing failed: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _sendWifiCredentials() async {
    if (_ssidController.text.isEmpty) {
      setState(() {
        _errorMessage = 'Please enter WiFi SSID';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final connectionManager = context.read<ConnectionManager>();
      final success = await connectionManager.sendWifiCredentials(
        _ssidController.text,
        _passwordController.text,
      );

      if (success) {
        // Wait a bit for glasses to connect to WiFi
        await Future.delayed(const Duration(seconds: 3));

        // Try to connect via WiFi
        // For now, we'll skip this and go straight to main screen
        // In production, you'd discover the IP or have user enter it

        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const MainScreen()),
          );
        }
      } else {
        setState(() {
          _errorMessage = 'Failed to send WiFi credentials';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'WiFi setup failed: $e';
        _isLoading = false;
      });
    }
  }

  void _skipWifiSetup() {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const MainScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Glasses Setup'),
        centerTitle: true,
      ),
      body: Stepper(
        currentStep: _currentStep,
        onStepContinue: _isLoading ? null : _onStepContinue,
        onStepCancel: _currentStep > 0 ? () => setState(() => _currentStep--) : null,
        controlsBuilder: (context, details) {
          return Padding(
            padding: const EdgeInsets.only(top: 16.0),
            child: Row(
              children: [
                if (_isLoading)
                  const CircularProgressIndicator()
                else
                  ElevatedButton(
                    onPressed: details.onStepContinue,
                    child: Text(_currentStep == 2 ? 'Finish' : 'Continue'),
                  ),
                const SizedBox(width: 8),
                if (details.onStepCancel != null && !_isLoading)
                  TextButton(
                    onPressed: details.onStepCancel,
                    child: const Text('Back'),
                  ),
                if (_currentStep == 2 && !_isLoading)
                  TextButton(
                    onPressed: _skipWifiSetup,
                    child: const Text('Skip WiFi'),
                  ),
              ],
            ),
          );
        },
        steps: [
          Step(
            title: const Text('Find Glasses'),
            content: _buildScanStep(),
            isActive: _currentStep >= 0,
          ),
          Step(
            title: const Text('Pair Device'),
            content: _buildPairingStep(),
            isActive: _currentStep >= 1,
          ),
          Step(
            title: const Text('WiFi Setup'),
            content: _buildWifiStep(),
            isActive: _currentStep >= 2,
          ),
        ],
      ),
    );
  }

  Widget _buildScanStep() {
    return Consumer<BluetoothManager>(
      builder: (context, bluetoothManager, _) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Turn on your Smart Glasses and tap "Scan" to find them.'),
            const SizedBox(height: 16),
            if (_errorMessage != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Text(
                  _errorMessage!,
                  style: TextStyle(color: Theme.of(context).colorScheme.error),
                ),
              ),
            ElevatedButton.icon(
              onPressed: _isLoading ? null : _startScan,
              icon: const Icon(Icons.bluetooth_searching),
              label: const Text('Scan for Devices'),
            ),
            const SizedBox(height: 16),
            if (bluetoothManager.discoveredDevices.isNotEmpty) ...[
              const Text('Found devices:'),
              const SizedBox(height: 8),
              ...bluetoothManager.discoveredDevices.map((device) {
                return ListTile(
                  leading: const Icon(Icons.bluetooth),
                  title: Text(device.platformName.isNotEmpty
                      ? device.platformName
                      : 'Unknown Device'),
                  subtitle: Text(device.remoteId.toString()),
                  trailing: _isLoading
                      ? const CircularProgressIndicator()
                      : const Icon(Icons.arrow_forward),
                  onTap: _isLoading
                      ? null
                      : () => _connectToDevice(device.remoteId.toString()),
                );
              }),
            ],
          ],
        );
      },
    );
  }

  Widget _buildPairingStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Enter the 6-digit pairing code spoken by your Smart Glasses:',
        ),
        const SizedBox(height: 16),
        if (_errorMessage != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: Text(
              _errorMessage!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        TextField(
          controller: _pairingCodeController,
          decoration: const InputDecoration(
            labelText: 'Pairing Code',
            hintText: '123456',
            border: OutlineInputBorder(),
          ),
          keyboardType: TextInputType.number,
          maxLength: 6,
        ),
      ],
    );
  }

  Widget _buildWifiStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Connect your Smart Glasses to WiFi for enhanced features:',
        ),
        const SizedBox(height: 16),
        if (_errorMessage != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: Text(
              _errorMessage!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        TextField(
          controller: _ssidController,
          decoration: const InputDecoration(
            labelText: 'WiFi Network (SSID)',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _passwordController,
          decoration: const InputDecoration(
            labelText: 'WiFi Password',
            border: OutlineInputBorder(),
          ),
          obscureText: true,
        ),
      ],
    );
  }

  void _onStepContinue() {
    switch (_currentStep) {
      case 0:
        if (_selectedDeviceId == null) {
          setState(() {
            _errorMessage = 'Please select a device';
          });
        }
        break;
      case 1:
        _verifyPairingCode();
        break;
      case 2:
        _sendWifiCredentials();
        break;
    }
  }
}
