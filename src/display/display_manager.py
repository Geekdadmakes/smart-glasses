#!/usr/bin/env python3
"""
Display Manager for Smart Glasses 1.8" LCD HUD
Driver: ST7789H2, Resolution: 240x198
"""

import time
import logging
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont
import board
import digitalio
from adafruit_rgb_display import st7789

logger = logging.getLogger(__name__)


class DisplayManager:
    """Manages the 1.8" LCD HUD display for Smart Glasses"""

    def __init__(self, config: dict = None):
        """
        Initialize the display manager

        Args:
            config: Display configuration dict with:
                - brightness: 0-100 (default 80)
                - timeout: seconds before auto-sleep (default 30)
                - rotation: 0, 90, 180, 270 (default 0)
        """
        self.config = config or {}
        self.display = None
        self.width = 240
        self.height = 198
        self.rotation = self.config.get('rotation', 0)
        self.brightness = self.config.get('brightness', 80)
        self.timeout = self.config.get('timeout', 30)

        # Display state
        self.is_on = False
        self.last_activity = time.time()

        # Fonts (we'll use PIL's default font initially)
        self.font_small = None
        self.font_medium = None
        self.font_large = None

        # Current screen content
        self.current_image = None

        try:
            self._initialize_display()
            self._initialize_fonts()
            logger.info("Display Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            raise

    def _initialize_display(self):
        """Initialize the ST7789 display via SPI"""
        try:
            # SPI Configuration
            cs_pin = digitalio.DigitalInOut(board.CE0)
            dc_pin = digitalio.DigitalInOut(board.D24)
            reset_pin = digitalio.DigitalInOut(board.D25)

            # Backlight control (PWM on GPIO 18)
            self.backlight = digitalio.DigitalInOut(board.D18)
            self.backlight.switch_to_output()

            # Create the ST7789 display
            self.display = st7789.ST7789(
                board.SPI(),
                cs=cs_pin,
                dc=dc_pin,
                rst=reset_pin,
                width=self.width,
                height=self.height,
                y_offset=0,
                x_offset=0,
                rotation=self.rotation,
                baudrate=24000000,  # 24MHz SPI speed
            )

            # Turn on display
            self.turn_on()

            # Show startup screen
            self._show_startup()

            logger.info(f"Display initialized: {self.width}x{self.height} @ {self.rotation}°")

        except Exception as e:
            logger.error(f"Display initialization failed: {e}")
            raise

    def _initialize_fonts(self):
        """Initialize fonts for text rendering"""
        try:
            # Try to load TrueType fonts, fall back to default
            try:
                self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                self.font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
                self.font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except:
                # Fall back to default font
                self.font_small = ImageFont.load_default()
                self.font_medium = ImageFont.load_default()
                self.font_large = ImageFont.load_default()

            logger.info("Fonts initialized")
        except Exception as e:
            logger.warning(f"Font initialization failed, using defaults: {e}")

    def _show_startup(self):
        """Show startup splash screen"""
        image = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw "Smart Glasses" text
        text = "Smart\nGlasses"
        bbox = draw.textbbox((0, 0), text, font=self.font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2

        draw.text((x, y), text, font=self.font_large, fill=(0, 150, 255), align="center")

        self._display_image(image)

    def turn_on(self):
        """Turn on the display backlight"""
        if self.backlight:
            self.backlight.value = True
            self.is_on = True
            self.last_activity = time.time()
            logger.debug("Display turned on")

    def turn_off(self):
        """Turn off the display backlight"""
        if self.backlight:
            self.backlight.value = False
            self.is_on = False
            logger.debug("Display turned off")

    def check_timeout(self):
        """Check if display should auto-sleep"""
        if self.is_on and self.timeout > 0:
            if time.time() - self.last_activity > self.timeout:
                self.turn_off()
                return True
        return False

    def wake(self):
        """Wake up the display"""
        if not self.is_on:
            self.turn_on()
        self.last_activity = time.time()

    def set_brightness(self, level: int):
        """
        Set display brightness (0-100)
        Note: This is a simple on/off for now. PWM would be needed for true dimming.
        """
        self.brightness = max(0, min(100, level))
        if self.brightness > 0:
            self.turn_on()
        else:
            self.turn_off()

    def _display_image(self, image: Image.Image):
        """Send image to the display"""
        if self.display:
            self.display.image(image)
            self.current_image = image
            self.wake()

    def clear(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Clear the display with a solid color"""
        image = Image.new("RGB", (self.width, self.height), color=color)
        self._display_image(image)

    def show_text(
        self,
        text: str,
        x: int = 0,
        y: int = 0,
        font_size: str = "medium",
        color: Tuple[int, int, int] = (255, 255, 255),
        background: Tuple[int, int, int] = (0, 0, 0),
        align: str = "left",
        clear_screen: bool = True
    ):
        """
        Display text on the screen

        Args:
            text: Text to display
            x, y: Position (if align="left")
            font_size: "small", "medium", or "large"
            color: Text color (R, G, B)
            background: Background color (R, G, B)
            align: "left", "center", or "right"
            clear_screen: Clear screen before drawing
        """
        # Create image
        if clear_screen:
            image = Image.new("RGB", (self.width, self.height), color=background)
        else:
            image = self.current_image.copy() if self.current_image else Image.new("RGB", (self.width, self.height), color=background)

        draw = ImageDraw.Draw(image)

        # Select font
        font = {
            "small": self.font_small,
            "medium": self.font_medium,
            "large": self.font_large
        }.get(font_size, self.font_medium)

        # Calculate position for alignment
        if align == "center":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
        elif align == "right":
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = self.width - text_width - 5

        # Draw text
        draw.text((x, y), text, font=font, fill=color)

        self._display_image(image)

    def show_status(
        self,
        battery: int = 0,
        mode: str = "active",
        connected: bool = False,
        time_str: str = None
    ):
        """
        Show status bar at top of display

        Args:
            battery: Battery percentage (0-100)
            mode: Current mode ("active", "sleep", "listening")
            connected: WiFi/BLE connection status
            time_str: Current time string
        """
        # Create status bar image
        image = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Status bar background
        draw.rectangle([(0, 0), (self.width, 25)], fill=(20, 20, 40))

        # Time (left side)
        if time_str:
            draw.text((5, 5), time_str, font=self.font_small, fill=(255, 255, 255))

        # Battery icon and percentage (right side)
        battery_x = self.width - 60
        battery_color = (0, 255, 0) if battery > 20 else (255, 0, 0)
        draw.rectangle([(battery_x, 8), (battery_x + 30, 18)], outline=(200, 200, 200))
        draw.rectangle([(battery_x + 30, 11), (battery_x + 32, 15)], fill=(200, 200, 200))

        # Fill battery
        fill_width = int(28 * (battery / 100))
        draw.rectangle([(battery_x + 1, 9), (battery_x + 1 + fill_width, 17)], fill=battery_color)

        # Battery text
        draw.text((battery_x + 35, 5), f"{battery}%", font=self.font_small, fill=(255, 255, 255))

        # Connection indicator (WiFi icon)
        if connected:
            # Simple WiFi indicator
            conn_x = self.width - 100
            draw.ellipse([(conn_x, 10), (conn_x + 10, 20)], outline=(0, 150, 255))
            draw.text((conn_x + 12, 5), "WiFi", font=self.font_small, fill=(0, 150, 255))

        # Mode indicator
        mode_colors = {
            "active": (0, 255, 0),
            "sleep": (100, 100, 100),
            "listening": (255, 165, 0)
        }
        mode_color = mode_colors.get(mode, (255, 255, 255))
        draw.ellipse([(70, 8), (80, 18)], fill=mode_color)
        draw.text((85, 5), mode.upper(), font=self.font_small, fill=mode_color)

        self._display_image(image)

    def show_notification(
        self,
        title: str,
        message: str,
        duration: float = 3.0,
        icon: str = None
    ):
        """
        Show a notification popup

        Args:
            title: Notification title
            message: Notification message
            duration: How long to show (seconds)
            icon: Icon type ("info", "warning", "error", "success")
        """
        image = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Notification box
        box_margin = 10
        box_color = {
            "info": (0, 100, 200),
            "warning": (255, 165, 0),
            "error": (255, 0, 0),
            "success": (0, 200, 0)
        }.get(icon, (50, 50, 50))

        draw.rectangle(
            [(box_margin, box_margin), (self.width - box_margin, self.height - box_margin)],
            fill=box_color,
            outline=(255, 255, 255),
            width=2
        )

        # Title
        title_y = box_margin + 10
        draw.text((20, title_y), title, font=self.font_large, fill=(255, 255, 255))

        # Message (word wrap)
        message_y = title_y + 35
        lines = self._wrap_text(message, self.width - 40, draw, self.font_medium)
        for line in lines:
            draw.text((20, message_y), line, font=self.font_medium, fill=(255, 255, 255))
            message_y += 20

        self._display_image(image)

        # Auto-hide after duration
        if duration > 0:
            time.sleep(duration)
            self.clear()

    def show_caption(
        self,
        text: str,
        position: str = "bottom",
        background_alpha: float = 0.7
    ):
        """
        Show caption text (for live transcription)

        Args:
            text: Caption text to display
            position: "top" or "bottom"
            background_alpha: Background transparency (0-1)
        """
        image = self.current_image.copy() if self.current_image else Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Caption box
        lines = self._wrap_text(text, self.width - 20, draw, self.font_medium)
        line_height = 20
        box_height = len(lines) * line_height + 10

        if position == "bottom":
            box_y = self.height - box_height
        else:
            box_y = 0

        # Semi-transparent background
        bg_color = (0, 0, 0, int(255 * background_alpha))
        draw.rectangle([(0, box_y), (self.width, box_y + box_height)], fill=(0, 0, 0))

        # Draw caption text
        text_y = box_y + 5
        for line in lines:
            draw.text((10, text_y), line, font=self.font_medium, fill=(255, 255, 0))
            text_y += line_height

        self._display_image(image)

    def show_list(
        self,
        title: str,
        items: List[str],
        selected_index: int = 0
    ):
        """
        Show a scrollable list

        Args:
            title: List title
            items: List of items to display
            selected_index: Currently selected item index
        """
        image = Image.new("RGB", (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Title bar
        draw.rectangle([(0, 0), (self.width, 25)], fill=(0, 50, 100))
        draw.text((10, 5), title, font=self.font_medium, fill=(255, 255, 255))

        # List items (show up to 7 items)
        item_y = 30
        item_height = 24
        max_visible = min(7, len(items))

        # Calculate scroll offset
        scroll_offset = max(0, selected_index - max_visible + 1)

        for i in range(scroll_offset, min(scroll_offset + max_visible, len(items))):
            item = items[i]

            # Highlight selected item
            if i == selected_index:
                draw.rectangle(
                    [(0, item_y), (self.width, item_y + item_height)],
                    fill=(50, 50, 100)
                )

            # Truncate long text
            if len(item) > 25:
                item = item[:22] + "..."

            draw.text((10, item_y + 4), item, font=self.font_small, fill=(255, 255, 255))
            item_y += item_height

        # Scroll indicator
        if len(items) > max_visible:
            scroll_height = int((max_visible / len(items)) * (self.height - 30))
            scroll_y = int((scroll_offset / len(items)) * (self.height - 30)) + 30
            draw.rectangle(
                [(self.width - 5, scroll_y), (self.width, scroll_y + scroll_height)],
                fill=(100, 100, 100)
            )

        self._display_image(image)

    def _wrap_text(self, text: str, max_width: int, draw: ImageDraw, font) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def cleanup(self):
        """Cleanup and turn off display"""
        logger.info("Cleaning up display...")
        self.clear()
        self.turn_off()
        logger.info("Display cleanup complete")
