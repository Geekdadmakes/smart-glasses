"""
Wake Word Detection - Detects wake words to activate the glasses

Supports multiple detection methods:
1. Porcupine (Picovoice) - Recommended, requires free API key
2. Energy-based detection - Simple fallback for testing
3. Vosk - Open source alternative (requires model download)
"""

import os
import logging
import struct
import pyaudio
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Detects wake words to activate voice commands"""

    def __init__(self, config, audio_config=None):
        """Initialize wake word detector"""
        self.config = config
        self.audio_config = audio_config or {}

        self.enabled = config.get('enabled', True)
        self.keyword = config.get('keyword', 'hey glasses')
        self.sensitivity = config.get('sensitivity', 0.5)
        self.method = config.get('method', 'porcupine')  # porcupine, energy, vosk

        # Audio parameters
        self.sample_rate = self.audio_config.get('sample_rate', 16000)
        self.channels = self.audio_config.get('channels', 1)
        self.chunk_size = self.audio_config.get('chunk_size', 512)

        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None

        # Detector
        self.detector = None
        self.detector_initialized = False

        # Initialize detection method
        self._initialize_detector()

        logger.info(f"Wake Word Detector initialized - method: {self.method}, keyword: '{self.keyword}'")

    def _initialize_detector(self):
        """Initialize the selected detection method"""
        try:
            if self.method == 'porcupine':
                self._initialize_porcupine()
            elif self.method == 'vosk':
                self._initialize_vosk()
            elif self.method == 'energy':
                self._initialize_energy_detector()
            else:
                logger.warning(f"Unknown method '{self.method}', falling back to energy detection")
                self.method = 'energy'
                self._initialize_energy_detector()

        except Exception as e:
            logger.error(f"Failed to initialize {self.method} detector: {e}")
            logger.info("Falling back to energy-based detection")
            self.method = 'energy'
            self._initialize_energy_detector()

    def _initialize_porcupine(self):
        """Initialize Porcupine wake word detector"""
        try:
            import pvporcupine

            # Get access key from environment
            access_key = os.getenv('PORCUPINE_ACCESS_KEY')

            if not access_key:
                raise ValueError("PORCUPINE_ACCESS_KEY not found in environment variables")

            # Built-in keywords for Porcupine
            # Available: alexa, americano, blueberry, bumblebee, computer, grapefruit,
            #            grasshopper, hey google, hey siri, jarvis, ok google, picovoice,
            #            porcupine, terminator

            # Map custom keywords to built-in ones
            keyword_map = {
                'hey glasses': 'computer',
                'hey jarvis': 'jarvis',
                'ok google': 'ok google',
                'hey google': 'hey google',
                'alexa': 'alexa',
                'computer': 'computer',
                'porcupine': 'porcupine'
            }

            keyword_lower = self.keyword.lower()
            porcupine_keyword = keyword_map.get(keyword_lower, 'computer')

            logger.info(f"Using Porcupine keyword: '{porcupine_keyword}' for '{self.keyword}'")

            # Initialize Porcupine
            self.detector = pvporcupine.create(
                access_key=access_key,
                keywords=[porcupine_keyword],
                sensitivities=[self.sensitivity]
            )

            # Update audio parameters to match Porcupine requirements
            self.sample_rate = self.detector.sample_rate
            self.chunk_size = self.detector.frame_length

            self.detector_initialized = True
            logger.info("Porcupine wake word detector initialized successfully")

        except ImportError:
            raise Exception("pvporcupine not installed. Install with: pip install pvporcupine")
        except Exception as e:
            raise Exception(f"Failed to initialize Porcupine: {e}")

    def _initialize_vosk(self):
        """Initialize Vosk wake word detector"""
        try:
            from vosk import Model, KaldiRecognizer

            # Check for model
            model_path = os.getenv('VOSK_MODEL_PATH', 'models/vosk-model-small-en-us-0.15')

            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Vosk model not found at {model_path}")

            # Initialize Vosk
            model = Model(model_path)
            self.detector = KaldiRecognizer(model, self.sample_rate)
            self.detector.SetWords(True)

            self.detector_initialized = True
            logger.info("Vosk wake word detector initialized successfully")

        except ImportError:
            raise Exception("vosk not installed. Install with: pip install vosk")
        except Exception as e:
            raise Exception(f"Failed to initialize Vosk: {e}")

    def _initialize_energy_detector(self):
        """Initialize simple energy-based detector"""
        # Energy threshold for detection
        self.energy_threshold = 3000
        self.energy_samples = []
        self.max_energy_samples = 5

        self.detector_initialized = True
        logger.info("Energy-based wake word detector initialized")
        logger.warning("Energy detection is for testing only - use Porcupine for production")

    def detect(self):
        """
        Detect wake word from audio input
        Returns True if wake word is detected
        """
        if not self.enabled or not self.detector_initialized:
            return False

        try:
            # Get audio stream if not already open
            if not self.stream or not self.stream.is_active():
                self._open_stream()

            # Read audio frame
            audio_frame = self.stream.read(self.chunk_size, exception_on_overflow=False)

            # Detect based on method
            if self.method == 'porcupine':
                return self._detect_porcupine(audio_frame)
            elif self.method == 'vosk':
                return self._detect_vosk(audio_frame)
            elif self.method == 'energy':
                return self._detect_energy(audio_frame)

        except Exception as e:
            logger.error(f"Error during wake word detection: {e}")
            return False

        return False

    def _open_stream(self):
        """Open audio input stream"""
        try:
            if self.stream and self.stream.is_active():
                self.stream.close()

            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.audio_config.get('mic_device_index')
            )

            logger.debug("Audio stream opened for wake word detection")

        except Exception as e:
            logger.error(f"Failed to open audio stream: {e}")
            raise

    def _detect_porcupine(self, audio_frame):
        """Detect using Porcupine"""
        try:
            # Convert audio to required format
            pcm = struct.unpack_from("h" * self.chunk_size, audio_frame)

            # Process with Porcupine
            keyword_index = self.detector.process(pcm)

            if keyword_index >= 0:
                logger.info(f"Wake word detected! (Porcupine)")
                return True

        except Exception as e:
            logger.error(f"Porcupine detection error: {e}")

        return False

    def _detect_vosk(self, audio_frame):
        """Detect using Vosk"""
        try:
            if self.detector.AcceptWaveform(audio_frame):
                result = self.detector.Result()

                # Check if keyword is in result
                if self.keyword.lower() in result.lower():
                    logger.info(f"Wake word detected! (Vosk)")
                    return True

        except Exception as e:
            logger.error(f"Vosk detection error: {e}")

        return False

    def _detect_energy(self, audio_frame):
        """Detect using simple energy threshold"""
        try:
            # Convert to numpy array
            audio_data = np.frombuffer(audio_frame, dtype=np.int16)

            # Calculate RMS energy
            energy = np.sqrt(np.mean(audio_data**2))

            # Track energy samples
            self.energy_samples.append(energy)
            if len(self.energy_samples) > self.max_energy_samples:
                self.energy_samples.pop(0)

            # Simple detection: if energy exceeds threshold
            if energy > self.energy_threshold:
                # Calculate average energy
                avg_energy = np.mean(self.energy_samples)

                # If current energy is significantly higher than average
                if energy > avg_energy * 2:
                    logger.info(f"Wake word detected! (Energy: {energy:.0f})")
                    # Clear samples to prevent immediate re-triggering
                    self.energy_samples = []
                    return True

        except Exception as e:
            logger.error(f"Energy detection error: {e}")

        return False

    def set_sensitivity(self, sensitivity):
        """Update detection sensitivity (0.0 to 1.0)"""
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        logger.info(f"Sensitivity updated to {self.sensitivity}")

        # Reinitialize if using Porcupine
        if self.method == 'porcupine' and self.detector:
            self.cleanup()
            self._initialize_porcupine()

    def cleanup(self):
        """Cleanup detector resources"""
        logger.info("Cleaning up wake word detector")

        # Close audio stream
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        # Cleanup detector
        if self.detector:
            if self.method == 'porcupine':
                try:
                    self.detector.delete()
                except:
                    pass
            self.detector = None

        # Terminate PyAudio
        if self.audio:
            self.audio.terminate()


# Setup Instructions:
#
# For Porcupine (Recommended):
# 1. Sign up for free access key at https://console.picovoice.ai/
# 2. Add to .env: PORCUPINE_ACCESS_KEY=your_key_here
# 3. Install: pip install pvporcupine
#
# For Vosk:
# 1. Download model from https://alphacephei.com/vosk/models
# 2. Extract to models/vosk-model-small-en-us-0.15/
# 3. Install: pip install vosk
#
# For Energy (Testing only):
# - No setup needed, works out of the box
# - Very simple, prone to false positives
# - Use for testing audio setup only
