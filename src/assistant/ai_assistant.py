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
