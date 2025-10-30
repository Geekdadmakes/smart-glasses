"""
OCR (Optical Character Recognition) - Read text from images
"""

import logging
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


class OCRReader:
    """Reads text from images using OCR"""

    def __init__(self, config):
        """Initialize OCR reader"""
        self.config = config
        self.enabled = config.get('ocr', False)
        self.language = 'eng'  # Default language

        logger.info("OCR Reader initialized")

    def read_text(self, image_path):
        """
        Extract text from an image
        Returns the recognized text
        """
        if not self.enabled:
            logger.warning("OCR not enabled")
            return None

        try:
            # Open image
            image = Image.open(image_path)

            # Perform OCR
            text = pytesseract.image_to_string(image, lang=self.language)

            logger.info(f"Extracted text: {text[:100]}...")
            return text.strip()

        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return None

    def read_text_from_camera(self, camera_manager):
        """
        Take a photo and read text from it
        """
        try:
            # Take photo
            photo_path = camera_manager.take_photo()

            if photo_path:
                # Read text from photo
                text = self.read_text(photo_path)
                return text
            else:
                return None

        except Exception as e:
            logger.error(f"Error reading text from camera: {e}")
            return None

    def translate_text(self, text, target_language='es'):
        """
        Translate extracted text
        (Placeholder for future translation feature)
        """
        # TODO: Integrate translation API
        # Options: Google Translate API, DeepL, etc.
        logger.warning("Translation not yet implemented")
        return text


# TODO: Setup Tesseract OCR
# Installation on Raspberry Pi:
# sudo apt-get install tesseract-ocr
# sudo apt-get install tesseract-ocr-[lang]  # for additional languages
#
# For better performance on Pi Zero:
# - Pre-process images (resize, enhance contrast)
# - Use specific language data files only
# - Consider using lighter OCR alternatives for real-time use
