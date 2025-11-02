import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/connection_manager.dart';
import '../../models/status.dart';
import '../../models/conversation.dart';
import '../productivity/notes_screen.dart';
import '../productivity/todos_screen.dart';
import '../conversation/conversation_history_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Status? _status;
  List<ConversationMessage> _recentMessages = [];
  bool _isLoading = true;
  String? _errorMessage;
  Timer? _pollingTimer;

  // Auto-refresh every 5 seconds
  static const _pollingInterval = Duration(seconds: 5);

  @override
  void initState() {
    super.initState();
    _loadData();
    _startPolling();
  }

  @override
  void dispose() {
    _stopPolling();
    super.dispose();
  }

  void _startPolling() {
    _pollingTimer = Timer.periodic(_pollingInterval, (_) {
      if (mounted) {
        _loadData(silent: true);
      }
    });
  }

  void _stopPolling() {
    _pollingTimer?.cancel();
    _pollingTimer = null;
  }

  Future<void> _loadData({bool silent = false}) async {
    if (!silent) {
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
    }

    try {
      final connectionManager = context.read<ConnectionManager>();
      final apiClient = connectionManager.apiClient;

      if (apiClient != null) {
        final status = await apiClient.getStatus();
        final history = await apiClient.getConversationHistory();

        if (mounted) {
          setState(() {
            _status = status;
            _recentMessages = history.take(5).toList();
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _errorMessage = 'Not connected to Smart Glasses';
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      // Only show error on manual refresh, not during polling
      if (!silent && mounted) {
        setState(() {
          _errorMessage = 'Failed to load data: $e';
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _toggleSleepMode() async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      if (_status?.mode == 'sleep') {
        await apiClient.wake();
      } else {
        await apiClient.sleep();
      }

      await _loadData();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to toggle mode: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Glasses'),
        actions: [
          // Auto-refresh indicator
          if (_pollingTimer != null && _pollingTimer!.isActive)
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: Center(
                child: Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: Colors.green,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.green.withOpacity(0.5),
                        blurRadius: 4,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _loadData(silent: false),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => _loadData(silent: false),
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _errorMessage != null
                ? _buildErrorView()
                : _buildDashboard(),
      ),
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
          Text(
            _errorMessage!,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildDashboard() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildStatusCard(),
        const SizedBox(height: 16),
        _buildQuickActions(),
        const SizedBox(height: 16),
        _buildRecentConversation(),
      ],
    );
  }

  Widget _buildStatusCard() {
    final isSleeping = _status?.mode == 'sleep';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Status',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: _status?.connected == true
                        ? Colors.green.withOpacity(0.2)
                        : Colors.red.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _status?.connected == true
                            ? Icons.check_circle
                            : Icons.error,
                        size: 16,
                        color: _status?.connected == true
                            ? Colors.green
                            : Colors.red,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _status?.connected == true ? 'Connected' : 'Disconnected',
                        style: TextStyle(
                          color: _status?.connected == true
                              ? Colors.green
                              : Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            _buildStatusRow(Icons.person, 'Name', _status?.name ?? 'Unknown'),
            _buildStatusRow(Icons.psychology, 'Personality',
                _status?.personality ?? 'Unknown'),
            _buildStatusRow(
              Icons.power_settings_new,
              'Mode',
              isSleeping ? 'Sleep' : 'Active',
            ),
            _buildStatusRow(
              Icons.battery_std,
              'Battery',
              '${_status?.battery ?? 0}%',
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _toggleSleepMode,
                icon: Icon(isSleeping ? Icons.power : Icons.power_off),
                label: Text(isSleeping ? 'Wake Up' : 'Sleep'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: 12),
          Text(
            '$label:',
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              value,
              textAlign: TextAlign.end,
              style: TextStyle(
                color: Theme.of(context).colorScheme.secondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Quick Actions',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildQuickAction(
                  Icons.camera_alt,
                  'Photo',
                  _takePhoto,
                ),
                _buildQuickAction(
                  Icons.videocam,
                  'Video',
                  _recordVideo,
                ),
                _buildQuickAction(
                  Icons.mic,
                  'Notes',
                  _navigateToNotes,
                ),
                _buildQuickAction(
                  Icons.check_box,
                  'Todos',
                  _navigateToTodos,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickAction(IconData icon, String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, size: 32),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentConversation() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Recent Conversation',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                TextButton(
                  onPressed: _navigateToConversationHistory,
                  child: const Text('View All'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (_recentMessages.isEmpty)
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(
                  child: Text('No recent conversations'),
                ),
              )
            else
              ..._recentMessages.map((msg) => _buildMessageBubble(msg)),
          ],
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ConversationMessage message) {
    final isUser = message.role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isUser
              ? Theme.of(context).colorScheme.primaryContainer
              : Theme.of(context).colorScheme.secondaryContainer,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          message.content,
          style: TextStyle(
            color: isUser
                ? Theme.of(context).colorScheme.onPrimaryContainer
                : Theme.of(context).colorScheme.onSecondaryContainer,
          ),
        ),
      ),
    );
  }

  Future<void> _takePhoto() async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.capturePhoto();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Photo captured!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to capture photo: $e')),
        );
      }
    }
  }

  Future<void> _recordVideo() async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.recordVideo(10);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Recording 10 second video...')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to record video: $e')),
        );
      }
    }
  }

  void _navigateToNotes() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const NotesScreen()),
    );
  }

  void _navigateToTodos() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const TodosScreen()),
    );
  }

  void _navigateToConversationHistory() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ConversationHistoryScreen()),
    );
  }
}
