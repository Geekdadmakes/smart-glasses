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
        self.bluetooth_manager = BluetoothManager(
            self.config.get('bluetooth', {}),
            camera_manager=self.camera_manager
        )
        self.ai_assistant = AIAssistant(
            self.config['assistant'],
            camera_manager=self.camera_manager,
            bluetooth_manager=self.bluetooth_manager
        )

        # State
        self.running = False
        self.listening = False

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
        """Main application loop"""
        logger.info("Entering main loop - listening for wake word...")

        while self.running:
            try:
                # Listen for wake word
                if self.wake_word_detector.detect():
                    logger.info("Wake word detected!")
                    self.audio_manager.play_activation_sound()

                    # Process voice command
                    self.process_voice_command()

                # Small delay to prevent CPU overload
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)

    def process_voice_command(self):
        """Process a voice command after wake word detection"""
        try:
            # Listen for command
            logger.info("Listening for command...")
            command = self.speech_recognizer.listen()

            if not command:
                logger.info("No command heard")
                self.audio_manager.play_error_sound()
                return

            logger.info(f"Command received: {command}")

            # Check for special commands first
            if self.handle_special_command(command):
                return

            # Send to AI assistant
            logger.info("Processing with AI assistant...")
            response = self.ai_assistant.process(command)

            # Speak the response
            self.audio_manager.speak(response)

        except Exception as e:
            logger.error(f"Error processing voice command: {e}", exc_info=True)
            self.audio_manager.speak("Sorry, I encountered an error.")

    def handle_special_command(self, command):
        """Handle special commands like taking photos, etc."""
        command_lower = command.lower()

        # Photo command
        if "take a photo" in command_lower or "take photo" in command_lower:
            logger.info("Taking photo...")
            self.audio_manager.speak("Taking photo")
            photo_path = self.camera_manager.take_photo()
            self.audio_manager.speak(f"Photo saved")
            return True

        # Video command
        elif "record video" in command_lower or "start recording" in command_lower:
            logger.info("Recording video...")
            self.audio_manager.speak("Recording video")
            video_path = self.camera_manager.record_video(duration=10)
            self.audio_manager.speak("Video saved")
            return True

        # Shutdown command
        elif "shutdown" in command_lower or "turn off" in command_lower:
            logger.info("Shutdown requested")
            self.audio_manager.speak("Shutting down")
            self.stop()
            return True

        return False

    def stop(self):
        """Stop the smart glasses system"""
        logger.info("Stopping Smart Glasses...")
        self.running = False

        # Cleanup
        if hasattr(self, 'audio_manager'):
            self.audio_manager.cleanup()
        if hasattr(self, 'wake_word_detector'):
            self.wake_word_detector.cleanup()
        if hasattr(self, 'camera_manager'):
            self.camera_manager.cleanup()

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
