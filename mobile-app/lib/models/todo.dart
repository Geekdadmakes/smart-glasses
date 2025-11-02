class Todo {
  final String id;
  final String task;
  final bool completed;
  final DateTime timestamp;

  Todo({
    required this.id,
    required this.task,
    required this.completed,
    required this.timestamp,
  });

  factory Todo.fromJson(Map<String, dynamic> json) {
    return Todo(
      id: json['id'],
      task: json['task'],
      completed: json['completed'] ?? false,
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'task': task,
      'completed': completed,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}
