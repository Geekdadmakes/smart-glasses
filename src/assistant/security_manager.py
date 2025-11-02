"""
Security & Privacy Manager - Clear history, privacy mode, data management
"""

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manage security and privacy features"""

    def __init__(self, memory_dir='./memory'):
        """Initialize security manager"""
        self.memory_dir = Path(memory_dir)
        self.security_file = self.memory_dir / 'security_settings.json'

        # Load settings
        self.settings = self._load_settings()

        logger.info("Security Manager initialized")

    def _load_settings(self):
        """Load security settings"""
        try:
            if self.security_file.exists():
                with open(self.security_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading security settings: {e}")

        return {
            'private_mode': False,
            'save_conversation_history': True,
            'save_photos': True,
            'voice_confirmation_required': False
        }

    def _save_settings(self):
        """Save security settings"""
        try:
            with open(self.security_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving security settings: {e}")

    def clear_conversation_history(self):
        """Clear conversation history"""
        try:
            history_file = self.memory_dir / 'conversation_memory.json'

            if history_file.exists():
                # Backup before clearing
                backup_file = self.memory_dir / 'conversation_memory_backup.json'
                if history_file.exists():
                    with open(history_file, 'r') as f:
                        data = json.load(f)
                    with open(backup_file, 'w') as f:
                        json.dump(data, f, indent=2)

                # Clear
                with open(history_file, 'w') as f:
                    json.dump([], f)

                logger.info("Conversation history cleared")
                return "Conversation history cleared. Backup saved."
            else:
                return "No conversation history to clear"

        except Exception as e:
            logger.error(f"Error clearing history: {e}")
            return "Couldn't clear conversation history"

    def clear_all_data(self):
        """Clear all user data (use with caution!)"""
        try:
            cleared_items = []

            # Clear conversation history
            history_file = self.memory_dir / 'conversation_memory.json'
            if history_file.exists():
                os.remove(history_file)
                cleared_items.append("conversation history")

            # Clear preferences
            prefs_file = self.memory_dir / 'user_preferences.json'
            if prefs_file.exists():
                os.remove(prefs_file)
                cleared_items.append("preferences")

            # Clear productivity data
            productivity_dir = self.memory_dir / 'productivity'
            if productivity_dir.exists():
                for file in productivity_dir.glob('*.json'):
                    os.remove(file)
                cleared_items.append("productivity data")

            # Clear fitness data
            fitness_dir = self.memory_dir / 'fitness'
            if fitness_dir.exists():
                for file in fitness_dir.glob('*.json'):
                    os.remove(file)
                cleared_items.append("fitness data")

            # Clear communications
            comms_dir = self.memory_dir / 'communications'
            if comms_dir.exists():
                for file in comms_dir.glob('*.json'):
                    os.remove(file)
                cleared_items.append("communications data")

            if cleared_items:
                logger.warning(f"All data cleared: {', '.join(cleared_items)}")
                return f"Cleared: {', '.join(cleared_items)}. This cannot be undone."
            else:
                return "No data to clear"

        except Exception as e:
            logger.error(f"Error clearing all data: {e}")
            return f"Error clearing data: {str(e)}"

    def enable_private_mode(self):
        """Enable private mode (don't save history)"""
        self.settings['private_mode'] = True
        self.settings['save_conversation_history'] = False
        self._save_settings()

        logger.info("Private mode enabled")
        return "Private mode enabled. Conversation history will not be saved."

    def disable_private_mode(self):
        """Disable private mode"""
        self.settings['private_mode'] = False
        self.settings['save_conversation_history'] = True
        self._save_settings()

        logger.info("Private mode disabled")
        return "Private mode disabled. Conversation history will be saved normally."

    def get_privacy_status(self):
        """Get current privacy settings status"""
        private_mode = self.settings.get('private_mode', False)
        save_history = self.settings.get('save_conversation_history', True)

        result = f"Privacy status: "
        result += f"Private mode: {'ON' if private_mode else 'OFF'}. "
        result += f"Save history: {'YES' if save_history else 'NO'}. "

        logger.info("Privacy status retrieved")
        return result

    def get_data_summary(self):
        """Get summary of stored data"""
        try:
            summary = "Data stored: "
            items = []

            # Check conversation history
            history_file = self.memory_dir / 'conversation_memory.json'
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                    if history:
                        items.append(f"{len(history)} conversation messages")
                except:
                    pass

            # Check productivity
            productivity_dir = self.memory_dir / 'productivity'
            if productivity_dir.exists():
                notes_file = productivity_dir / 'notes.json'
                if notes_file.exists():
                    try:
                        with open(notes_file, 'r') as f:
                            notes = json.load(f)
                        if notes:
                            items.append(f"{len(notes)} notes")
                    except:
                        pass

            # Check contacts
            comms_dir = self.memory_dir / 'communications'
            if comms_dir.exists():
                contacts_file = comms_dir / 'contacts.json'
                if contacts_file.exists():
                    try:
                        with open(contacts_file, 'r') as f:
                            contacts = json.load(f)
                        if contacts:
                            items.append(f"{len(contacts)} contacts")
                    except:
                        pass

            if items:
                summary += ", ".join(items)
            else:
                summary += "None"

            logger.info("Data summary retrieved")
            return summary

        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return "Couldn't get data summary"

    def export_data(self):
        """Export all data (returns summary, actual export would need implementation)"""
        summary = self.get_data_summary()

        result = f"Data export requested. {summary}. "
        result += "To export, access the memory folder on your device."

        logger.info("Data export requested")
        return result
