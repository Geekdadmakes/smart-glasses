"""
Flask REST API Server for Smart Glasses
Handles WiFi-based high-bandwidth communication with iOS companion app
"""

import logging
import json
import os
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
import yaml

logger = logging.getLogger(__name__)


class APIServer:
    """
    Flask REST API server for WiFi communication
    Handles settings, camera, media, productivity, and system control
    """

    def __init__(self, managers=None, port=5000):
        """
        Initialize API server

        Args:
            managers: Dictionary of manager instances
            port: Port to run server on (default: 5000)
        """
        self.managers = managers or {}
        self.port = port

        # Create Flask app
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for iOS app

        # Load configuration
        self.config = self._load_config()

        # Load API key
        self.api_key = self._load_api_key()

        # Setup routes
        self._setup_routes()

        # Server thread
        self.server_thread = None
        self.is_running = False

        logger.info(f"API Server initialized on port {self.port}")

    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            config_path = Path('./config/config.yaml')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        return {}

    def _load_api_key(self):
        """Load API key for authentication"""
        try:
            api_key_file = Path('./config/api_key.txt')
            if api_key_file.exists():
                with open(api_key_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading API key: {e}")
        return None

    def _check_auth(self):
        """Check API key authentication"""
        api_key = request.headers.get('X-API-Key')
        if not self.api_key or api_key != self.api_key:
            return jsonify({'error': 'Unauthorized'}), 401
        return None

    def _setup_routes(self):
        """Setup all API routes"""

        # Authentication middleware
        @self.app.before_request
        def before_request():
            # Skip auth for connection test endpoint
            if request.path == '/api/connection/test':
                return None
            # Check auth for all other endpoints
            auth_error = self._check_auth()
            if auth_error:
                return auth_error

        # ===== STATUS & CONNECTION =====

        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """Get system status"""
            try:
                status = {
                    'mode': 'active',  # TODO: Get from main app
                    'personality': self.config.get('assistant', {}).get('personality', 'friendly'),
                    'name': self.config.get('assistant', {}).get('name', 'Jarvis'),
                    'battery': 85,  # TODO: Get actual battery level
                    'connected': True,
                    'timestamp': datetime.now().isoformat()
                }
                return jsonify(status)
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/connection/test', methods=['GET'])
        def test_connection():
            """Test connection (no auth required)"""
            return jsonify({'status': 'ok', 'message': 'Connection successful'})

        @self.app.route('/api/connection/type', methods=['GET'])
        def get_connection_type():
            """Get connection type"""
            return jsonify({'type': 'wifi'})

        # ===== SETTINGS =====

        @self.app.route('/api/settings', methods=['GET'])
        def get_settings():
            """Get all settings"""
            try:
                settings = {
                    'personality': self.config.get('assistant', {}).get('personality', 'friendly'),
                    'name': self.config.get('assistant', {}).get('name', 'Jarvis'),
                    'wake_word': {
                        'keyword': self.config.get('wake_word', {}).get('keyword', 'hey glasses'),
                        'sensitivity': self.config.get('wake_word', {}).get('sensitivity', 0.5)
                    },
                    'voice': {
                        'engine': self.config.get('tts', {}).get('engine', 'gtts'),
                        'rate': self.config.get('tts', {}).get('rate', 150),
                        'volume': self.config.get('tts', {}).get('volume', 0.6)
                    },
                    'camera': {
                        'resolution': self.config.get('camera', {}).get('resolution', {}),
                        'rotation': 0,  # TODO: Get from camera manager
                        'flip_horizontal': False,
                        'flip_vertical': False
                    }
                }
                return jsonify(settings)
            except Exception as e:
                logger.error(f"Error getting settings: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/settings/personality', methods=['PUT'])
        def update_personality():
            """Update AI personality"""
            try:
                data = request.get_json()
                personality = data.get('personality')

                if personality not in ['friendly', 'professional', 'witty', 'jarvis', 'casual']:
                    return jsonify({'error': 'Invalid personality'}), 400

                self._update_config('assistant', 'personality', personality)
                return jsonify({'success': True, 'personality': personality})
            except Exception as e:
                logger.error(f"Error updating personality: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/settings/name', methods=['PUT'])
        def update_name():
            """Update assistant name"""
            try:
                data = request.get_json()
                name = data.get('name')

                if not name:
                    return jsonify({'error': 'Name is required'}), 400

                self._update_config('assistant', 'name', name)
                return jsonify({'success': True, 'name': name})
            except Exception as e:
                logger.error(f"Error updating name: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/settings/wake-word', methods=['PUT'])
        def update_wake_word():
            """Update wake word configuration"""
            try:
                data = request.get_json()
                keyword = data.get('keyword')
                sensitivity = data.get('sensitivity')

                if keyword:
                    self._update_config('wake_word', 'keyword', keyword)
                if sensitivity is not None:
                    self._update_config('wake_word', 'sensitivity', float(sensitivity))

                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error updating wake word: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/settings/voice', methods=['PUT'])
        def update_voice():
            """Update voice settings"""
            try:
                data = request.get_json()

                if 'engine' in data:
                    self._update_config('tts', 'engine', data['engine'])
                if 'rate' in data:
                    self._update_config('tts', 'rate', int(data['rate']))
                if 'volume' in data:
                    self._update_config('tts', 'volume', float(data['volume']))

                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error updating voice: {e}")
                return jsonify({'error': str(e)}), 500

        # ===== CAMERA =====

        @self.app.route('/api/camera/stream', methods=['GET'])
        def camera_stream():
            """MJPEG camera stream"""
            # TODO: Implement MJPEG streaming
            return jsonify({'error': 'Camera streaming not yet implemented'}), 501

        @self.app.route('/api/camera/snapshot', methods=['GET'])
        def camera_snapshot():
            """Get single camera snapshot"""
            try:
                if 'camera_manager' not in self.managers:
                    return jsonify({'error': 'Camera not available'}), 503

                # Take a photo
                photo_path = self.managers['camera_manager'].take_photo()

                if photo_path and Path(photo_path).exists():
                    return send_file(photo_path, mimetype='image/jpeg')
                else:
                    return jsonify({'error': 'Failed to capture snapshot'}), 500
            except Exception as e:
                logger.error(f"Error getting snapshot: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/camera/capture', methods=['POST'])
        def camera_capture():
            """Capture photo remotely"""
            try:
                if 'camera_manager' not in self.managers:
                    return jsonify({'error': 'Camera not available'}), 503

                photo_path = self.managers['camera_manager'].take_photo()

                return jsonify({
                    'success': True,
                    'path': str(photo_path),
                    'filename': Path(photo_path).name
                })
            except Exception as e:
                logger.error(f"Error capturing photo: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/camera/record', methods=['POST'])
        def camera_record():
            """Record video remotely"""
            try:
                if 'camera_manager' not in self.managers:
                    return jsonify({'error': 'Camera not available'}), 503

                data = request.get_json() or {}
                duration = data.get('duration', 10)

                video_path = self.managers['camera_manager'].record_video(duration=duration)

                return jsonify({
                    'success': True,
                    'path': str(video_path),
                    'filename': Path(video_path).name
                })
            except Exception as e:
                logger.error(f"Error recording video: {e}")
                return jsonify({'error': str(e)}), 500

        # ===== MEDIA (Photos & Videos) =====

        @self.app.route('/api/photos', methods=['GET'])
        def get_photos():
            """List all photos"""
            try:
                photos_dir = Path('./photos')
                if not photos_dir.exists():
                    return jsonify([])

                photos = []
                for photo_file in sorted(photos_dir.glob('*.jpg'), reverse=True):
                    stat = photo_file.stat()
                    photos.append({
                        'id': photo_file.stem,
                        'filename': photo_file.name,
                        'size': stat.st_size,
                        'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

                return jsonify(photos)
            except Exception as e:
                logger.error(f"Error listing photos: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/photos/<photo_id>', methods=['GET'])
        def get_photo(photo_id):
            """Download specific photo"""
            try:
                photo_path = Path(f'./photos/{photo_id}.jpg')

                if not photo_path.exists():
                    return jsonify({'error': 'Photo not found'}), 404

                return send_file(photo_path, mimetype='image/jpeg', as_attachment=False)
            except Exception as e:
                logger.error(f"Error getting photo: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/photos/<photo_id>', methods=['DELETE'])
        def delete_photo(photo_id):
            """Delete photo"""
            try:
                photo_path = Path(f'./photos/{photo_id}.jpg')

                if not photo_path.exists():
                    return jsonify({'error': 'Photo not found'}), 404

                os.remove(photo_path)
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error deleting photo: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/videos', methods=['GET'])
        def get_videos():
            """List all videos"""
            try:
                videos_dir = Path('./videos')
                if not videos_dir.exists():
                    return jsonify([])

                videos = []
                for video_file in sorted(videos_dir.glob('*.h264'), reverse=True):
                    stat = video_file.stat()
                    videos.append({
                        'id': video_file.stem,
                        'filename': video_file.name,
                        'size': stat.st_size,
                        'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })

                return jsonify(videos)
            except Exception as e:
                logger.error(f"Error listing videos: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/videos/<video_id>', methods=['GET'])
        def get_video(video_id):
            """Download specific video"""
            try:
                video_path = Path(f'./videos/{video_id}.h264')

                if not video_path.exists():
                    return jsonify({'error': 'Video not found'}), 404

                return send_file(video_path, mimetype='video/h264', as_attachment=True)
            except Exception as e:
                logger.error(f"Error getting video: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/videos/<video_id>', methods=['DELETE'])
        def delete_video(video_id):
            """Delete video"""
            try:
                video_path = Path(f'./videos/{video_id}.h264')

                if not video_path.exists():
                    return jsonify({'error': 'Video not found'}), 404

                os.remove(video_path)
                return jsonify({'success': True})
            except Exception as e:
                logger.error(f"Error deleting video: {e}")
                return jsonify({'error': str(e)}), 500

        # ===== PRODUCTIVITY (Notes & Todos) =====

        @self.app.route('/api/notes', methods=['GET'])
        def get_notes():
            """Get all notes"""
            try:
                if 'productivity_manager' in self.managers:
                    notes = self.managers['productivity_manager'].get_notes()
                    return jsonify(notes)
                return jsonify([])
            except Exception as e:
                logger.error(f"Error getting notes: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/notes', methods=['POST'])
        def add_note():
            """Add new note"""
            try:
                data = request.get_json()
                content = data.get('content')

                if not content:
                    return jsonify({'error': 'Content is required'}), 400

                if 'productivity_manager' in self.managers:
                    result = self.managers['productivity_manager'].add_note(content)
                    return jsonify({'success': True, 'message': result})

                return jsonify({'error': 'Productivity manager not available'}), 503
            except Exception as e:
                logger.error(f"Error adding note: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/todos', methods=['GET'])
        def get_todos():
            """Get all todos"""
            try:
                if 'productivity_manager' in self.managers:
                    todos = self.managers['productivity_manager'].get_todos()
                    return jsonify(todos)
                return jsonify([])
            except Exception as e:
                logger.error(f"Error getting todos: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/todos', methods=['POST'])
        def add_todo():
            """Add new todo"""
            try:
                data = request.get_json()
                task = data.get('task')
                priority = data.get('priority', 'medium')

                if not task:
                    return jsonify({'error': 'Task is required'}), 400

                if 'productivity_manager' in self.managers:
                    result = self.managers['productivity_manager'].add_todo(task, priority)
                    return jsonify({'success': True, 'message': result})

                return jsonify({'error': 'Productivity manager not available'}), 503
            except Exception as e:
                logger.error(f"Error adding todo: {e}")
                return jsonify({'error': str(e)}), 500

        # ===== CONVERSATION HISTORY =====

        @self.app.route('/api/conversation', methods=['GET'])
        def get_conversation():
            """Get conversation history"""
            try:
                memory_file = Path('./memory/conversation_memory.json')
                if memory_file.exists():
                    with open(memory_file, 'r') as f:
                        history = json.load(f)
                    return jsonify(history)
                return jsonify([])
            except Exception as e:
                logger.error(f"Error getting conversation: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/conversation', methods=['DELETE'])
        def clear_conversation():
            """Clear conversation history"""
            try:
                if 'security_manager' in self.managers:
                    result = self.managers['security_manager'].clear_conversation_history()
                    return jsonify({'success': True, 'message': result})

                # Fallback: clear manually
                memory_file = Path('./memory/conversation_memory.json')
                if memory_file.exists():
                    with open(memory_file, 'w') as f:
                        json.dump([], f)
                    return jsonify({'success': True, 'message': 'Conversation history cleared'})

                return jsonify({'success': True, 'message': 'No history to clear'})
            except Exception as e:
                logger.error(f"Error clearing conversation: {e}")
                return jsonify({'error': str(e)}), 500

        # ===== SYSTEM CONTROL =====

        @self.app.route('/api/control/sleep', methods=['POST'])
        def control_sleep():
            """Put system to sleep"""
            try:
                # TODO: Trigger sleep mode in main app
                logger.info("Sleep command received via API")
                return jsonify({'success': True, 'message': 'Going to sleep'})
            except Exception as e:
                logger.error(f"Error in sleep control: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/control/wake', methods=['POST'])
        def control_wake():
            """Wake system up"""
            try:
                # TODO: Trigger wake mode in main app
                logger.info("Wake command received via API")
                return jsonify({'success': True, 'message': 'Waking up'})
            except Exception as e:
                logger.error(f"Error in wake control: {e}")
                return jsonify({'error': str(e)}), 500

    def _update_config(self, section, key, value):
        """Update configuration file"""
        try:
            config_path = Path('./config/config.yaml')

            # Update in-memory config
            if section not in self.config:
                self.config[section] = {}
            self.config[section][key] = value

            # Save to file
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f)

            logger.info(f"Config updated: {section}.{key} = {value}")

        except Exception as e:
            logger.error(f"Error updating config: {e}")

    def start(self):
        """Start the API server"""
        try:
            logger.info(f"Starting API server on 0.0.0.0:{self.port}...")
            self.is_running = True
            self.app.run(host='0.0.0.0', port=self.port, debug=False, threaded=True)
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            self.is_running = False

    def start_in_thread(self):
        """Start server in background thread"""
        self.server_thread = threading.Thread(target=self.start, daemon=True)
        self.server_thread.start()
        logger.info("API server started in background thread")
        return self.server_thread

    def stop(self):
        """Stop the API server"""
        # TODO: Implement graceful shutdown
        self.is_running = False
        logger.info("API server stopped")
