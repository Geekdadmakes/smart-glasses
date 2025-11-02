import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/connection_manager.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  File? _currentSnapshot;
  bool _isLiveMode = false;
  bool _isLoading = false;
  int _rotation = 0;
  bool _horizontalFlip = false;

  Future<void> _refreshSnapshot() async {
    setState(() => _isLoading = true);

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient != null) {
        final snapshot = await apiClient.getCameraSnapshot();
        setState(() {
          _currentSnapshot = snapshot;
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to get snapshot: $e')),
        );
      }
    }
  }

  Future<void> _capturePhoto() async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.capturePhoto();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Photo captured and saved!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to capture: $e')),
        );
      }
    }
  }

  Future<void> _recordVideo() async {
    // Show duration picker
    final duration = await showDialog<int>(
      context: context,
      builder: (context) => _VideoDurationDialog(),
    );

    if (duration == null) return;

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.recordVideo(duration);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Recording $duration second video...')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to record: $e')),
        );
      }
    }
  }

  Future<void> _rotateCamera() async {
    final newRotation = (_rotation + 90) % 360;

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.rotateCamera(newRotation);
      setState(() => _rotation = newRotation);

      await _refreshSnapshot();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to rotate: $e')),
        );
      }
    }
  }

  Future<void> _flipCamera() async {
    final newFlip = !_horizontalFlip;

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.flipCamera(newFlip);
      setState(() => _horizontalFlip = newFlip);

      await _refreshSnapshot();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to flip: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Camera'),
        actions: [
          IconButton(
            icon: Icon(_isLiveMode ? Icons.camera : Icons.videocam),
            onPressed: () {
              setState(() => _isLiveMode = !_isLiveMode);
            },
            tooltip: _isLiveMode ? 'Snapshot Mode' : 'Live Mode',
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: _buildViewfinder(),
          ),
          _buildControls(),
        ],
      ),
    );
  }

  Widget _buildViewfinder() {
    return Container(
      color: Colors.black,
      child: Center(
        child: _isLoading
            ? const CircularProgressIndicator()
            : _currentSnapshot != null
                ? Image.file(
                    _currentSnapshot!,
                    fit: BoxFit.contain,
                  )
                : Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.camera_alt_outlined,
                        size: 64,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Tap refresh to view camera',
                        style: TextStyle(
                          color: Colors.grey[400],
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
      ),
    );
  }

  Widget _buildControls() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Camera controls (rotate/flip)
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              IconButton.outlined(
                icon: const Icon(Icons.rotate_90_degrees_ccw),
                onPressed: _rotateCamera,
                tooltip: 'Rotate',
              ),
              const SizedBox(width: 16),
              IconButton.outlined(
                icon: const Icon(Icons.flip),
                onPressed: _flipCamera,
                tooltip: 'Flip Horizontal',
              ),
              const SizedBox(width: 16),
              IconButton.outlined(
                icon: const Icon(Icons.refresh),
                onPressed: _refreshSnapshot,
                tooltip: 'Refresh Snapshot',
              ),
            ],
          ),
          const SizedBox(height: 16),
          // Capture controls
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildCaptureButton(
                icon: Icons.camera_alt,
                label: 'Photo',
                onPressed: _capturePhoto,
              ),
              _buildCaptureButton(
                icon: Icons.videocam,
                label: 'Video',
                onPressed: _recordVideo,
                isPrimary: false,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCaptureButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
    bool isPrimary = true,
  }) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8),
        child: ElevatedButton.icon(
          onPressed: onPressed,
          icon: Icon(icon),
          label: Text(label),
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.all(16),
            backgroundColor: isPrimary ? null : Colors.grey[300],
            foregroundColor: isPrimary ? null : Colors.black87,
          ),
        ),
      ),
    );
  }
}

class _VideoDurationDialog extends StatefulWidget {
  @override
  State<_VideoDurationDialog> createState() => _VideoDurationDialogState();
}

class _VideoDurationDialogState extends State<_VideoDurationDialog> {
  int _duration = 10;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Video Duration'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('$_duration seconds'),
          Slider(
            value: _duration.toDouble(),
            min: 5,
            max: 60,
            divisions: 11,
            label: '$_duration s',
            onChanged: (value) {
              setState(() => _duration = value.toInt());
            },
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          onPressed: () => Navigator.pop(context, _duration),
          child: const Text('Record'),
        ),
      ],
    );
  }
}
