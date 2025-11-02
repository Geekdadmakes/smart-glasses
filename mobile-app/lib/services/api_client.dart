import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/status.dart';
import '../models/photo.dart';
import '../models/video.dart';
import '../models/note.dart';
import '../models/todo.dart';
import '../models/conversation.dart';
import '../models/settings.dart';

class ApiClient {
  final String baseUrl;
  final String apiKey;

  ApiClient({required this.baseUrl, required this.apiKey});

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
      };

  // Status & Connection
  Future<Status> getStatus() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/status'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return Status.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to get status');
    }
  }

  Future<Map<String, dynamic>> getConnectionInfo() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/connection/info'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to get connection info');
    }
  }

  // Settings
  Future<Settings> getSettings() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/settings'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      return Settings.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to get settings');
    }
  }

  Future<bool> updatePersonality(String personality) async {
    final response = await http.put(
      Uri.parse('$baseUrl/api/settings/personality'),
      headers: _headers,
      body: json.encode({'personality': personality}),
    );

    return response.statusCode == 200;
  }

  Future<bool> updateName(String name) async {
    final response = await http.put(
      Uri.parse('$baseUrl/api/settings/name'),
      headers: _headers,
      body: json.encode({'name': name}),
    );

    return response.statusCode == 200;
  }

  Future<bool> updateWakeWord(String wakeWord) async {
    final response = await http.put(
      Uri.parse('$baseUrl/api/settings/wake_word'),
      headers: _headers,
      body: json.encode({'wake_word': wakeWord}),
    );

    return response.statusCode == 200;
  }

  Future<bool> updateVoice({String? engine, int? rate, double? volume}) async {
    Map<String, dynamic> body = {};
    if (engine != null) body['engine'] = engine;
    if (rate != null) body['rate'] = rate;
    if (volume != null) body['volume'] = volume;

    final response = await http.put(
      Uri.parse('$baseUrl/api/settings/voice'),
      headers: _headers,
      body: json.encode(body),
    );

    return response.statusCode == 200;
  }

  // Camera
  Future<File?> getCameraSnapshot() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/camera/snapshot'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      // Save to temporary file
      final tempDir = Directory.systemTemp;
      final file = File('${tempDir.path}/snapshot_${DateTime.now().millisecondsSinceEpoch}.jpg');
      await file.writeAsBytes(response.bodyBytes);
      return file;
    }
    return null;
  }

  Future<bool> capturePhoto() async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/camera/capture'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  Future<bool> recordVideo(int duration) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/camera/record'),
      headers: _headers,
      body: json.encode({'duration': duration}),
    );

    return response.statusCode == 200;
  }

  Future<bool> rotateCamera(int degrees) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/camera/rotate'),
      headers: _headers,
      body: json.encode({'degrees': degrees}),
    );

    return response.statusCode == 200;
  }

  Future<bool> flipCamera(bool horizontal) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/camera/flip'),
      headers: _headers,
      body: json.encode({'horizontal': horizontal}),
    );

    return response.statusCode == 200;
  }

  // Media - Photos
  Future<List<Photo>> listPhotos() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/media/photos'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['photos'];
      return data.map((json) => Photo.fromJson(json)).toList();
    } else {
      throw Exception('Failed to list photos');
    }
  }

  Future<File?> downloadPhoto(String filename) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/media/photos/$filename'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final tempDir = Directory.systemTemp;
      final file = File('${tempDir.path}/$filename');
      await file.writeAsBytes(response.bodyBytes);
      return file;
    }
    return null;
  }

  Future<bool> deletePhoto(String filename) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/api/media/photos/$filename'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  // Media - Videos
  Future<List<Video>> listVideos() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/media/videos'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['videos'];
      return data.map((json) => Video.fromJson(json)).toList();
    } else {
      throw Exception('Failed to list videos');
    }
  }

  Future<File?> downloadVideo(String filename) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/media/videos/$filename'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final tempDir = Directory.systemTemp;
      final file = File('${tempDir.path}/$filename');
      await file.writeAsBytes(response.bodyBytes);
      return file;
    }
    return null;
  }

  Future<bool> deleteVideo(String filename) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/api/media/videos/$filename'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  // Productivity - Notes
  Future<List<Note>> listNotes() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/productivity/notes'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['notes'];
      return data.map((json) => Note.fromJson(json)).toList();
    } else {
      throw Exception('Failed to list notes');
    }
  }

  Future<bool> addNote(String content) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/productivity/notes'),
      headers: _headers,
      body: json.encode({'content': content}),
    );

    return response.statusCode == 200;
  }

  Future<bool> deleteNote(String id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/api/productivity/notes/$id'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  // Productivity - Todos
  Future<List<Todo>> listTodos() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/productivity/todos'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['todos'];
      return data.map((json) => Todo.fromJson(json)).toList();
    } else {
      throw Exception('Failed to list todos');
    }
  }

  Future<bool> addTodo(String task) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/productivity/todos'),
      headers: _headers,
      body: json.encode({'task': task}),
    );

    return response.statusCode == 200;
  }

  Future<bool> toggleTodo(String id) async {
    final response = await http.put(
      Uri.parse('$baseUrl/api/productivity/todos/$id/toggle'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  Future<bool> deleteTodo(String id) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/api/productivity/todos/$id'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  // Conversation History
  Future<List<ConversationMessage>> getConversationHistory() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/conversation/history'),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body)['history'];
      return data.map((json) => ConversationMessage.fromJson(json)).toList();
    } else {
      throw Exception('Failed to get conversation history');
    }
  }

  Future<bool> clearConversationHistory() async {
    final response = await http.delete(
      Uri.parse('$baseUrl/api/conversation/history'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  // System Control
  Future<bool> sleep() async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/system/sleep'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }

  Future<bool> wake() async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/system/wake'),
      headers: _headers,
    );

    return response.statusCode == 200;
  }
}
