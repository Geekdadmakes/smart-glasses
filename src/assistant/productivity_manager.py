"""
Productivity Manager - Handle notes, reminders, todos, and shopping lists
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ProductivityManager:
    """Manage productivity features: notes, reminders, todos, shopping lists"""

    def __init__(self, data_dir='./productivity'):
        """Initialize productivity manager"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.notes_file = self.data_dir / 'notes.json'
        self.reminders_file = self.data_dir / 'reminders.json'
        self.shopping_list_file = self.data_dir / 'shopping_list.json'
        self.todos_file = self.data_dir / 'todos.json'

        # Load data
        self.notes = self._load_json(self.notes_file, [])
        self.reminders = self._load_json(self.reminders_file, [])
        self.shopping_list = self._load_json(self.shopping_list_file, [])
        self.todos = self._load_json(self.todos_file, [])

        logger.info("Productivity Manager initialized")

    def _load_json(self, file_path, default):
        """Load JSON file or return default"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
        return default

    def _save_json(self, file_path, data):
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving {file_path}: {e}")

    # NOTES
    def add_note(self, note_text):
        """Add a voice note"""
        note = {
            'id': len(self.notes) + 1,
            'text': note_text,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d %I:%M %p')
        }
        self.notes.append(note)
        self._save_json(self.notes_file, self.notes)
        logger.info(f"Note added: {note_text[:50]}...")
        return f"Note saved: {note_text}"

    def get_notes(self):
        """Get all notes"""
        if not self.notes:
            return "You have no notes saved"

        notes_text = f"You have {len(self.notes)} notes:\n"
        for note in self.notes[-5:]:  # Last 5 notes
            notes_text += f"• {note['date']}: {note['text']}\n"
        return notes_text.strip()

    # REMINDERS
    def add_reminder(self, task, time_str):
        """Add a reminder"""
        reminder = {
            'id': len(self.reminders) + 1,
            'task': task,
            'time': time_str,
            'created': datetime.now().isoformat(),
            'completed': False
        }
        self.reminders.append(reminder)
        self._save_json(self.reminders_file, self.reminders)
        logger.info(f"Reminder added: {task} at {time_str}")
        return f"Reminder set: {task} at {time_str}"

    def get_reminders(self):
        """Get active reminders"""
        active = [r for r in self.reminders if not r['completed']]
        if not active:
            return "You have no reminders set"

        reminders_text = f"You have {len(active)} reminders:\n"
        for reminder in active:
            reminders_text += f"• {reminder['time']}: {reminder['task']}\n"
        return reminders_text.strip()

    # SHOPPING LIST
    def add_to_shopping_list(self, items_str):
        """Add items to shopping list"""
        items = [item.strip() for item in items_str.split(',')]
        added = []
        for item in items:
            if item and item not in self.shopping_list:
                self.shopping_list.append(item)
                added.append(item)

        self._save_json(self.shopping_list_file, self.shopping_list)

        if added:
            logger.info(f"Added to shopping list: {', '.join(added)}")
            return f"Added to shopping list: {', '.join(added)}"
        else:
            return "Items already on the list"

    def get_shopping_list(self):
        """Get shopping list"""
        if not self.shopping_list:
            return "Your shopping list is empty"

        list_text = f"You have {len(self.shopping_list)} items on your shopping list:\n"
        for item in self.shopping_list:
            list_text += f"• {item}\n"
        return list_text.strip()

    def clear_shopping_list(self):
        """Clear shopping list"""
        self.shopping_list = []
        self._save_json(self.shopping_list_file, self.shopping_list)
        return "Shopping list cleared"

    # TODOS
    def add_todo(self, task, priority='medium'):
        """Add a todo item"""
        todo = {
            'id': len(self.todos) + 1,
            'task': task,
            'priority': priority,
            'created': datetime.now().isoformat(),
            'completed': False
        }
        self.todos.append(todo)
        self._save_json(self.todos_file, self.todos)
        logger.info(f"Todo added: {task} (priority: {priority})")
        return f"Added to todos: {task} (priority: {priority})"

    def get_todos(self):
        """Get active todos"""
        active = [t for t in self.todos if not t['completed']]
        if not active:
            return "You have no pending tasks"

        todos_text = f"You have {len(active)} pending tasks:\n"
        for todo in sorted(active, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x['priority'], 1)):
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(todo['priority'], '⚪')
            todos_text += f"{priority_emoji} {todo['task']}\n"
        return todos_text.strip()

    def complete_todo(self, task_id):
        """Mark todo as completed"""
        for todo in self.todos:
            if todo['id'] == task_id:
                todo['completed'] = True
                self._save_json(self.todos_file, self.todos)
                return f"Task completed: {todo['task']}"
        return "Task not found"
