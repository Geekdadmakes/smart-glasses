import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/connection_manager.dart';
import '../../models/settings.dart';
import '../setup/setup_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  Settings? _settings;
  bool _isLoading = true;
  String? _errorMessage;

  // Personality options
  final List<String> _personalities = [
    'friendly',
    'professional',
    'humorous',
    'concise',
    'detailed',
  ];

  // Voice engine options
  final List<String> _voiceEngines = [
    'gtts',
    'pyttsx3',
    'espeak',
  ];

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient != null) {
        final settings = await apiClient.getSettings();
        setState(() {
          _settings = settings;
          _isLoading = false;
        });
      } else {
        setState(() {
          _errorMessage = 'Not connected';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load settings: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _updatePersonality(String personality) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.updatePersonality(personality);
      await _loadSettings();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Personality updated')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    }
  }

  Future<void> _updateName(String name) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.updateName(name);
      await _loadSettings();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Name updated')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    }
  }

  Future<void> _updateWakeWord(String wakeWord) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.updateWakeWord(wakeWord);
      await _loadSettings();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Wake word updated')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    }
  }

  Future<void> _updateVoiceEngine(String engine) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.updateVoice(engine: engine);
      await _loadSettings();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Voice engine updated')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    }
  }

  Future<void> _updateVoiceRate(int rate) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.updateVoice(rate: rate);
      setState(() {
        _settings = _settings?.copyWith(voiceRate: rate);
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    }
  }

  Future<void> _updateVoiceVolume(double volume) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.updateVoice(volume: volume);
      setState(() {
        _settings = _settings?.copyWith(voiceVolume: volume);
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Update failed: $e')),
        );
      }
    }
  }

  Future<void> _unpairDevice() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Unpair Device'),
        content: const Text(
          'Are you sure you want to unpair your Smart Glasses? You will need to go through the setup process again.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Unpair'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      final connectionManager = context.read<ConnectionManager>();
      await connectionManager.unpair();

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const SetupScreen()),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Unpair failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadSettings,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? _buildErrorView()
              : _buildSettings(),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Theme.of(context).colorScheme.error,
          ),
          const SizedBox(height: 16),
          Text(_errorMessage!),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadSettings,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildSettings() {
    return ListView(
      children: [
        _buildSection('AI Settings', [
          _buildPersonalityTile(),
          _buildNameTile(),
          _buildWakeWordTile(),
        ]),
        _buildSection('Voice Settings', [
          _buildVoiceEngineTile(),
          _buildVoiceRateTile(),
          _buildVoiceVolumeTile(),
        ]),
        _buildSection('Connection', [
          _buildConnectionInfoTile(),
        ]),
        _buildSection('Device', [
          _buildUnpairTile(),
        ]),
      ],
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.bold,
                ),
          ),
        ),
        ...children,
        const Divider(),
      ],
    );
  }

  Widget _buildPersonalityTile() {
    return ListTile(
      leading: const Icon(Icons.psychology),
      title: const Text('Personality'),
      subtitle: Text(_settings?.personality ?? 'Unknown'),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () => _showPersonalityDialog(),
    );
  }

  Widget _buildNameTile() {
    return ListTile(
      leading: const Icon(Icons.badge),
      title: const Text('Name'),
      subtitle: Text(_settings?.name ?? 'Unknown'),
      trailing: const Icon(Icons.edit, size: 20),
      onTap: () => _showNameDialog(),
    );
  }

  Widget _buildWakeWordTile() {
    return ListTile(
      leading: const Icon(Icons.mic),
      title: const Text('Wake Word'),
      subtitle: Text(_settings?.wakeWord ?? 'Unknown'),
      trailing: const Icon(Icons.edit, size: 20),
      onTap: () => _showWakeWordDialog(),
    );
  }

  Widget _buildVoiceEngineTile() {
    return ListTile(
      leading: const Icon(Icons.record_voice_over),
      title: const Text('Voice Engine'),
      subtitle: Text(_settings?.voiceEngine ?? 'Unknown'),
      trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      onTap: () => _showVoiceEngineDialog(),
    );
  }

  Widget _buildVoiceRateTile() {
    return ListTile(
      leading: const Icon(Icons.speed),
      title: const Text('Voice Speed'),
      subtitle: Slider(
        value: _settings?.voiceRate.toDouble() ?? 150,
        min: 50,
        max: 300,
        divisions: 50,
        label: '${_settings?.voiceRate ?? 150}',
        onChanged: (value) => _updateVoiceRate(value.toInt()),
      ),
    );
  }

  Widget _buildVoiceVolumeTile() {
    return ListTile(
      leading: const Icon(Icons.volume_up),
      title: const Text('Voice Volume'),
      subtitle: Slider(
        value: _settings?.voiceVolume ?? 0.6,
        min: 0.0,
        max: 1.0,
        divisions: 10,
        label: '${((_settings?.voiceVolume ?? 0.6) * 100).toInt()}%',
        onChanged: _updateVoiceVolume,
      ),
    );
  }

  Widget _buildConnectionInfoTile() {
    return Consumer<ConnectionManager>(
      builder: (context, connectionManager, _) {
        return ListTile(
          leading: Icon(
            connectionManager.isConnected ? Icons.check_circle : Icons.error,
            color: connectionManager.isConnected ? Colors.green : Colors.red,
          ),
          title: const Text('Connection Status'),
          subtitle: Text(
            connectionManager.isConnected
                ? 'Connected via ${connectionManager.currentConnection.name}'
                : 'Disconnected',
          ),
        );
      },
    );
  }

  Widget _buildUnpairTile() {
    return ListTile(
      leading: const Icon(Icons.link_off, color: Colors.red),
      title: const Text('Unpair Device', style: TextStyle(color: Colors.red)),
      subtitle: const Text('Remove this device from Smart Glasses'),
      onTap: _unpairDevice,
    );
  }

  void _showPersonalityDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Choose Personality'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: _personalities.map((personality) {
            return RadioListTile<String>(
              title: Text(personality[0].toUpperCase() + personality.substring(1)),
              value: personality,
              groupValue: _settings?.personality,
              onChanged: (value) {
                Navigator.pop(context);
                if (value != null) _updatePersonality(value);
              },
            );
          }).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }

  void _showNameDialog() {
    final controller = TextEditingController(text: _settings?.name);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Change Name'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'AI Name',
            hintText: 'Assistant',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              if (controller.text.isNotEmpty) {
                _updateName(controller.text);
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showWakeWordDialog() {
    final controller = TextEditingController(text: _settings?.wakeWord);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Change Wake Word'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Wake Word',
            hintText: 'computer',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              if (controller.text.isNotEmpty) {
                _updateWakeWord(controller.text);
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showVoiceEngineDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Choose Voice Engine'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: _voiceEngines.map((engine) {
            return RadioListTile<String>(
              title: Text(engine.toUpperCase()),
              value: engine,
              groupValue: _settings?.voiceEngine,
              onChanged: (value) {
                Navigator.pop(context);
                if (value != null) _updateVoiceEngine(value);
              },
            );
          }).toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }
}
