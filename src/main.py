#!/usr/bin/env python3
"""
Smart Glasses - Main Application
Voice-activated smart glasses with AI assistant capabilities
"""

import os
import sys
import time
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

# Import our modules
from audio.audio_manager import AudioManager
from audio.tts_manager import TTSManager
from audio.wake_word import WakeWordDetector
from audio.speech_recognition import SpeechRecognizer
from assistant.ai_assistant import AIAssistant
from camera.camera_manager import CameraManager
from bluetooth.bluetooth_manager import BluetoothManager
from connection.connection_manager import ConnectionManager
from display.display_manager import DisplayManager
from display.hud_overlay import HUDOverlay

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartGlasses:
    """Main application class for Smart Glasses"""

    def __init__(self, config_path='config/config.yaml'):
        """Initialize the smart glasses system"""
        logger.info("Initializing Smart Glasses...")

        # Load configuration
        self.config = self.load_config(config_path)

        # Initialize components
        # TTS with personality matching
        personality = self.config['assistant'].get('personality', 'friendly')
        self.tts_manager = TTSManager(self.config['tts'], personality=personality)

        self.audio_manager = AudioManager(
            self.config['audio'],
            tts_manager=self.tts_manager
        )
        self.wake_word_detector = WakeWordDetector(
            self.config['wake_word'],
            audio_config=self.config['audio']
        )
        self.speech_recognizer = SpeechRecognizer(self.config['speech'])
        self.camera_manager = CameraManager(self.config['camera'])

        # Display/HUD (1.8" LCD)
        self.display_manager = None
        self.hud_overlay = None
        if self.config.get('display', {}).get('enabled', False):
            try:
                logger.info("Initializing HUD display...")
                self.display_manager = DisplayManager(self.config['display'])
                self.hud_overlay = HUDOverlay(self.display_manager, self.config['display'])
                logger.info("HUD display initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize display (continuing without HUD): {e}")
                self.display_manager = None
                self.hud_overlay = None

        self.bluetooth_manager = BluetoothManager(
            self.config.get('bluetooth', {}),
            camera_manager=self.camera_manager
        )
        self.ai_assistant = AIAssistant(
            self.config['assistant'],
            camera_manager=self.camera_manager,
            bluetooth_manager=self.bluetooth_manager
        )

        # iOS Companion App - Connection Manager (BLE + WiFi)
        logger.info("Initializing iOS companion app connection manager...")
        managers_dict = {
            'audio_manager': self.audio_manager,
            'tts_manager': self.tts_manager,
            'camera_manager': self.camera_manager,
            'bluetooth_manager': self.bluetooth_manager,
            'ai_assistant': self.ai_assistant,
            'wake_word_detector': self.wake_word_detector,
            'speech_recognizer': self.speech_recognizer,
            'display_manager': self.display_manager,
            'hud_overlay': self.hud_overlay
        }

        # Add productivity manager and other managers if available
        if hasattr(self.ai_assistant, 'productivity_manager'):
            managers_dict['productivity_manager'] = self.ai_assistant.productivity_manager
        if hasattr(self.ai_assistant, 'security_manager'):
            managers_dict['security_manager'] = self.ai_assistant.security_manager

        self.connection_manager = ConnectionManager(managers=managers_dict)

        # State
        self.running = False
        self.listening = False
        self.active_mode = False  # True = always listening, False = wake word only
        self.last_activity_time = time.time()
        self.sleep_timeout = 60  # seconds of inactivity before returning to sleep

        logger.info("Smart Glasses initialized successfully")

    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def start(self):
        """Start the smart glasses system"""
        logger.info("Starting Smart Glasses...")
        self.running = True

        try:
            # Start iOS companion app connection manager (BLE + WiFi)
            logger.info("Starting iOS companion app servers...")
            self.connection_manager.start()

            # Play startup sound
            self.audio_manager.play_startup_sound()

            # Main loop
            self.run_main_loop()

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.stop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            self.stop()

    def run_main_loop(self):
        """Main application loop with SLEEP and ACTIVE modes"""
        logger.info("Entering main loop - listening for wake word...")

        # Show initial status on HUD
        if self.hud_overlay:
            self.hud_overlay.show_sleep_mode()

        while self.running:
            try:
                if not self.active_mode:
                    # SLEEP MODE: Wait for wake word
                    logger.debug("SLEEP mode - listening for wake word...")
                    if self.wake_word_detector.detect():
                        logger.info("Wake word detected! Entering ACTIVE mode...")
                        self.active_mode = True
                        self.last_activity_time = time.time()

                        # Show wake on HUD
                        if self.hud_overlay:
                            self.hud_overlay.wake_from_sleep()

                        self.audio_manager.speak("I'm listening")
                        # Continue to active mode
                    # Small delay in sleep mode
                    time.sleep(0.1)
                    continue  # Loop back to check wake word again

                if self.active_mode:
                    # ACTIVE MODE: Continuously listen for commands
                    # Check for sleep timeout
                    if time.time() - self.last_activity_time > self.sleep_timeout:
                        logger.info("Sleep timeout reached, returning to SLEEP mode")
                        self.active_mode = False
                        self.audio_manager.speak("Going to sleep")

                        # Show sleep mode on HUD
                        if self.hud_overlay:
                            self.hud_overlay.show_sleep_mode()

                        logger.info("Returning to SLEEP mode - wake word listening active")
                        continue

                    # Check display timeout
                    if self.display_manager:
                        self.display_manager.check_timeout()

                    # Listen for any speech
                    command = self.speech_recognizer.listen()

                    if command:
                        self.last_activity_time = time.time()

                        # Show listening mode on HUD
                        if self.hud_overlay:
                            self.hud_overlay.show_listening_mode()

                        self.process_voice_command(command)

                    # Small delay
                    time.sleep(0.2)

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)

    def process_voice_command(self, command):
        """Process a voice command"""
        try:
            if not command:
                return

            logger.info(f"Command received: {command}")

            # Strip wake word if present
            wake_words = ['computer', 'hey glasses', 'hey jarvis', 'jarvis']
            command_lower = command.lower()
            for wake_word in wake_words:
                if command_lower.startswith(wake_word):
                    command = command[len(wake_word):].strip()
                    logger.info(f"Stripped wake word, command is now: {command}")
                    break

            if not command:
                return

            # Show user command as caption
            if self.hud_overlay:
                self.hud_overlay.show_caption(f"You: {command}")

            # Check for sleep commands
            sleep_phrases = ['go to sleep', 'sleep mode', 'stop listening', 'goodbye', 'goodnight']
            if any(phrase in command_lower for phrase in sleep_phrases):
                logger.info("Sleep command detected")
                self.active_mode = False
                self.audio_manager.speak("Going to sleep. Say the wake word to wake me.", blocking=True)

                # Show sleep mode on HUD
                if self.hud_overlay:
                    self.hud_overlay.show_sleep_mode()

                return

            # Check for special commands
            if self.handle_special_command(command):
                return

            # Send to AI assistant
            logger.info("Processing with AI assistant...")
            response = self.ai_assistant.process(command)

            # Show AI response as caption
            if self.hud_overlay:
                self.hud_overlay.show_ai_response(response, streaming=True)

            # Speak the response (non-blocking for interruption)
            self.audio_manager.speak(response, blocking=False)

            # Monitor for interruptions while speaking
            self.listen_for_interruption()

            # Clear caption after response
            if self.hud_overlay:
                time.sleep(2)  # Let user read the response
                self.hud_overlay.clear_caption()

        except Exception as e:
            logger.error(f"Error processing voice command: {e}", exc_info=True)
            self.audio_manager.speak("Sorry, I encountered an error.", blocking=True)

    def listen_for_interruption(self):
        """Listen for speech while TTS is playing and interrupt if detected"""
        while self.audio_manager.is_speaking:
            try:
                # Quick check for speech (short timeout)
                command = self.speech_recognizer.listen()

                if command:
                    # Speech detected - interrupt!
                    logger.info(f"Interruption detected: {command}")
                    self.audio_manager.stop_speaking()
                    self.last_activity_time = time.time()

                    # Process the new command
                    self.process_voice_command(command)
                    break

            except Exception as e:
                logger.debug(f"Error during interruption check: {e}")

            # Small delay before next check
            time.sleep(0.1)

    def handle_special_command(self, command):
        """Handle special commands like taking photos, etc."""
        command_lower = command.lower()

        # Photo command
        if "take a photo" in command_lower or "take photo" in command_lower:
            logger.info("Taking photo...")
            self.audio_manager.speak("Taking photo", blocking=True)
            photo_path = self.camera_manager.take_photo()

            # Show photo capture on HUD
            if self.hud_overlay:
                self.hud_overlay.show_photo_capture()

            self.audio_manager.speak(f"Photo saved", blocking=True)
            return True

        # Video command
        elif "record video" in command_lower or "start recording" in command_lower:
            logger.info("Recording video...")
            self.audio_manager.speak("Recording video", blocking=True)

            # Show recording indicator on HUD
            if self.hud_overlay:
                self.hud_overlay.show_video_recording(True)

            video_path = self.camera_manager.record_video(duration=10)

            # Hide recording indicator
            if self.hud_overlay:
                self.hud_overlay.show_video_recording(False)

            self.audio_manager.speak("Video saved", blocking=True)
            return True

        # Shutdown command
        elif "shutdown" in command_lower or "turn off" in command_lower:
            logger.info("Shutdown requested")
            self.audio_manager.speak("Shutting down", blocking=True)
            self.stop()
            return True

        return False

    def stop(self):
        """Stop the smart glasses system"""
        logger.info("Stopping Smart Glasses...")
        self.running = False

        # Cleanup
        if hasattr(self, 'connection_manager'):
            logger.info("Stopping iOS companion app servers...")
            self.connection_manager.stop()
        if hasattr(self, 'audio_manager'):
            self.audio_manager.cleanup()
        if hasattr(self, 'wake_word_detector'):
            self.wake_word_detector.cleanup()
        if hasattr(self, 'camera_manager'):
            self.camera_manager.cleanup()
        if hasattr(self, 'hud_overlay'):
            logger.info("Cleaning up HUD display...")
            self.hud_overlay.cleanup()

        logger.info("Smart Glasses stopped")


def main():
    """Main entry point"""
    print("=" * 50)
    print("Smart Glasses - Voice-Activated AI Glasses")
    print("=" * 50)

    # Create smart glasses instance
    glasses = SmartGlasses()

    # Start the system
    glasses.start()


if __name__ == "__main__":
    main()
