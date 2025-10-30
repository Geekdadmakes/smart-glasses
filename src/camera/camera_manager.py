"""
Camera Manager - Handles photo and video capture
"""

import os
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages camera operations for photos and videos"""

    def __init__(self, config):
        """Initialize camera manager"""
        self.config = config
        self.resolution = (
            config.get('resolution', {}).get('width', 1920),
            config.get('resolution', {}).get('height', 1080)
        )
        self.photo_format = config.get('photo_format', 'jpg')
        self.video_format = config.get('video_format', 'h264')

        # Setup directories
        self.photos_dir = Path(config.get('photos_directory', './photos'))
        self.videos_dir = Path(config.get('videos_directory', './videos'))
        self.photos_dir.mkdir(exist_ok=True)
        self.videos_dir.mkdir(exist_ok=True)

        # Initialize camera
        self.camera = None
        self.initialize_camera()

        logger.info(f"Camera Manager initialized - resolution: {self.resolution}")

    def initialize_camera(self):
        """Initialize the Raspberry Pi camera"""
        try:
            # Import picamera2 (only available on Raspberry Pi)
            try:
                from picamera2 import Picamera2
                self.camera = Picamera2()
                config = self.camera.create_still_configuration(
                    main={"size": self.resolution}
                )
                self.camera.configure(config)
                logger.info("Camera initialized successfully")
            except ImportError:
                logger.warning("picamera2 not available - using placeholder mode")
                self.camera = None
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.camera = None

    def take_photo(self):
        """
        Take a photo and save it
        Returns the path to the saved photo
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.{self.photo_format}"
            filepath = self.photos_dir / filename

            if self.camera:
                logger.info(f"Taking photo: {filepath}")
                self.camera.start()
                self.camera.capture_file(str(filepath))
                self.camera.stop()
                logger.info(f"Photo saved: {filepath}")
            else:
                logger.warning("Camera not available - creating placeholder")
                filepath.touch()

            return str(filepath)

        except Exception as e:
            logger.error(f"Error taking photo: {e}")
            return None

    def record_video(self, duration=10):
        """
        Record a video for the specified duration
        Returns the path to the saved video
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.{self.video_format}"
            filepath = self.videos_dir / filename

            if self.camera:
                logger.info(f"Recording video: {filepath} (duration: {duration}s)")

                # Configure for video
                video_config = self.camera.create_video_configuration()
                self.camera.configure(video_config)

                # Start recording
                self.camera.start_recording(str(filepath))

                # Record for duration
                import time
                time.sleep(duration)

                # Stop recording
                self.camera.stop_recording()
                self.camera.stop()

                logger.info(f"Video saved: {filepath}")
            else:
                logger.warning("Camera not available - creating placeholder")
                filepath.touch()

            return str(filepath)

        except Exception as e:
            logger.error(f"Error recording video: {e}")
            return None

    def get_recent_photos(self, count=10):
        """Get list of recent photos"""
        photos = sorted(self.photos_dir.glob(f"*.{self.photo_format}"), reverse=True)
        return [str(p) for p in photos[:count]]

    def get_recent_videos(self, count=10):
        """Get list of recent videos"""
        videos = sorted(self.videos_dir.glob(f"*.{self.video_format}"), reverse=True)
        return [str(v) for v in videos[:count]]

    def cleanup(self):
        """Cleanup camera resources"""
        logger.info("Cleaning up camera manager")
        if self.camera:
            try:
                self.camera.close()
            except:
                pass
