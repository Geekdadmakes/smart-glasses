class Status {
  final String mode;
  final String personality;
  final String name;
  final int battery;
  final bool connected;
  final DateTime timestamp;

  Status({
    required this.mode,
    required this.personality,
    required this.name,
    required this.battery,
    required this.connected,
    required this.timestamp,
  });

  factory Status.fromJson(Map<String, dynamic> json) {
    return Status(
      mode: json['mode'] ?? 'unknown',
      personality: json['personality'] ?? 'friendly',
      name: json['name'] ?? 'Assistant',
      battery: json['battery'] ?? 0,
      connected: json['connected'] ?? false,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'mode': mode,
      'personality': personality,
      'name': name,
      'battery': battery,
      'connected': connected,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
