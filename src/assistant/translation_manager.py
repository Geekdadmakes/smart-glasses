"""
Translation Manager - Text translation, speech translation, language detection
"""

import logging
import requests

logger = logging.getLogger(__name__)


class TranslationManager:
    """Manage translation and language features"""

    def __init__(self):
        """Initialize translation manager"""
        logger.info("Translation Manager initialized")

    def translate_text(self, text, target_language, source_language='auto'):
        """Translate text using Google Translate (via googletrans library)"""
        try:
            from googletrans import Translator

            translator = Translator()

            # Translate
            result = translator.translate(
                text,
                src=source_language,
                dest=target_language
            )

            translated_text = result.text
            detected_lang = result.src

            response = f"Translation to {target_language}: {translated_text}"
            if source_language == 'auto' and detected_lang:
                response += f". Detected source language: {detected_lang}"

            logger.info(f"Translated '{text[:30]}...' from {detected_lang} to {target_language}")
            return response

        except ImportError:
            return "Translation requires 'googletrans' library. Install with: pip install googletrans==4.0.0-rc1"
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return f"Couldn't translate text: {str(e)}"

    def detect_language(self, text):
        """Detect language of text"""
        try:
            from googletrans import Translator, LANGUAGES

            translator = Translator()

            # Detect language
            detection = translator.detect(text)

            lang_code = detection.lang
            confidence = detection.confidence

            # Get language name
            lang_name = LANGUAGES.get(lang_code, lang_code)

            result = f"Detected language: {lang_name} ({lang_code})"
            if confidence:
                result += f", confidence: {confidence:.0%}"

            logger.info(f"Language detected: {lang_name} for '{text[:30]}...'")
            return result

        except ImportError:
            return "Language detection requires 'googletrans' library"
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return "Couldn't detect language"

    def translate_sign(self, vision_api_func, target_language, camera_manager=None):
        """Translate text from a sign/image"""
        if not camera_manager:
            return "Camera not available"

        # Take photo
        photo_path = camera_manager.take_photo()

        # Use vision API to read text
        read_prompt = "Extract and return ONLY the text visible in this image. If there are multiple text elements, separate them with newlines. Do not add any commentary."

        text_content = vision_api_func(photo_path, read_prompt)

        if not text_content or "no text" in text_content.lower():
            return "No text detected in image"

        # Translate the extracted text
        translation_result = self.translate_text(text_content, target_language)

        logger.info(f"Sign translated to {target_language}")
        return f"Text from image: {text_content}. {translation_result}"

    def get_supported_languages(self):
        """Get list of supported languages"""
        try:
            from googletrans import LANGUAGES

            # Get common languages
            common_langs = {
                'en': 'English',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ru': 'Russian',
                'ja': 'Japanese',
                'ko': 'Korean',
                'zh-cn': 'Chinese (Simplified)',
                'zh-tw': 'Chinese (Traditional)',
                'ar': 'Arabic',
                'hi': 'Hindi',
                'nl': 'Dutch',
                'pl': 'Polish',
                'tr': 'Turkish',
                'vi': 'Vietnamese',
                'th': 'Thai',
                'sv': 'Swedish',
                'no': 'Norwegian'
            }

            result = "Common supported languages: "
            result += ", ".join([f"{name} ({code})" for code, name in list(common_langs.items())[:10]])
            result += f". Plus {len(LANGUAGES) - len(common_langs)} more languages available."

            return result

        except ImportError:
            return "Language list requires 'googletrans' library"
        except Exception as e:
            logger.error(f"Error getting languages: {e}")
            return "Couldn't get language list"

    def say_phrase_in_language(self, phrase, language):
        """Translate and return a common phrase in target language"""
        try:
            # Common phrases dictionary
            common_phrases = {
                'hello': 'Hello',
                'goodbye': 'Goodbye',
                'please': 'Please',
                'thank you': 'Thank you',
                'yes': 'Yes',
                'no': 'No',
                'excuse me': 'Excuse me',
                'sorry': 'I am sorry',
                'help': 'Help',
                'where is': 'Where is',
                'how much': 'How much',
                'good morning': 'Good morning',
                'good night': 'Good night',
                'my name is': 'My name is',
                'nice to meet you': 'Nice to meet you',
                'do you speak english': 'Do you speak English?',
                'i dont understand': 'I don\'t understand',
                'bathroom': 'Where is the bathroom?',
                'water': 'Water',
                'food': 'Food',
                'bill': 'The bill, please'
            }

            # Find matching phrase
            phrase_lower = phrase.lower()
            english_text = common_phrases.get(phrase_lower, phrase)

            # Translate
            result = self.translate_text(english_text, language, source_language='en')

            logger.info(f"Phrase '{phrase}' translated to {language}")
            return result

        except Exception as e:
            logger.error(f"Phrase translation error: {e}")
            return "Couldn't translate phrase"

    def romanize_text(self, text, source_language):
        """Convert non-Latin script to romanized version"""
        try:
            from googletrans import Translator

            translator = Translator()

            # Translate to get romanization
            result = translator.translate(text, src=source_language, dest='en')

            if hasattr(result, 'pronunciation') and result.pronunciation:
                romanized = result.pronunciation
                return f"Romanization: {romanized}"
            else:
                return f"Original: {text}. Romanization not available."

        except ImportError:
            return "Romanization requires 'googletrans' library"
        except Exception as e:
            logger.error(f"Romanization error: {e}")
            return "Couldn't romanize text"
