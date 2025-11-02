"""
Enhanced Vision Manager - Barcode scanning, product info, nutrition labels, color/face detection
"""

import logging
import base64
import requests

logger = logging.getLogger(__name__)


class VisionManager:
    """Manage enhanced vision features"""

    def __init__(self, camera_manager=None):
        """Initialize vision manager"""
        self.camera_manager = camera_manager
        logger.info("Vision Manager initialized")

    def scan_barcode(self, image_path=None):
        """Scan barcode/QR code from image"""
        try:
            # Use ZBar library for barcode scanning
            from pyzbar import pyzbar
            from PIL import Image

            # Take photo if not provided
            if not image_path and self.camera_manager:
                image_path = self.camera_manager.take_photo()

            if not image_path:
                return "No image available for barcode scanning"

            # Open image
            image = Image.open(image_path)

            # Detect barcodes
            barcodes = pyzbar.decode(image)

            if not barcodes:
                return "No barcode or QR code detected in image"

            # Process detected barcodes
            results = []
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type

                results.append({
                    'data': barcode_data,
                    'type': barcode_type
                })

                logger.info(f"Barcode detected: {barcode_type} - {barcode_data}")

            if len(results) == 1:
                result = results[0]
                return f"Detected {result['type']}: {result['data']}"
            else:
                text = f"Detected {len(results)} barcodes: "
                for i, r in enumerate(results, 1):
                    text += f"{i}. {r['type']}: {r['data']}. "
                return text.strip()

        except ImportError:
            return "Barcode scanning requires 'pyzbar' library. Install with: pip install pyzbar"
        except Exception as e:
            logger.error(f"Barcode scanning error: {e}")
            return f"Couldn't scan barcode: {str(e)}"

    def get_product_info(self, barcode):
        """Get product information from barcode using Open Food Facts API"""
        try:
            # Open Food Facts API (free, crowdsourced product database)
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 1:
                return f"Product not found for barcode: {barcode}"

            product = data.get('product', {})

            # Extract key information
            name = product.get('product_name', 'Unknown')
            brands = product.get('brands', 'Unknown')
            categories = product.get('categories', '')
            quantity = product.get('quantity', '')

            result = f"Product: {name}"
            if brands:
                result += f" by {brands}"
            if quantity:
                result += f", {quantity}"
            if categories:
                cats = categories.split(',')[:2]  # First 2 categories
                result += f". Categories: {', '.join(cats)}"

            logger.info(f"Product info retrieved: {name}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Product info error: {e}")
            return f"Couldn't get product info for barcode: {barcode}"

    def read_nutrition_label(self, vision_api_func, image_path=None):
        """Read nutrition label using vision AI"""
        # Take photo if not provided
        if not image_path and self.camera_manager:
            image_path = self.camera_manager.take_photo()

        if not image_path:
            return "No image available for nutrition label reading"

        # Use vision API to analyze
        prompt = """Analyze this nutrition label. Extract and report:
- Serving size
- Calories per serving
- Total fat, saturated fat
- Sodium
- Total carbohydrates, fiber, sugars
- Protein
- Key vitamins/minerals if visible

Format as a brief summary suitable for voice output."""

        result = vision_api_func(image_path, prompt)
        logger.info("Nutrition label analyzed")
        return result

    def detect_colors(self, vision_api_func, image_path=None):
        """Detect dominant colors in image"""
        # Take photo if not provided
        if not image_path and self.camera_manager:
            image_path = self.camera_manager.take_photo()

        if not image_path:
            return "No image available for color detection"

        prompt = """Identify and list the 3-5 dominant colors in this image.
For each color, provide the color name and approximate location/object.
Format as a brief, voice-friendly list."""

        result = vision_api_func(image_path, prompt)
        logger.info("Colors detected")
        return result

    def detect_faces(self, vision_api_func, image_path=None):
        """Detect faces and describe them"""
        # Take photo if not provided
        if not image_path and self.camera_manager:
            image_path = self.camera_manager.take_photo()

        if not image_path:
            return "No image available for face detection"

        prompt = """Analyze faces in this image. Report:
- Number of people visible
- For each person: approximate age range, gender presentation, facial expression
- General description of what they're doing

Be respectful and focus on observable characteristics only.
Format as brief, voice-friendly description."""

        result = vision_api_func(image_path, prompt)
        logger.info("Faces detected")
        return result

    def detect_objects(self, vision_api_func, image_path=None):
        """Detect and count objects in image"""
        # Take photo if not provided
        if not image_path and self.camera_manager:
            image_path = self.camera_manager.take_photo()

        if not image_path:
            return "No image available for object detection"

        prompt = """List all distinct objects visible in this image.
Group similar items and provide counts.
Format as a brief inventory suitable for voice output.
Example: "I see 3 books, 2 cups, 1 laptop, a plant, and a lamp." """

        result = vision_api_func(image_path, prompt)
        logger.info("Objects detected")
        return result

    def analyze_scene(self, vision_api_func, image_path=None):
        """Analyze entire scene comprehensively"""
        # Take photo if not provided
        if not image_path and self.camera_manager:
            image_path = self.camera_manager.take_photo()

        if not image_path:
            return "No image available for scene analysis"

        prompt = """Provide a comprehensive analysis of this scene including:
- Location type (indoor/outdoor, room type, etc.)
- Main objects and their arrangement
- People present and activities
- Lighting and atmosphere
- Any text visible
- Notable colors or patterns

Format as natural, conversational description suitable for someone who can't see the image."""

        result = vision_api_func(image_path, prompt)
        logger.info("Scene analyzed")
        return result

    def describe_for_accessibility(self, vision_api_func, image_path=None):
        """Describe image for visually impaired users"""
        # Take photo if not provided
        if not image_path and self.camera_manager:
            image_path = self.camera_manager.take_photo()

        if not image_path:
            return "No image available"

        prompt = """Describe this image in detail for a person who is visually impaired.
Include:
- Overall scene and setting
- People present and what they're doing
- Important objects and their locations
- Text content if any
- Colors and spatial relationships
- Potential hazards or navigation information

Be thorough, clear, and helpful. Format for voice output."""

        result = vision_api_func(image_path, prompt)
        logger.info("Accessibility description generated")
        return result

    def compare_products(self, vision_api_func, image_path1, image_path2):
        """Compare two products side by side"""
        if not image_path1 or not image_path2:
            return "Need two images to compare products"

        # This would require multi-image vision API support
        # For now, analyze each separately and combine
        prompt1 = "Describe this product briefly: name, price if visible, key features."
        prompt2 = "Describe this product briefly: name, price if visible, key features."

        product1 = vision_api_func(image_path1, prompt1)
        product2 = vision_api_func(image_path2, prompt2)

        result = f"Product 1: {product1}. Product 2: {product2}"
        logger.info("Products compared")
        return result
