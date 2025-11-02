class Settings {
  final String personality;
  final String name;
  final String wakeWord;
  final String voiceEngine;
  final int voiceRate;
  final double voiceVolume;

  Settings({
    required this.personality,
    required this.name,
    required this.wakeWord,
    required this.voiceEngine,
    required this.voiceRate,
    required this.voiceVolume,
  });

  factory Settings.fromJson(Map<String, dynamic> json) {
    return Settings(
      personality: json['personality'] ?? 'friendly',
      name: json['name'] ?? 'Assistant',
      wakeWord: json['wake_word'] ?? 'computer',
      voiceEngine: json['voice_engine'] ?? 'gtts',
      voiceRate: json['voice_rate'] ?? 150,
      voiceVolume: (json['voice_volume'] ?? 0.6).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'personality': personality,
      'name': name,
      'wake_word': wakeWord,
      'voice_engine': voiceEngine,
      'voice_rate': voiceRate,
      'voice_volume': voiceVolume,
    };
  }

  Settings copyWith({
    String? personality,
    String? name,
    String? wakeWord,
    String? voiceEngine,
    int? voiceRate,
    double? voiceVolume,
  }) {
    return Settings(
      personality: personality ?? this.personality,
      name: name ?? this.name,
      wakeWord: wakeWord ?? this.wakeWord,
      voiceEngine: voiceEngine ?? this.voiceEngine,
      voiceRate: voiceRate ?? this.voiceRate,
      voiceVolume: voiceVolume ?? this.voiceVolume,
    );
  }
}
