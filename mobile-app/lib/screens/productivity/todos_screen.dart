import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/connection_manager.dart';
import '../../models/todo.dart';

class TodosScreen extends StatefulWidget {
  const TodosScreen({super.key});

  @override
  State<TodosScreen> createState() => _TodosScreenState();
}

class _TodosScreenState extends State<TodosScreen> {
  List<Todo> _todos = [];
  bool _isLoading = true;
  String? _errorMessage;
  final _todoController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadTodos();
  }

  @override
  void dispose() {
    _todoController.dispose();
    super.dispose();
  }

  Future<void> _loadTodos() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient != null) {
        final todos = await apiClient.listTodos();
        setState(() {
          _todos = todos;
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
        _errorMessage = 'Failed to load todos: $e';
        _isLoading = false;
      });
    }
  }

  Future<void> _addTodo() async {
    if (_todoController.text.isEmpty) return;

    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.addTodo(_todoController.text);
      _todoController.clear();
      await _loadTodos();

      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Todo added')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to add todo: $e')),
        );
      }
    }
  }

  Future<void> _toggleTodo(Todo todo) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.toggleTodo(todo.id);
      await _loadTodos();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to toggle todo: $e')),
        );
      }
    }
  }

  Future<void> _deleteTodo(Todo todo) async {
    try {
      final apiClient = context.read<ConnectionManager>().apiClient;
      if (apiClient == null) return;

      await apiClient.deleteTodo(todo.id);
      await _loadTodos();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Todo deleted')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete todo: $e')),
        );
      }
    }
  }

  void _showAddTodoDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Todo'),
        content: TextField(
          controller: _todoController,
          decoration: const InputDecoration(
            labelText: 'Task',
            hintText: 'Enter your task...',
            border: OutlineInputBorder(),
          ),
          autofocus: true,
        ),
        actions: [
          TextButton(
            onPressed: () {
              _todoController.clear();
              Navigator.pop(context);
            },
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: _addTodo,
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Todos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadTodos,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? _buildErrorView()
              : _buildTodosList(),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddTodoDialog,
        child: const Icon(Icons.add),
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
          Text(_errorMessage!),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadTodos,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildTodosList() {
    if (_todos.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.check_circle_outline,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              'No todos yet',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Tap + to add your first task',
              style: TextStyle(
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
      );
    }

    // Separate completed and pending todos
    final pendingTodos = _todos.where((t) => !t.completed).toList();
    final completedTodos = _todos.where((t) => t.completed).toList();

    return ListView(
      padding: const EdgeInsets.all(8),
      children: [
        if (pendingTodos.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              'Pending (${pendingTodos.length})',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ),
          ...pendingTodos.map((todo) => _buildTodoCard(todo)),
        ],
        if (completedTodos.isNotEmpty) ...[
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              'Completed (${completedTodos.length})',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.grey[600],
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ),
          ...completedTodos.map((todo) => _buildTodoCard(todo)),
        ],
      ],
    );
  }

  Widget _buildTodoCard(Todo todo) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
      child: ListTile(
        leading: Checkbox(
          value: todo.completed,
          onChanged: (_) => _toggleTodo(todo),
        ),
        title: Text(
          todo.task,
          style: TextStyle(
            decoration: todo.completed ? TextDecoration.lineThrough : null,
            color: todo.completed ? Colors.grey : null,
          ),
        ),
        subtitle: Text(
          _formatDate(todo.timestamp),
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete, color: Colors.red),
          onPressed: () => _deleteTodo(todo),
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'Today ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays == 1) {
      return 'Yesterday ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${date.month}/${date.day}/${date.year}';
    }
  }
}
