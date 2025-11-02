class Video {
  final String filename;
  final DateTime timestamp;
  final int size;
  final int duration;

  Video({
    required this.filename,
    required this.timestamp,
    required this.size,
    this.duration = 0,
  });

  factory Video.fromJson(Map<String, dynamic> json) {
    return Video(
      filename: json['filename'],
      timestamp: DateTime.parse(json['timestamp']),
      size: json['size'] ?? 0,
      duration: json['duration'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'filename': filename,
      'timestamp': timestamp.toIso8601String(),
      'size': size,
      'duration': duration,
    };
  }
}
