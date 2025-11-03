#!/usr/bin/env python3
"""
HUD Overlay System for Smart Glasses
Manages different display modes and overlays
"""

import time
import logging
from typing import Optional, Dict, List
from datetime import datetime
from .display_manager import DisplayManager

logger = logging.getLogger(__name__)


class HUDOverlay:
    """Manages HUD overlays and display modes for Smart Glasses"""

    def __init__(self, display_manager: DisplayManager, config: dict = None):
        """
        Initialize HUD overlay system

        Args:
            display_manager: DisplayManager instance
            config: Configuration dict
        """
        self.display = display_manager
        self.config = config or {}

        # Current state
        self.current_mode = "status"  # "status", "caption", "notification", "menu"
        self.battery_level = 100
        self.connection_status = False
        self.system_mode = "active"  # "active", "sleep", "listening"

        # Caption buffer
        self.caption_text = ""
        self.caption_enabled = self.config.get('captions', True)

        # Notification queue
        self.notification_queue = []

        logger.info("HUD Overlay initialized")

    def update_status(
        self,
        battery: Optional[int] = None,
        mode: Optional[str] = None,
        connected: Optional[bool] = None
    ):
        """Update system status"""
        if battery is not None:
            self.battery_level = battery
        if mode is not None:
            self.system_mode = mode
        if connected is not None:
            self.connection_status = connected

    def show_status_display(self):
        """Show the status display (default HUD mode)"""
        self.current_mode = "status"

        # Get current time
        time_str = datetime.now().strftime("%H:%M")

        # Show status bar
        self.display.show_status(
            battery=self.battery_level,
            mode=self.system_mode,
            connected=self.connection_status,
            time_str=time_str
        )

    def show_listening_mode(self):
        """Show listening indicator"""
        self.update_status(mode="listening")
        self.display.show_text(
            text="LISTENING...",
            font_size="large",
            color=(255, 165, 0),
            align="center",
            clear_screen=True
        )

    def show_ai_response(self, text: str, streaming: bool = False):
        """
        Show AI response text

        Args:
            text: Response text to display
            streaming: If True, update caption instead of full screen
        """
        if streaming and self.caption_enabled:
            # Show as live caption at bottom
            self.show_caption(text)
        else:
            # Show as full screen text
            self.display.show_text(
                text=text,
                font_size="medium",
                color=(0, 255, 150),
                background=(0, 0, 20),
                clear_screen=True
            )

    def show_caption(self, text: str):
        """
        Show live caption text (for transcription)

        Args:
            text: Caption text to display
        """
        if not self.caption_enabled:
            return

        self.caption_text = text
        self.current_mode = "caption"

        # Show caption overlay
        self.display.show_caption(
            text=text,
            position="bottom",
            background_alpha=0.8
        )

    def clear_caption(self):
        """Clear the caption display"""
        self.caption_text = ""
        self.show_status_display()

    def show_notification(
        self,
        title: str,
        message: str,
        type: str = "info",
        duration: float = 3.0,
        queue: bool = True
    ):
        """
        Show a notification

        Args:
            title: Notification title
            message: Notification message
            type: "info", "warning", "error", "success"
            duration: Display duration in seconds
            queue: If True, queue notification if one is showing
        """
        notification = {
            'title': title,
            'message': message,
            'type': type,
            'duration': duration
        }

        if self.current_mode == "notification" and queue:
            # Queue the notification
            self.notification_queue.append(notification)
            logger.debug(f"Queued notification: {title}")
        else:
            # Show immediately
            self._display_notification(notification)

    def _display_notification(self, notification: Dict):
        """Display a notification"""
        self.current_mode = "notification"

        self.display.show_notification(
            title=notification['title'],
            message=notification['message'],
            icon=notification['type'],
            duration=notification['duration']
        )

        # Process next queued notification
        if self.notification_queue:
            next_notification = self.notification_queue.pop(0)
            self._display_notification(next_notification)
        else:
            # Return to status display
            self.show_status_display()

    def show_photo_capture(self):
        """Show photo capture animation"""
        # Flash white
        self.display.clear(color=(255, 255, 255))
        time.sleep(0.1)

        # Show "Photo Captured" message
        self.show_notification(
            title="Photo",
            message="Captured!",
            type="success",
            duration=1.5,
            queue=False
        )

    def show_video_recording(self, recording: bool):
        """
        Show video recording indicator

        Args:
            recording: True if recording, False if stopped
        """
        if recording:
            # Show red recording dot
            self.display.show_text(
                text="● REC",
                font_size="large",
                color=(255, 0, 0),
                background=(0, 0, 0),
                x=10,
                y=10,
                align="left",
                clear_screen=False
            )
        else:
            self.show_notification(
                title="Video",
                message="Recording saved!",
                type="success",
                duration=2.0,
                queue=False
            )

    def show_menu(self, title: str, items: List[str], selected: int = 0):
        """
        Show a menu

        Args:
            title: Menu title
            items: List of menu items
            selected: Currently selected item index
        """
        self.current_mode = "menu"
        self.display.show_list(
            title=title,
            items=items,
            selected_index=selected
        )

    def show_notes_list(self, notes: List[Dict]):
        """
        Show notes list

        Args:
            notes: List of note dicts with 'content' and 'timestamp'
        """
        items = [note['content'][:30] + "..." if len(note['content']) > 30 else note['content']
                 for note in notes]

        self.show_menu(
            title="Notes",
            items=items if items else ["No notes"],
            selected=0
        )

    def show_todos_list(self, todos: List[Dict]):
        """
        Show todos list

        Args:
            todos: List of todo dicts with 'task' and 'completed'
        """
        items = []
        for todo in todos:
            prefix = "✓ " if todo.get('completed') else "○ "
            items.append(prefix + todo['task'])

        self.show_menu(
            title="Todos",
            items=items if items else ["No todos"],
            selected=0
        )

    def show_conversation_history(self, messages: List[Dict]):
        """
        Show conversation history

        Args:
            messages: List of message dicts with 'role' and 'content'
        """
        items = []
        for msg in messages:
            role = "You" if msg['role'] == 'user' else "AI"
            content = msg['content'][:25] + "..." if len(msg['content']) > 25 else msg['content']
            items.append(f"{role}: {content}")

        self.show_menu(
            title="Conversation",
            items=items if items else ["No messages"],
            selected=0
        )

    def show_translation(self, original: str, translated: str, source_lang: str, target_lang: str):
        """
        Show translation result

        Args:
            original: Original text
            translated: Translated text
            source_lang: Source language code
            target_lang: Target language code
        """
        self.display.clear(color=(0, 20, 40))

        # Show original at top
        self.display.show_text(
            text=f"{source_lang.upper()}: {original}",
            font_size="small",
            color=(150, 150, 150),
            background=(0, 20, 40),
            y=20,
            clear_screen=False
        )

        # Show translation in middle
        self.display.show_text(
            text=translated,
            font_size="large",
            color=(0, 255, 150),
            align="center",
            clear_screen=False
        )

        # Show target language at bottom
        self.display.show_text(
            text=f"→ {target_lang.upper()}",
            font_size="small",
            color=(100, 100, 255),
            background=(0, 20, 40),
            y=self.display.height - 30,
            clear_screen=False
        )

    def show_battery_warning(self, level: int):
        """Show low battery warning"""
        if level <= 20:
            self.show_notification(
                title="Low Battery",
                message=f"{level}% remaining",
                type="warning",
                duration=3.0
            )
        elif level <= 10:
            self.show_notification(
                title="Critical Battery",
                message=f"{level}% - Charge soon!",
                type="error",
                duration=5.0
            )

    def show_connection_status(self, connected: bool, type: str = "WiFi"):
        """Show connection status change"""
        if connected:
            self.show_notification(
                title="Connected",
                message=f"{type} connected",
                type="success",
                duration=2.0
            )
        else:
            self.show_notification(
                title="Disconnected",
                message=f"{type} disconnected",
                type="warning",
                duration=2.0
            )

    def show_error(self, message: str):
        """Show error message"""
        self.show_notification(
            title="Error",
            message=message,
            type="error",
            duration=3.0
        )

    def show_sleep_mode(self):
        """Show sleep mode screen"""
        self.update_status(mode="sleep")
        self.display.show_text(
            text="SLEEP MODE\n\nSay wake word\nto activate",
            font_size="medium",
            color=(100, 100, 100),
            background=(0, 0, 0),
            align="center",
            clear_screen=True
        )

        # Dim display after showing message
        time.sleep(2)
        self.display.turn_off()

    def wake_from_sleep(self):
        """Wake from sleep mode"""
        self.update_status(mode="active")
        self.display.turn_on()
        self.show_status_display()

    def enable_captions(self, enabled: bool):
        """Enable or disable live captions"""
        self.caption_enabled = enabled
        logger.info(f"Captions {'enabled' if enabled else 'disabled'}")

    def cleanup(self):
        """Cleanup HUD overlay"""
        logger.info("Cleaning up HUD overlay...")
        self.display.cleanup()
