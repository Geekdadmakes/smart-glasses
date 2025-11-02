"""
Text-to-Speech Manager - Enhanced TTS with multiple voice options
"""

import os
import logging
import subprocess
import pyttsx3
from pathlib import Path

logger = logging.getLogger(__name__)


class TTSManager:
    """Enhanced text-to-speech manager with personality-matched voices"""

    def __init__(self, config, personality='friendly'):
        """Initialize TTS manager"""
        self.config = config
        self.personality = personality
        self.engine_type = config.get('engine', 'pyttsx3')
        self.rate = config.get('rate', 150)
        self.volume = config.get('volume', 0.9)

        # Initialize engine
        self.engine = None
        self._initialize_engine()

        # Track current playback process for interruption
        self.current_playback_process = None

        logger.info(f"TTS Manager initialized - engine: {self.engine_type}, personality: {personality}")

    def _initialize_engine(self):
        """Initialize the TTS engine"""
        try:
            if self.engine_type == 'pyttsx3':
                self.engine = pyttsx3.init()
                self._configure_pyttsx3()
            elif self.engine_type == 'gtts':
                # Google TTS (requires internet)
                # Will be initialized per-request
                pass
            elif self.engine_type == 'elevenlabs':
                # ElevenLabs (premium, very natural)
                # Requires API key
                pass
            else:
                logger.warning(f"Unknown TTS engine: {self.engine_type}, using pyttsx3")
                self.engine = pyttsx3.init()
                self._configure_pyttsx3()

        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            # Fallback to basic pyttsx3
            self.engine = pyttsx3.init()

    def _configure_pyttsx3(self):
        """Configure pyttsx3 based on personality"""
        try:
            # Voice selection based on personality
            voices = self.engine.getProperty('voices')

            # Personality voice mapping
            voice_preferences = {
                'friendly': {
                    'gender': 'female',
                    'rate': 160,
                    'pitch': 1.1
                },
                'professional': {
                    'gender': 'male',
                    'rate': 150,
                    'pitch': 1.0
                },
                'witty': {
                    'gender': 'male',
                    'rate': 170,
                    'pitch': 1.15
                },
                'jarvis': {
                    'gender': 'male',
                    'rate': 145,
                    'pitch': 0.95,
                    'prefer': 'british'
                },
                'casual': {
                    'gender': 'female',
                    'rate': 165,
                    'pitch': 1.05
                }
            }

            prefs = voice_preferences.get(self.personality, voice_preferences['friendly'])

            # Try to find matching voice
            selected_voice = None

            # First, try to find preferred voice
            if 'prefer' in prefs:
                for voice in voices:
                    if prefs['prefer'].lower() in voice.name.lower():
                        selected_voice = voice.id
                        logger.info(f"Selected preferred voice: {voice.name}")
                        break

            # If no preferred, match by gender
            if not selected_voice:
                preferred_gender = prefs.get('gender', 'female')
                for voice in voices:
                    # Check gender in voice name or ID
                    if preferred_gender in voice.name.lower() or preferred_gender in voice.id.lower():
                        selected_voice = voice.id
                        logger.info(f"Selected voice by gender: {voice.name}")
                        break

            # Use default if still not found
            if not selected_voice and voices:
                selected_voice = voices[0].id
                logger.info(f"Using default voice: {voices[0].name}")

            # Apply voice
            if selected_voice:
                self.engine.setProperty('voice', selected_voice)

            # Set rate and volume
            rate = prefs.get('rate', self.rate)
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', self.volume)

            logger.info(f"TTS configured - rate: {rate}, volume: {self.volume}")

        except Exception as e:
            logger.error(f"Error configuring pyttsx3: {e}")

    def speak(self, text):
        """Convert text to speech and play it"""
        try:
            if self.engine_type == 'pyttsx3':
                self._speak_pyttsx3(text)
            elif self.engine_type == 'gtts':
                self._speak_gtts(text)
            elif self.engine_type == 'elevenlabs':
                self._speak_elevenlabs(text)
            else:
                logger.error(f"Unknown engine type: {self.engine_type}")

        except Exception as e:
            logger.error(f"TTS error: {e}")

    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        logger.info(f"Speaking (pyttsx3): {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def _speak_gtts(self, text):
        """Speak using Google TTS (requires internet)"""
        try:
            from gtts import gTTS
            import tempfile

            logger.info(f"Speaking (gTTS): {text}")

            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name

            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(temp_file)

            # Play audio using mpg123 - use Popen so we can interrupt
            self.current_playback_process = subprocess.Popen(
                ['mpg123', '-q', temp_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for completion
            self.current_playback_process.wait()
            self.current_playback_process = None

            # Cleanup
            os.remove(temp_file)

        except Exception as e:
            logger.error(f"gTTS error: {e}")
            # Fallback to pyttsx3
            self._speak_pyttsx3(text)

    def _speak_elevenlabs(self, text):
        """Speak using ElevenLabs API (premium)"""
        try:
            from elevenlabs import generate, play, set_api_key, Voice, VoiceSettings
            import tempfile

            # Get API key
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                logger.error("ELEVENLABS_API_KEY not found in environment")
                self._speak_pyttsx3(text)
                return

            set_api_key(api_key)

            # Get voice ID for personality
            voice_id = self._get_elevenlabs_voice_id()

            logger.info(f"Speaking (ElevenLabs): {text}")

            # Generate audio with voice settings
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id=voice_id,
                    settings=VoiceSettings(
                        stability=0.5,
                        similarity_boost=0.75,
                        style=0.0,
                        use_speaker_boost=True
                    )
                ),
                model="eleven_monolingual_v1"  # or eleven_multilingual_v2 for other languages
            )

            # Save audio to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
                fp.write(audio)

            # Play audio using mpg123 (more reliable on Pi)
            subprocess.run(['mpg123', '-q', temp_file], check=False)

            # Cleanup
            os.remove(temp_file)

        except ImportError:
            logger.error("elevenlabs library not installed. Install with: pip install elevenlabs")
            self._speak_pyttsx3(text)
        except Exception as e:
            logger.error(f"ElevenLabs error: {e}")
            logger.info("Falling back to pyttsx3")
            self._speak_pyttsx3(text)

    def _get_elevenlabs_voice_id(self):
        """Get ElevenLabs voice ID based on personality"""
        # Personality to voice ID mapping
        # You can customize these with your preferred ElevenLabs voices

        personality_voices = {
            'friendly': os.getenv('ELEVENLABS_VOICE_FRIENDLY', 'EXAVITQu4vr4xnSDxMaL'),  # Bella
            'professional': os.getenv('ELEVENLABS_VOICE_PROFESSIONAL', 'pNInz6obpgDQGcFmaJgB'),  # Adam
            'witty': os.getenv('ELEVENLABS_VOICE_WITTY', 'TxGEqnHWrfWFTfGW9XjX'),  # Josh
            'jarvis': os.getenv('ELEVENLABS_VOICE_JARVIS', 'VR6AewLTigWG4xSOukaG'),  # Arnold (British)
            'casual': os.getenv('ELEVENLABS_VOICE_CASUAL', 'jsCqWAovK2LkecY7zXl4'),  # Freya
        }

        voice_id = personality_voices.get(self.personality)

        if not voice_id:
            logger.warning(f"No voice ID for personality '{self.personality}', using default")
            voice_id = 'pNInz6obpgDQGcFmaJgB'  # Adam as default

        logger.info(f"Using ElevenLabs voice ID: {voice_id} for personality: {self.personality}")
        return voice_id

    def set_rate(self, rate):
        """Set speaking rate (words per minute)"""
        self.rate = rate
        if self.engine_type == 'pyttsx3':
            self.engine.setProperty('rate', rate)
        logger.info(f"TTS rate set to {rate}")

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.engine_type == 'pyttsx3':
            self.engine.setProperty('volume', self.volume)
        logger.info(f"TTS volume set to {self.volume}")

    def list_voices(self):
        """List available voices"""
        if self.engine_type == 'pyttsx3':
            voices = self.engine.getProperty('voices')
            logger.info("Available voices:")
            for idx, voice in enumerate(voices):
                logger.info(f"  [{idx}] {voice.name} ({voice.id})")
                logger.info(f"      Languages: {voice.languages}")
                logger.info(f"      Gender: {voice.gender if hasattr(voice, 'gender') else 'unknown'}")
            return voices
        return []

    def stop_speaking(self):
        """Stop current speech playback"""
        if self.current_playback_process:
            try:
                self.current_playback_process.terminate()
                self.current_playback_process.wait(timeout=1)
                self.current_playback_process = None
                logger.info("Speech playback interrupted")
                return True
            except Exception as e:
                logger.error(f"Error stopping playback: {e}")
        return False

    def cleanup(self):
        """Cleanup TTS resources"""
        logger.info("Cleaning up TTS manager")

        # Stop any ongoing playback
        self.stop_speaking()

        if self.engine and self.engine_type == 'pyttsx3':
            try:
                self.engine.stop()
            except:
                pass


# Voice personality recommendations:
#
# JARVIS personality:
# - British English voice if available
# - Slightly slower rate (145 WPM)
# - Lower pitch
# - Professional tone
#
# FRIENDLY personality:
# - Warm, upbeat voice
# - Medium-fast rate (160 WPM)
# - Slightly higher pitch
#
# PROFESSIONAL personality:
# - Clear, neutral voice
# - Standard rate (150 WPM)
# - Neutral pitch
#
# For best results on Raspberry Pi:
# - Use pyttsx3 (offline, lightweight)
# - Download additional voices: sudo apt-get install espeak-ng
# - For premium voices, consider using ElevenLabs API (cloud-based)
