class Photo {
  final String filename;
  final DateTime timestamp;
  final int size;

  Photo({
    required this.filename,
    required this.timestamp,
    required this.size,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    return Photo(
      filename: json['filename'],
      timestamp: DateTime.parse(json['timestamp']),
      size: json['size'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'filename': filename,
      'timestamp': timestamp.toIso8601String(),
      'size': size,
    };
  }
}
