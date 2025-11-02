"""
Audio Manager - Handles audio input/output for the smart glasses
"""

import pyaudio
import logging
import pyttsx3
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioManager:
    """Manages audio input and output"""

    def __init__(self, config, tts_manager=None):
        """Initialize audio manager"""
        self.config = config
        self.sample_rate = config.get('sample_rate', 16000)
        self.channels = config.get('channels', 1)
        self.chunk_size = config.get('chunk_size', 1024)

        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # Use provided TTS manager or create basic one
        self.tts_manager = tts_manager
        if not self.tts_manager:
            # Fallback to basic pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)

        # Track TTS playback state
        self.is_speaking = False
        self.speak_thread = None

        logger.info("Audio Manager initialized")

    def get_input_stream(self):
        """Get an input stream from the microphone"""
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.config.get('mic_device_index')
            )
            return stream
        except Exception as e:
            logger.error(f"Failed to open input stream: {e}")
            return None

    def get_output_stream(self):
        """Get an output stream to the speaker"""
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                output_device_index=self.config.get('speaker_device_index')
            )
            return stream
        except Exception as e:
            logger.error(f"Failed to open output stream: {e}")
            return None

    def speak(self, text, blocking=False):
        """Convert text to speech and play it"""
        try:
            logger.info(f"Speaking: {text}")

            if blocking:
                # Blocking mode - wait for speech to finish
                self._speak_blocking(text)
            else:
                # Non-blocking mode - run in thread for interruption
                self.stop_speaking()  # Stop any ongoing speech first
                self.is_speaking = True
                self.speak_thread = threading.Thread(target=self._speak_blocking, args=(text,))
                self.speak_thread.daemon = True
                self.speak_thread.start()

        except Exception as e:
            logger.error(f"TTS error: {e}")
            self.is_speaking = False

    def _speak_blocking(self, text):
        """Internal method to speak (blocking)"""
        try:
            if self.tts_manager:
                self.tts_manager.speak(text)
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
        finally:
            self.is_speaking = False

    def stop_speaking(self):
        """Stop current speech playback"""
        if self.is_speaking and self.tts_manager:
            logger.info("Interrupting speech...")
            self.tts_manager.stop_speaking()
            self.is_speaking = False
            if self.speak_thread:
                self.speak_thread.join(timeout=0.5)

    def play_startup_sound(self):
        """Play startup sound"""
        self.speak("Smart glasses ready")

    def play_activation_sound(self):
        """Play activation sound when wake word is detected"""
        # Could use a short beep sound here
        logger.info("Playing activation sound")

    def play_error_sound(self):
        """Play error sound"""
        logger.info("Playing error sound")

    def list_audio_devices(self):
        """List all available audio devices"""
        logger.info("Available audio devices:")
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            logger.info(f"  [{i}] {info['name']}")
            logger.info(f"      Inputs: {info['maxInputChannels']}, Outputs: {info['maxOutputChannels']}")

    def cleanup(self):
        """Cleanup audio resources"""
        logger.info("Cleaning up audio manager")

        # Stop any ongoing speech
        self.stop_speaking()

        if self.tts_manager:
            self.tts_manager.cleanup()
        elif hasattr(self, 'tts_engine'):
            self.tts_engine.stop()
        if hasattr(self, 'audio'):
            self.audio.terminate()
