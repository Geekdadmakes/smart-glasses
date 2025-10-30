"""
Speech Recognition - Converts speech to text
"""

import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Handles speech-to-text recognition"""

    def __init__(self, config):
        """Initialize speech recognizer"""
        self.config = config
        self.engine = config.get('engine', 'vosk')
        self.language = config.get('language', 'en-US')
        self.timeout = config.get('timeout', 5)
        self.phrase_time_limit = config.get('phrase_time_limit', 10)

        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True

        logger.info(f"Speech Recognizer initialized - engine: {self.engine}")

    def listen(self):
        """
        Listen for speech and convert to text
        Returns the recognized text or None
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening for speech...")

                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=self.phrase_time_limit
                )

                # Recognize speech
                text = self.recognize_speech(audio)
                return text

        except sr.WaitTimeoutError:
            logger.warning("Listening timed out")
            return None
        except Exception as e:
            logger.error(f"Error listening for speech: {e}")
            return None

    def recognize_speech(self, audio):
        """Recognize speech from audio data"""
        try:
            if self.engine == 'google':
                # Use Google Speech Recognition (requires internet)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized (Google): {text}")
                return text

            elif self.engine == 'vosk':
                # Use Vosk (offline, requires model download)
                # TODO: Setup Vosk model
                logger.warning("Vosk not yet implemented, falling back to Google")
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized (Google fallback): {text}")
                return text

            else:
                logger.error(f"Unknown recognition engine: {self.engine}")
                return None

        except sr.UnknownValueError:
            logger.warning("Speech not understood")
            return None
        except sr.RequestError as e:
            logger.error(f"Recognition service error: {e}")
            return None
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            return None


# TODO: Setup Vosk for offline speech recognition
# Download model from: https://alphacephei.com/vosk/models
# Recommended: vosk-model-small-en-us-0.15 (40MB) for Pi Zero
