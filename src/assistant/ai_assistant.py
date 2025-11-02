"""
AI Assistant - Handles conversational AI using Claude or GPT
Enhanced with personality, memory, and tool calling
"""

import os
import json
import logging
import base64
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from openai import OpenAI
from assistant.productivity_manager import ProductivityManager
from assistant.smart_home_manager import SmartHomeManager
from assistant.info_manager import InfoManager
from assistant.media_manager import MediaManager
from assistant.navigation_manager import NavigationManager
from assistant.communications_manager import CommunicationsManager
from assistant.quick_tools_manager import QuickToolsManager
from assistant.vision_manager import VisionManager
from assistant.translation_manager import TranslationManager
from assistant.fitness_manager import FitnessManager
from assistant.games_manager import GamesManager
from assistant.security_manager import SecurityManager

logger = logging.getLogger(__name__)


class AIAssistant:
    """AI assistant for processing voice commands and queries"""

    def __init__(self, config, camera_manager=None, bluetooth_manager=None):
        """Initialize AI assistant"""
        self.config = config
        self.provider = config.get('provider', 'anthropic')
        self.model = config.get('model', 'claude-3-5-sonnet-20241022')
        self.max_tokens = config.get('max_tokens', 1024)
        self.temperature = config.get('temperature', 0.7)

        # Personality settings
        self.personality = config.get('personality', 'friendly')
        self.assistant_name = config.get('name', 'Assistant')
        self.use_tools = config.get('use_tools', True)

        # Get API key from environment
        api_key_env = config.get('api_key_env', 'ANTHROPIC_API_KEY')
        self.api_key = os.getenv(api_key_env)

        if not self.api_key:
            logger.warning(f"API key not found in environment variable: {api_key_env}")

        # Initialize client
        self.client = None
        if self.provider == 'anthropic' and self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        elif self.provider == 'openai' and self.api_key:
            self.client = OpenAI(api_key=self.api_key)

        # Tool managers
        self.camera_manager = camera_manager
        self.bluetooth_manager = bluetooth_manager
        self.tools_available = []

        # Productivity manager (will be initialized after memory_dir is set)
        self.productivity_manager = None

        # Memory
        self.conversation_history = []
        self.user_preferences = {}
        self.session_context = {
            'session_start': datetime.now().isoformat(),
            'location': None,
            'user_name': None
        }

        # Memory persistence
        self.memory_dir = Path(config.get('memory_directory', './memory'))
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / 'conversation_memory.json'
        self.preferences_file = self.memory_dir / 'user_preferences.json'

        # Initialize productivity manager
        self.productivity_manager = ProductivityManager(
            data_dir=str(self.memory_dir / 'productivity')
        )

        # Initialize smart home manager
        self.smart_home_manager = SmartHomeManager(
            config_dir=str(self.memory_dir / 'smart_home')
        )

        # Initialize information manager
        self.info_manager = InfoManager()

        # Initialize media manager
        self.media_manager = MediaManager()

        # Initialize navigation manager
        self.navigation_manager = NavigationManager()

        # Initialize communications manager
        self.communications_manager = CommunicationsManager(
            data_dir=str(self.memory_dir / 'communications')
        )

        # Initialize quick tools manager
        self.quick_tools_manager = QuickToolsManager()

        # Initialize vision manager
        self.vision_manager = VisionManager(camera_manager=self.camera_manager)

        # Initialize translation manager
        self.translation_manager = TranslationManager()

        # Initialize fitness manager
        self.fitness_manager = FitnessManager(data_dir=str(self.memory_dir / 'fitness'))

        # Initialize games manager
        self.games_manager = GamesManager()

        # Initialize security manager
        self.security_manager = SecurityManager(memory_dir=str(self.memory_dir))

        # Load persistent memory
        self._load_memory()
        self._load_preferences()

        # System prompt
        self.system_prompt = self._build_system_prompt()

        # Initialize tools
        if self.use_tools:
            self._initialize_tools()

        logger.info(f"AI Assistant initialized - provider: {self.provider}, model: {self.model}, personality: {self.personality}")

    def _build_system_prompt(self):
        """Build system prompt based on personality and context"""

        # Base personality templates
        personalities = {
            'friendly': {
                'tone': 'warm, friendly, and conversational',
                'traits': 'You are enthusiastic, supportive, and use casual language. You occasionally use light humor.',
                'greeting': 'You greet users warmly and make them feel comfortable.'
            },
            'professional': {
                'tone': 'professional, clear, and efficient',
                'traits': 'You are formal, precise, and focus on delivering accurate information quickly.',
                'greeting': 'You are courteous and respectful in all interactions.'
            },
            'witty': {
                'tone': 'clever, humorous, and entertaining',
                'traits': 'You enjoy wordplay, make jokes, and keep things light-hearted while still being helpful.',
                'greeting': 'You often start with a clever remark or joke.'
            },
            'jarvis': {
                'tone': 'sophisticated, British, and slightly sarcastic',
                'traits': 'Like Tony Stark\'s AI assistant. You are witty, occasionally sarcastic, but always loyal and helpful. You address the user as "sir" or by name.',
                'greeting': 'You speak with refined British English and subtle dry humor.'
            },
            'casual': {
                'tone': 'relaxed, laid-back, and chill',
                'traits': 'You are like a helpful friend. You use casual language, contractions, and keep things simple.',
                'greeting': 'You are casual and approachable, like talking to a friend.'
            }
        }

        personality_config = personalities.get(self.personality, personalities['friendly'])

        # Build the prompt
        prompt = f"""You are {self.assistant_name}, an AI assistant integrated into smart glasses worn by the user.

PERSONALITY:
- Tone: {personality_config['tone']}
- Traits: {personality_config['traits']}
- Style: {personality_config['greeting']}

IMPORTANT GUIDELINES:
1. Keep responses BRIEF (1-3 sentences max) - they will be spoken aloud
2. Be conversational and natural - you're speaking, not writing
3. If asked to do something you can't do, acknowledge it briefly
4. Use the user's name if you know it
5. Remember context from earlier in the conversation
6. For complex answers, offer to break them into parts

CAPABILITIES:
You can help with:
- **SEEING and describing what the user is looking at** (via camera + vision AI)
- **Reading text** from signs, menus, documents (OCR via camera)
- **Identifying objects** and providing information about them
- Answering questions about the visual environment
- Taking photos and videos
- Music control (play, pause, next, previous)
- Hands-free phone calls (answer, end calls)
- Setting timers and reminders
- Telling time and date
- Simple calculations
- General conversation
- Remembering user preferences

CONTEXT:
- Current session started: {self.session_context.get('session_start', 'just now')}
- User name: {self.session_context.get('user_name', 'not set - you can ask')}
- Location: {self.session_context.get('location', 'unknown')}

MEMORY:
You have access to user preferences and past conversations. Reference them naturally when relevant.

VISION:
You have the ability to SEE through the camera! When users ask "what am I looking at?", "what is this?", "read this", or similar questions, use your vision tools to help them. You can describe scenes, read text, identify objects, and answer visual questions. This is one of your most powerful features!

Remember: You're worn on glasses, so you literally see what the user sees and can help them understand their visual environment in real-time."""

        return prompt

    def _initialize_tools(self):
        """Initialize available tools for Claude"""
        self.tools_available = [
            {
                "name": "take_photo",
                "description": "Take a photo with the smart glasses camera. Returns the file path of the captured photo.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "record_video",
                "description": "Record a video with the smart glasses camera. Default duration is 10 seconds.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "duration": {
                            "type": "number",
                            "description": "Duration in seconds to record (default: 10)",
                            "default": 10
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "set_timer",
                "description": "Set a timer for a specified duration. The assistant will notify when time is up.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "duration_seconds": {
                            "type": "number",
                            "description": "Timer duration in seconds"
                        },
                        "label": {
                            "type": "string",
                            "description": "Optional label for the timer (e.g., 'tea', 'workout')"
                        }
                    },
                    "required": ["duration_seconds"]
                }
            },
            {
                "name": "get_time",
                "description": "Get the current date and time",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "save_preference",
                "description": "Save a user preference for future reference",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Preference key (e.g., 'favorite_color', 'home_city')"
                        },
                        "value": {
                            "type": "string",
                            "description": "Preference value"
                        }
                    },
                    "required": ["key", "value"]
                }
            },
            {
                "name": "recall_preference",
                "description": "Recall a previously saved user preference",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "Preference key to recall"
                        }
                    },
                    "required": ["key"]
                }
            },
            {
                "name": "media_control",
                "description": "Control music/media playback on connected phone (play, pause, next track, previous track)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["play", "pause", "next", "previous"],
                            "description": "Media control action to perform"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "answer_call",
                "description": "Answer an incoming phone call",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "end_call",
                "description": "End the current phone call or reject an incoming call",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "bluetooth_status",
                "description": "Get Bluetooth connection status and information about connected devices",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "look_at",
                "description": "Take a photo and analyze what the user is looking at. Use this when the user asks 'what am I looking at?', 'what do you see?', 'describe this', etc. Returns a description of the scene.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Optional specific question about the scene (e.g., 'what color is this?', 'how many people?')"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "read_text",
                "description": "Take a photo and read any text visible in the image using OCR. Use when user says 'read this', 'what does this say?', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "identify_object",
                "description": "Take a photo and identify a specific object. Use when user asks 'what is this?', 'identify this object', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "take_note",
                "description": "Save a voice note for later. Use when user says 'take a note', 'remember this', 'write down', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "note": {
                            "type": "string",
                            "description": "The note content to save"
                        }
                    },
                    "required": ["note"]
                }
            },
            {
                "name": "set_reminder",
                "description": "Set a reminder with a specific time. Use when user says 'remind me', 'set a reminder', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "What to be reminded about"
                        },
                        "time": {
                            "type": "string",
                            "description": "When to remind (e.g., '3pm', 'in 2 hours', '5:30pm')"
                        }
                    },
                    "required": ["task", "time"]
                }
            },
            {
                "name": "add_to_shopping_list",
                "description": "Add items to the shopping list. Use when user says 'add to shopping list', 'I need to buy', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "string",
                            "description": "Item(s) to add to shopping list (comma-separated if multiple)"
                        }
                    },
                    "required": ["items"]
                }
            },
            {
                "name": "add_todo",
                "description": "Add a task to the todo list. Use when user says 'add to my todos', 'I need to do', 'add task', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "The task to add"
                        },
                        "priority": {
                            "type": "string",
                            "description": "Priority level: low, medium, or high (optional)"
                        }
                    },
                    "required": ["task"]
                }
            },
            {
                "name": "read_notes",
                "description": "Read back saved notes. Use when user asks 'read my notes', 'what are my notes', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "read_shopping_list",
                "description": "Read the shopping list. Use when user asks 'what's on my shopping list', 'read shopping list', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "read_todos",
                "description": "Read the todo list. Use when user asks 'what are my todos', 'what do I need to do', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            # Smart Home tools
            {
                "name": "turn_on_device",
                "description": "Turn on a smart home device (light, switch, etc.). Use when user says 'turn on', 'switch on', 'lights on', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "device": {
                            "type": "string",
                            "description": "Name of the device to turn on (e.g., 'living room light', 'bedroom lamp')"
                        }
                    },
                    "required": ["device"]
                }
            },
            {
                "name": "turn_off_device",
                "description": "Turn off a smart home device. Use when user says 'turn off', 'switch off', 'lights off', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "device": {
                            "type": "string",
                            "description": "Name of the device to turn off"
                        }
                    },
                    "required": ["device"]
                }
            },
            {
                "name": "set_brightness",
                "description": "Set brightness level for a light. Use when user says 'dim', 'brighten', 'set brightness', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "device": {
                            "type": "string",
                            "description": "Name of the light device"
                        },
                        "brightness": {
                            "type": "number",
                            "description": "Brightness level from 0-100 percent"
                        }
                    },
                    "required": ["device", "brightness"]
                }
            },
            {
                "name": "set_temperature",
                "description": "Set thermostat temperature. Use when user says 'set temperature', 'make it warmer/cooler', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "device": {
                            "type": "string",
                            "description": "Name of the thermostat (e.g., 'thermostat', 'main thermostat')"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature in degrees (Fahrenheit or Celsius based on system)"
                        }
                    },
                    "required": ["device", "temperature"]
                }
            },
            {
                "name": "activate_scene",
                "description": "Activate a smart home scene/routine. Use when user says 'activate', 'run scene', 'movie time', 'good morning', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "scene": {
                            "type": "string",
                            "description": "Name of the scene to activate (e.g., 'movie time', 'good morning', 'bedtime')"
                        }
                    },
                    "required": ["scene"]
                }
            },
            {
                "name": "check_device_status",
                "description": "Check the status of a smart home device. Use when user asks 'is the light on', 'what's the temperature', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "device": {
                            "type": "string",
                            "description": "Name of the device to check"
                        }
                    },
                    "required": ["device"]
                }
            },
            # Information & Lookup tools
            {
                "name": "get_weather",
                "description": "Get current weather for a location. Use when user asks 'what's the weather', 'how's the weather', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or location (optional, uses default if not provided)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_forecast",
                "description": "Get weather forecast for upcoming days. Use when user asks 'weather forecast', 'what's the weather tomorrow', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name or location (optional)"
                        },
                        "days": {
                            "type": "number",
                            "description": "Number of days to forecast (1-5, default 3)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_news",
                "description": "Get latest news headlines. Use when user asks 'what's the news', 'latest headlines', 'news about X', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "News topic to search for (optional, e.g., 'technology', 'sports')"
                        },
                        "count": {
                            "type": "number",
                            "description": "Number of headlines to return (1-5, default 3)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "search_wikipedia",
                "description": "Search Wikipedia for information. Use when user asks 'who is', 'what is', 'tell me about', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Wikipedia search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "define_word",
                "description": "Get the definition of a word. Use when user asks 'what does X mean', 'define X', 'definition of X', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Word to define"
                        }
                    },
                    "required": ["word"]
                }
            },
            {
                "name": "convert_units",
                "description": "Convert between units (length, weight, volume, temperature). Use when user asks 'convert X to Y', 'how many X in Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "string",
                            "description": "Numeric value to convert"
                        },
                        "from_unit": {
                            "type": "string",
                            "description": "Unit to convert from (e.g., 'miles', 'kg', 'celsius')"
                        },
                        "to_unit": {
                            "type": "string",
                            "description": "Unit to convert to (e.g., 'kilometers', 'pounds', 'fahrenheit')"
                        }
                    },
                    "required": ["value", "from_unit", "to_unit"]
                }
            },
            {
                "name": "convert_currency",
                "description": "Convert between currencies. Use when user asks 'convert X dollars to euros', 'how much is X in Y currency', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "string",
                            "description": "Amount to convert"
                        },
                        "from_currency": {
                            "type": "string",
                            "description": "Currency code to convert from (e.g., 'USD', 'EUR', 'GBP')"
                        },
                        "to_currency": {
                            "type": "string",
                            "description": "Currency code to convert to"
                        }
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                }
            },
            # Enhanced Media tools
            {
                "name": "search_song",
                "description": "Search for a song by name. Use when user asks 'find song X', 'search for X song', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Song name or search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_artist",
                "description": "Search for an artist and their songs. Use when user asks 'songs by X', 'artist X', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "artist": {
                            "type": "string",
                            "description": "Artist name"
                        }
                    },
                    "required": ["artist"]
                }
            },
            {
                "name": "search_album",
                "description": "Search for an album. Use when user asks 'find album X', 'album by Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "album": {
                            "type": "string",
                            "description": "Album name"
                        }
                    },
                    "required": ["album"]
                }
            },
            {
                "name": "search_podcast",
                "description": "Search for podcasts. Use when user asks 'find podcast X', 'search for X podcast', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Podcast name or topic"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "set_volume",
                "description": "Set system volume to specific level. Use when user says 'set volume to X', 'volume X percent', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "level": {
                            "type": "number",
                            "description": "Volume level from 0-100"
                        }
                    },
                    "required": ["level"]
                }
            },
            {
                "name": "get_volume",
                "description": "Get current system volume. Use when user asks 'what's the volume', 'volume level', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "volume_up",
                "description": "Increase volume. Use when user says 'volume up', 'louder', 'increase volume', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Amount to increase (1-100, default 10)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "volume_down",
                "description": "Decrease volume. Use when user says 'volume down', 'quieter', 'decrease volume', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Amount to decrease (1-100, default 10)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "mute_audio",
                "description": "Mute audio. Use when user says 'mute', 'silence', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "unmute_audio",
                "description": "Unmute audio. Use when user says 'unmute', 'sound on', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            # Navigation & Location tools
            {
                "name": "get_current_location",
                "description": "Get current approximate location. Use when user asks 'where am I', 'what's my location', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_directions",
                "description": "Get directions between two locations. Use when user asks 'how do I get to X', 'directions to Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Starting location (address or place name)"
                        },
                        "destination": {
                            "type": "string",
                            "description": "Destination (address or place name)"
                        }
                    },
                    "required": ["origin", "destination"]
                }
            },
            {
                "name": "find_nearby_places",
                "description": "Find nearby places of a specific type. Use when user asks 'find nearby X', 'where's the nearest Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location to search around"
                        },
                        "place_type": {
                            "type": "string",
                            "description": "Type of place (e.g., 'restaurant', 'gas_station', 'hospital', 'atm')"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_distance_between",
                "description": "Calculate distance between two locations. Use when user asks 'how far is X from Y', 'distance between A and B', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location1": {
                            "type": "string",
                            "description": "First location"
                        },
                        "location2": {
                            "type": "string",
                            "description": "Second location"
                        }
                    },
                    "required": ["location1", "location2"]
                }
            },
            {
                "name": "search_place",
                "description": "Search for a specific place or address. Use when user asks 'where is X', 'find location Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Place name or address to search for"
                        }
                    },
                    "required": ["query"]
                }
            },
            # Communications tools
            {
                "name": "add_contact",
                "description": "Add a new contact. Use when user says 'add contact', 'save contact', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Contact name"},
                        "phone": {"type": "string", "description": "Phone number"},
                        "email": {"type": "string", "description": "Email address (optional)"}
                    },
                    "required": ["name", "phone"]
                }
            },
            {
                "name": "get_contact",
                "description": "Get contact information. Use when user asks 'what's X's number', 'find contact Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Contact name"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "list_contacts",
                "description": "List all saved contacts. Use when user asks 'list contacts', 'show my contacts', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "call_contact",
                "description": "Initiate call to a contact. Use when user says 'call X', 'phone Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Contact name to call"}
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "dictate_message",
                "description": "Dictate a text message. Use when user says 'send message to X', 'text Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Recipient name or number"},
                        "message": {"type": "string", "description": "Message text"}
                    },
                    "required": ["recipient", "message"]
                }
            },
            {
                "name": "compose_email",
                "description": "Compose an email draft. Use when user says 'send email', 'email X', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "recipient": {"type": "string", "description": "Recipient name or email"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["recipient", "subject", "body"]
                }
            },
            # Quick Tools
            {
                "name": "calculate",
                "description": "Perform mathematical calculation. Use for 'calculate', 'what is X plus Y', math problems, etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Mathematical expression (e.g., '5 + 3 * 2', '100 / 4')"}
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "calculate_age",
                "description": "Calculate age from birthdate. Use when user asks 'how old is someone born on X', 'calculate age', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "birthdate": {"type": "string", "description": "Birthdate (YYYY-MM-DD or MM/DD/YYYY)"}
                    },
                    "required": ["birthdate"]
                }
            },
            {
                "name": "days_until",
                "description": "Calculate days until a date. Use for 'how many days until X', 'days to Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "Target date"}
                    },
                    "required": ["date"]
                }
            },
            {
                "name": "flip_coin",
                "description": "Flip a coin (heads or tails). Use when user says 'flip a coin', 'coin toss', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "roll_dice",
                "description": "Roll dice. Use when user says 'roll dice', 'roll a die', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sides": {"type": "number", "description": "Number of sides (default 6)"},
                        "count": {"type": "number", "description": "Number of dice to roll (default 1)"}
                    },
                    "required": []
                }
            },
            {
                "name": "random_number",
                "description": "Generate random number in range. Use for 'random number', 'pick a number between X and Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "number", "description": "Minimum value (default 1)"},
                        "max": {"type": "number", "description": "Maximum value (default 100)"}
                    },
                    "required": []
                }
            },
            {
                "name": "tip_calculator",
                "description": "Calculate tip and total. Use when user asks 'calculate tip', 'what's 20% tip on X', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "bill": {"type": "number", "description": "Bill amount in dollars"},
                        "tip_percent": {"type": "number", "description": "Tip percentage (default 20)"}
                    },
                    "required": ["bill"]
                }
            },
            # Enhanced Vision tools
            {
                "name": "scan_barcode",
                "description": "Scan barcode or QR code. Use when user says 'scan barcode', 'scan QR code', 'what's this barcode', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "read_nutrition_label",
                "description": "Read nutrition information from food label. Use when user asks 'read nutrition', 'what's in this', 'nutrition facts', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "detect_colors",
                "description": "Identify dominant colors in view. Use when user asks 'what colors', 'describe colors', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "count_objects",
                "description": "Count and list objects in view. Use when user asks 'count objects', 'what objects', 'inventory', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            # Language & Translation tools
            {
                "name": "translate_text",
                "description": "Translate text to another language. Use when user says 'translate X to Y', 'how do you say X in Y', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to translate"},
                        "target_language": {"type": "string", "description": "Target language code (e.g., 'es' for Spanish, 'fr' for French)"},
                        "source_language": {"type": "string", "description": "Source language code (optional, 'auto' to detect)"}
                    },
                    "required": ["text", "target_language"]
                }
            },
            {
                "name": "detect_language",
                "description": "Detect what language text is in. Use when user asks 'what language is this', 'detect language', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"}
                    },
                    "required": ["text"]
                }
            },
            {
                "name": "translate_sign",
                "description": "Translate text from a sign or image. Use when user says 'translate this sign', 'what does this say in English', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "target_language": {"type": "string", "description": "Target language code (e.g., 'en' for English)"}
                    },
                    "required": ["target_language"]
                }
            },
            # Fitness & Health tools
            {
                "name": "start_workout",
                "description": "Start workout timer. Use when user says 'start workout', 'begin exercise', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workout_type": {"type": "string", "description": "Type of workout (e.g., 'running', 'yoga', 'strength')"}
                    },
                    "required": []
                }
            },
            {
                "name": "end_workout",
                "description": "End workout timer. Use when user says 'stop workout', 'end exercise', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "log_water",
                "description": "Log water intake. Use when user says 'log water', 'drank X ounces', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "ounces": {"type": "number", "description": "Ounces of water consumed"}
                    },
                    "required": ["ounces"]
                }
            },
            {
                "name": "water_reminder",
                "description": "Get water reminder. Use when user asks 'remind me to drink water', 'water reminder', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            # Fun & Games tools
            {
                "name": "get_trivia",
                "description": "Get trivia question. Use when user says 'trivia', 'ask me a question', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_quote",
                "description": "Get inspirational quote. Use when user says 'quote', 'inspire me', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "tell_joke",
                "description": "Tell a joke. Use when user says 'tell me a joke', 'make me laugh', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_riddle",
                "description": "Get a riddle. Use when user says 'riddle', 'ask me a riddle', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            # Security & Privacy tools
            {
                "name": "clear_history",
                "description": "Clear conversation history. Use when user says 'clear history', 'delete conversations', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "enable_private_mode",
                "description": "Enable private mode. Use when user says 'private mode', 'don't save history', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_privacy_status",
                "description": "Get privacy settings status. Use when user asks 'privacy status', 'is private mode on', etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

        logger.info(f"Initialized {len(self.tools_available)} tools for AI assistant")

    def process(self, user_input):
        """
        Process user input and return AI response
        """
        if not self.client:
            logger.error("AI client not initialized - check API key")
            return "Sorry, I'm not properly configured. Please check the API key."

        try:
            logger.info(f"Processing: {user_input}")

            if self.provider == 'anthropic':
                response = self.process_anthropic(user_input)
            elif self.provider == 'openai':
                response = self.process_openai(user_input)
            else:
                response = "Sorry, I don't have a valid AI provider configured."

            logger.info(f"Response: {response}")

            # Save memory periodically
            self._save_memory()

            return response

        except Exception as e:
            logger.error(f"Error processing with AI: {e}")
            return "Sorry, I encountered an error processing your request."

    def process_anthropic(self, user_input):
        """Process using Anthropic Claude API with tool calling support"""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })

            # Call Claude API with tools if available
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": self.system_prompt,
                "messages": self.conversation_history
            }

            if self.use_tools and self.tools_available:
                kwargs["tools"] = self.tools_available

            response = self.client.messages.create(**kwargs)

            # Handle tool use if present
            assistant_content = []
            final_text = None

            for content_block in response.content:
                if content_block.type == "text":
                    final_text = content_block.text
                    assistant_content.append(content_block)

                elif content_block.type == "tool_use":
                    # Execute tool
                    tool_result = self._execute_tool(
                        content_block.name,
                        content_block.input
                    )

                    # Add tool use to content
                    assistant_content.append(content_block)

                    # Add assistant message with tool use
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_content
                    })

                    # Add tool result
                    self.conversation_history.append({
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": str(tool_result)
                        }]
                    })

                    # Get final response after tool use
                    final_response = self.client.messages.create(
                        model=self.model,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        system=self.system_prompt,
                        messages=self.conversation_history,
                        tools=self.tools_available if self.use_tools else None
                    )

                    final_text = final_response.content[0].text
                    assistant_content = [final_response.content[0]]

            # Add final assistant response to history
            if final_text:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content if assistant_content else final_text
                })

            # Keep history manageable (last 20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return final_text or "I completed the task."

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    def _execute_tool(self, tool_name, tool_input):
        """Execute a tool and return the result"""
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

        try:
            if tool_name == "take_photo":
                if self.camera_manager:
                    photo_path = self.camera_manager.take_photo()
                    return f"Photo captured and saved to {photo_path}"
                else:
                    return "Camera not available"

            elif tool_name == "record_video":
                if self.camera_manager:
                    duration = tool_input.get('duration', 10)
                    video_path = self.camera_manager.record_video(duration=duration)
                    return f"Video recorded for {duration} seconds and saved to {video_path}"
                else:
                    return "Camera not available"

            elif tool_name == "set_timer":
                duration = tool_input.get('duration_seconds')
                label = tool_input.get('label', 'Timer')
                # TODO: Implement actual timer functionality
                return f"Timer set for {duration} seconds ({duration/60:.1f} minutes) - {label}"

            elif tool_name == "get_time":
                now = datetime.now()
                return now.strftime("Current time: %I:%M %p, %A, %B %d, %Y")

            elif tool_name == "save_preference":
                key = tool_input.get('key')
                value = tool_input.get('value')
                self.user_preferences[key] = value
                self._save_preferences()
                return f"Saved preference: {key} = {value}"

            elif tool_name == "recall_preference":
                key = tool_input.get('key')
                value = self.user_preferences.get(key)
                if value:
                    return f"{key}: {value}"
                else:
                    return f"No preference found for {key}"

            elif tool_name == "media_control":
                if self.bluetooth_manager:
                    action = tool_input.get('action')
                    if action == 'play':
                        self.bluetooth_manager.media_play()
                        return "Playing music"
                    elif action == 'pause':
                        self.bluetooth_manager.media_pause()
                        return "Music paused"
                    elif action == 'next':
                        self.bluetooth_manager.media_next()
                        return "Skipping to next track"
                    elif action == 'previous':
                        self.bluetooth_manager.media_previous()
                        return "Going to previous track"
                    else:
                        return f"Unknown media action: {action}"
                else:
                    return "Bluetooth not available"

            elif tool_name == "answer_call":
                if self.bluetooth_manager:
                    self.bluetooth_manager.answer_call()
                    return "Call answered"
                else:
                    return "Bluetooth not available"

            elif tool_name == "end_call":
                if self.bluetooth_manager:
                    self.bluetooth_manager.end_call()
                    return "Call ended"
                else:
                    return "Bluetooth not available"

            elif tool_name == "bluetooth_status":
                if self.bluetooth_manager:
                    status = self.bluetooth_manager.get_status()
                    if status['connected']:
                        return f"Bluetooth connected to {status.get('connected_device', 'phone')}"
                    else:
                        return "Bluetooth not connected"
                else:
                    return "Bluetooth not available"

            elif tool_name == "look_at":
                if self.camera_manager:
                    # Take a photo
                    photo_path = self.camera_manager.take_photo()

                    # Analyze with vision
                    question = tool_input.get('question', 'What do you see in this image?')
                    description = self._analyze_image_with_vision(photo_path, question)

                    return description
                else:
                    return "Camera not available"

            elif tool_name == "read_text":
                if self.camera_manager:
                    # Take a photo
                    photo_path = self.camera_manager.take_photo()

                    # Read text from image
                    text = self._analyze_image_with_vision(
                        photo_path,
                        "Read all visible text in this image. If there's no text, say 'No text visible'."
                    )

                    return text
                else:
                    return "Camera not available"

            elif tool_name == "identify_object":
                if self.camera_manager:
                    # Take a photo
                    photo_path = self.camera_manager.take_photo()

                    # Identify object
                    identification = self._analyze_image_with_vision(
                        photo_path,
                        "What is the main object in this image? Identify it and provide relevant details."
                    )

                    return identification
                else:
                    return "Camera not available"

            # Productivity tools
            elif tool_name == "take_note":
                note = tool_input.get('note')
                return self.productivity_manager.add_note(note)

            elif tool_name == "set_reminder":
                task = tool_input.get('task')
                time = tool_input.get('time')
                return self.productivity_manager.add_reminder(task, time)

            elif tool_name == "add_to_shopping_list":
                items = tool_input.get('items')
                return self.productivity_manager.add_to_shopping_list(items)

            elif tool_name == "add_todo":
                task = tool_input.get('task')
                priority = tool_input.get('priority', 'medium')
                return self.productivity_manager.add_todo(task, priority)

            elif tool_name == "read_notes":
                return self.productivity_manager.get_notes()

            elif tool_name == "read_shopping_list":
                return self.productivity_manager.get_shopping_list()

            elif tool_name == "read_todos":
                return self.productivity_manager.get_todos()

            # Smart Home tools
            elif tool_name == "turn_on_device":
                device = tool_input.get('device')
                return self.smart_home_manager.turn_on_device(device)

            elif tool_name == "turn_off_device":
                device = tool_input.get('device')
                return self.smart_home_manager.turn_off_device(device)

            elif tool_name == "set_brightness":
                device = tool_input.get('device')
                brightness = tool_input.get('brightness')
                return self.smart_home_manager.set_brightness(device, brightness)

            elif tool_name == "set_temperature":
                device = tool_input.get('device')
                temperature = tool_input.get('temperature')
                return self.smart_home_manager.set_temperature(device, temperature)

            elif tool_name == "activate_scene":
                scene = tool_input.get('scene')
                return self.smart_home_manager.activate_scene(scene)

            elif tool_name == "check_device_status":
                device = tool_input.get('device')
                return self.smart_home_manager.get_device_state(device)

            # Information & Lookup tools
            elif tool_name == "get_weather":
                location = tool_input.get('location')
                return self.info_manager.get_weather(location)

            elif tool_name == "get_forecast":
                location = tool_input.get('location')
                days = tool_input.get('days', 3)
                return self.info_manager.get_forecast(location, days)

            elif tool_name == "get_news":
                topic = tool_input.get('topic')
                count = tool_input.get('count', 3)
                return self.info_manager.get_news(topic, count)

            elif tool_name == "search_wikipedia":
                query = tool_input.get('query')
                return self.info_manager.search_wikipedia(query)

            elif tool_name == "define_word":
                word = tool_input.get('word')
                return self.info_manager.define_word(word)

            elif tool_name == "convert_units":
                value = tool_input.get('value')
                from_unit = tool_input.get('from_unit')
                to_unit = tool_input.get('to_unit')
                return self.info_manager.convert_units(value, from_unit, to_unit)

            elif tool_name == "convert_currency":
                amount = tool_input.get('amount')
                from_currency = tool_input.get('from_currency')
                to_currency = tool_input.get('to_currency')
                return self.info_manager.convert_currency(amount, from_currency, to_currency)

            # Enhanced Media tools
            elif tool_name == "search_song":
                query = tool_input.get('query')
                return self.media_manager.search_song(query)

            elif tool_name == "search_artist":
                artist = tool_input.get('artist')
                return self.media_manager.search_artist(artist)

            elif tool_name == "search_album":
                album = tool_input.get('album')
                return self.media_manager.search_album(album)

            elif tool_name == "search_podcast":
                query = tool_input.get('query')
                return self.media_manager.search_podcast(query)

            elif tool_name == "set_volume":
                level = tool_input.get('level')
                return self.media_manager.set_volume(level)

            elif tool_name == "get_volume":
                return self.media_manager.get_volume()

            elif tool_name == "volume_up":
                amount = tool_input.get('amount', 10)
                return self.media_manager.volume_up(amount)

            elif tool_name == "volume_down":
                amount = tool_input.get('amount', 10)
                return self.media_manager.volume_down(amount)

            elif tool_name == "mute_audio":
                return self.media_manager.mute_audio()

            elif tool_name == "unmute_audio":
                return self.media_manager.unmute_audio()

            # Navigation & Location tools
            elif tool_name == "get_current_location":
                return self.navigation_manager.get_current_location()

            elif tool_name == "get_directions":
                origin = tool_input.get('origin')
                destination = tool_input.get('destination')
                return self.navigation_manager.get_directions(origin, destination)

            elif tool_name == "find_nearby_places":
                location = tool_input.get('location')
                place_type = tool_input.get('place_type')
                return self.navigation_manager.find_nearby_places(location, place_type)

            elif tool_name == "get_distance_between":
                location1 = tool_input.get('location1')
                location2 = tool_input.get('location2')
                return self.navigation_manager.get_distance_between(location1, location2)

            elif tool_name == "search_place":
                query = tool_input.get('query')
                return self.navigation_manager.search_place(query)

            # Communications tools
            elif tool_name == "add_contact":
                name = tool_input.get('name')
                phone = tool_input.get('phone')
                email = tool_input.get('email')
                return self.communications_manager.add_contact(name, phone, email)

            elif tool_name == "get_contact":
                name = tool_input.get('name')
                return self.communications_manager.get_contact(name)

            elif tool_name == "list_contacts":
                return self.communications_manager.list_contacts()

            elif tool_name == "call_contact":
                name = tool_input.get('name')
                return self.communications_manager.call_contact(name, self.bluetooth_manager)

            elif tool_name == "dictate_message":
                recipient = tool_input.get('recipient')
                message = tool_input.get('message')
                return self.communications_manager.dictate_message(recipient, message)

            elif tool_name == "compose_email":
                recipient = tool_input.get('recipient')
                subject = tool_input.get('subject')
                body = tool_input.get('body')
                return self.communications_manager.compose_email(recipient, subject, body)

            # Quick Tools
            elif tool_name == "calculate":
                expression = tool_input.get('expression')
                return self.quick_tools_manager.calculate(expression)

            elif tool_name == "calculate_age":
                birthdate = tool_input.get('birthdate')
                return self.quick_tools_manager.calculate_age(birthdate)

            elif tool_name == "days_until":
                date = tool_input.get('date')
                return self.quick_tools_manager.days_until(date)

            elif tool_name == "flip_coin":
                return self.quick_tools_manager.flip_coin()

            elif tool_name == "roll_dice":
                sides = tool_input.get('sides', 6)
                count = tool_input.get('count', 1)
                return self.quick_tools_manager.roll_dice(sides, count)

            elif tool_name == "random_number":
                min_val = tool_input.get('min', 1)
                max_val = tool_input.get('max', 100)
                return self.quick_tools_manager.random_number(min_val, max_val)

            elif tool_name == "tip_calculator":
                bill = tool_input.get('bill')
                tip_percent = tool_input.get('tip_percent', 20)
                return self.quick_tools_manager.tip_calculator(bill, tip_percent)

            # Enhanced Vision tools
            elif tool_name == "scan_barcode":
                return self.vision_manager.scan_barcode()

            elif tool_name == "read_nutrition_label":
                return self.vision_manager.read_nutrition_label(self._analyze_image_with_vision)

            elif tool_name == "detect_colors":
                return self.vision_manager.detect_colors(self._analyze_image_with_vision)

            elif tool_name == "count_objects":
                return self.vision_manager.detect_objects(self._analyze_image_with_vision)

            # Language & Translation tools
            elif tool_name == "translate_text":
                text = tool_input.get('text')
                target_lang = tool_input.get('target_language')
                source_lang = tool_input.get('source_language', 'auto')
                return self.translation_manager.translate_text(text, target_lang, source_lang)

            elif tool_name == "detect_language":
                text = tool_input.get('text')
                return self.translation_manager.detect_language(text)

            elif tool_name == "translate_sign":
                target_lang = tool_input.get('target_language')
                return self.translation_manager.translate_sign(
                    self._analyze_image_with_vision,
                    target_lang,
                    self.camera_manager
                )

            # Fitness & Health tools
            elif tool_name == "start_workout":
                workout_type = tool_input.get('workout_type', 'workout')
                return self.fitness_manager.start_workout(workout_type)

            elif tool_name == "end_workout":
                return self.fitness_manager.end_workout()

            elif tool_name == "log_water":
                ounces = tool_input.get('ounces')
                return self.fitness_manager.log_water(ounces)

            elif tool_name == "water_reminder":
                return self.fitness_manager.water_reminder()

            # Fun & Games tools
            elif tool_name == "get_trivia":
                return self.games_manager.get_trivia_question()

            elif tool_name == "get_quote":
                return self.games_manager.get_quote()

            elif tool_name == "tell_joke":
                return self.games_manager.joke()

            elif tool_name == "get_riddle":
                return self.games_manager.riddle()

            # Security & Privacy tools
            elif tool_name == "clear_history":
                return self.security_manager.clear_conversation_history()

            elif tool_name == "enable_private_mode":
                return self.security_manager.enable_private_mode()

            elif tool_name == "get_privacy_status":
                return self.security_manager.get_privacy_status()

            else:
                return f"Unknown tool: {tool_name}"

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"

    def _analyze_image_with_vision(self, image_path, question):
        """Analyze an image using Claude's vision capabilities"""
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')

            # Determine image type
            image_type = "image/jpeg"
            if image_path.endswith('.png'):
                image_type = "image/png"

            logger.info(f"Analyzing image with vision: {question}")

            if self.provider == 'anthropic':
                # Use Claude's vision API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": image_type,
                                        "data": image_data,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": question
                                }
                            ],
                        }
                    ],
                )

                description = response.content[0].text
                logger.info(f"Vision analysis complete: {description[:100]}...")
                return description

            elif self.provider == 'openai':
                # Use GPT-4o Vision (new 1.0+ format)
                response = self.client.chat.completions.create(
                    model=self.model,  # Use gpt-4o which has vision
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": question
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{image_type};base64,{image_data}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1024
                )

                description = response.choices[0].message.content
                logger.info(f"Vision analysis complete: {description[:100]}...")
                return description

            else:
                return "Vision analysis not available for this AI provider"

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Sorry, I couldn't analyze the image: {str(e)}"

    def process_openai(self, user_input):
        """Process using OpenAI GPT API with vision support"""
        try:
            # Check if this is a vision-related command
            vision_keywords = ['what am i looking at', 'what do you see', 'describe what',
                             'read this', 'what does this say', 'what is this object',
                             'what is this', 'identify this']

            is_vision_command = any(keyword in user_input.lower() for keyword in vision_keywords)

            if is_vision_command and self.camera_manager:
                # Handle vision commands directly
                logger.info("Detected vision command, using camera")
                photo_path = self.camera_manager.take_photo()

                # Determine the type of vision request
                if 'read' in user_input.lower():
                    question = "Read all visible text in this image. If there's no text, say 'No text visible'."
                elif 'identify' in user_input.lower() or 'what is this' in user_input.lower():
                    question = "Identify the main object in this image and provide information about it."
                else:
                    question = "Describe what you see in this image in detail."

                # Analyze image
                description = self._analyze_image_with_vision(photo_path, question)

                # Update history
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": description})

                return description

            # Regular text conversation
            # Normalize conversation history to ensure all content is strings
            normalized_history = []
            for msg in self.conversation_history:
                normalized_history.append({
                    "role": msg["role"],
                    "content": str(msg["content"])  # Ensure it's a string
                })

            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + normalized_history + [
                {"role": "user", "content": user_input}
            ]

            # Call OpenAI API (new 1.0+ format)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Extract response
            assistant_message = response.choices[0].message.content

            # Update history
            self.conversation_history.append({"role": "user", "content": user_input})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Keep history manageable
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return assistant_message

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _load_memory(self):
        """Load conversation history from file"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Only load recent history (last session)
                    self.conversation_history = data.get('history', [])[-10:]
                    self.session_context.update(data.get('context', {}))
                logger.info(f"Loaded {len(self.conversation_history)} messages from memory")
        except Exception as e:
            logger.error(f"Error loading memory: {e}")

    def _save_memory(self):
        """Save conversation history to file"""
        try:
            data = {
                'history': self.conversation_history,
                'context': self.session_context,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    def _load_preferences(self):
        """Load user preferences from file"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r') as f:
                    self.user_preferences = json.load(f)
                logger.info(f"Loaded {len(self.user_preferences)} user preferences")
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")

    def _save_preferences(self):
        """Save user preferences to file"""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.user_preferences, f, indent=2)
            logger.info("User preferences saved")
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")

    def set_user_name(self, name):
        """Set the user's name"""
        self.session_context['user_name'] = name
        self.user_preferences['name'] = name
        self._save_preferences()
        # Rebuild system prompt with new name
        self.system_prompt = self._build_system_prompt()
        logger.info(f"User name set to: {name}")

    def set_location(self, location):
        """Set current location"""
        self.session_context['location'] = location
        logger.info(f"Location set to: {location}")

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self._save_memory()
        logger.info("Conversation history cleared")

    def get_stats(self):
        """Get assistant statistics"""
        return {
            'messages_in_history': len(self.conversation_history),
            'user_preferences': len(self.user_preferences),
            'personality': self.personality,
            'model': self.model,
            'tools_available': len(self.tools_available) if self.use_tools else 0
        }
