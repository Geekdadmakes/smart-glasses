# AI Assistant - Feature Summary

## What Was Implemented

The AI assistant has been completely enhanced with personality, memory, voice, and tools.

### ✅ Personality System

**5 Unique Personalities:**
1. **Friendly** - Warm, encouraging, casual
2. **Professional** - Clear, efficient, formal
3. **Witty** - Humorous, clever, entertaining
4. **Jarvis** - British, sophisticated, slightly sarcastic (like Iron Man's AI)
5. **Casual** - Relaxed, laid-back, friendly

**How It Works:**
- Each personality has unique response patterns
- System prompts are dynamically generated
- Personality defined in `config/config.yaml`
- Can be changed anytime by editing config

**Key Files:**
- `src/assistant/ai_assistant.py` - Personality definitions and system prompts
- `config/config.yaml` - Personality selection
- `docs/PERSONALITY_EXAMPLES.md` - Examples of each personality

---

### ✅ Voice System

**Enhanced Text-to-Speech:**
- Personality-matched voices (gender, pitch, rate)
- Multiple TTS engines (pyttsx3, gTTS, **ElevenLabs integrated**)
- Premium natural voices via ElevenLabs
- Configurable rate, pitch, and volume
- Automatic voice selection based on personality
- Custom voice ID mapping per personality

**Voice Characteristics:**
| Personality | Voice | Rate | Pitch | Style |
|------------|-------|------|-------|-------|
| Friendly | Female | Fast | High | Upbeat |
| Professional | Male | Medium | Neutral | Steady |
| Witty | Male | Faster | High | Expressive |
| Jarvis | Male (British) | Slow | Low | Refined |
| Casual | Female | Medium | Medium | Relaxed |

**Key Files:**
- `src/audio/tts_manager.py` - Enhanced TTS system
- `src/audio/audio_manager.py` - Updated to use TTS manager
- `config/config.yaml` - TTS configuration

---

### ✅ Memory System

**Three Types of Memory:**

1. **Conversation History**
   - Remembers last 20 messages
   - Persists across sessions
   - Automatically managed
   - File: `memory/conversation_memory.json`

2. **User Preferences**
   - Permanent storage of user info
   - Saved via voice commands
   - Manually managed
   - File: `memory/user_preferences.json`

3. **Session Context**
   - Current session info (time, location, user name)
   - Automatically tracked
   - Included in all responses

**Memory Functions:**
- `_load_memory()` - Load conversation history
- `_save_memory()` - Save conversations
- `_load_preferences()` - Load user preferences
- `_save_preferences()` - Save preferences
- `set_user_name()` - Set user's name
- `set_location()` - Update location
- `clear_history()` - Clear conversation history

**Key Files:**
- `src/assistant/ai_assistant.py` - Memory management
- `memory/` directory - Storage location

---

### ✅ Tool Calling

**6 Built-in Tools:**

1. **take_photo**
   - Takes photo with camera
   - Returns file path
   - Automatic integration

2. **record_video**
   - Records video (configurable duration)
   - Default 10 seconds
   - Returns file path

3. **set_timer**
   - Sets countdown timer
   - Optional label
   - Duration in seconds

4. **get_time**
   - Returns current date and time
   - Formatted naturally

5. **save_preference**
   - Saves user preference
   - Key-value storage
   - Persists across sessions

6. **recall_preference**
   - Retrieves saved preference
   - Returns value or "not found"

**How Tools Work:**
- Claude automatically decides when to use tools
- Tool execution happens transparently
- Results are integrated into responses
- User just speaks naturally

**Tool Architecture:**
- Tool definitions in `_initialize_tools()`
- Tool execution in `_execute_tool()`
- Automatic API integration with Claude
- Easy to add new tools

**Key Files:**
- `src/assistant/ai_assistant.py` - Tool definitions and execution

---

### ✅ Context Awareness

**What the Assistant Knows:**
- Current date and time (always up-to-date)
- User's name (if set)
- Current location (if set)
- Session start time
- Past conversation (20 messages)
- Saved preferences (unlimited)

**How It's Used:**
- Included in system prompt
- Referenced in responses
- Provides personalized interaction
- Maintains continuity

**Example:**
```
User: "What time is it?"
Assistant: "Good afternoon! It's 3:45 PM."

User: "My name is Tony"
Assistant: "Nice to meet you, Tony!"

*Later*
User: "What's my name?"
Assistant: "Your name is Tony, as you told me earlier."
```

---

## Configuration

### Basic Setup

Edit `config/config.yaml`:

```yaml
assistant:
  # AI Provider
  provider: "anthropic"
  model: "claude-3-5-sonnet-20241022"
  api_key_env: "ANTHROPIC_API_KEY"

  # Response Settings
  max_tokens: 1024
  temperature: 0.7

  # Personality & Behavior
  personality: "jarvis"    # friendly, professional, witty, jarvis, casual
  name: "Jarvis"           # Assistant's name
  use_tools: true          # Enable tool calling

  # Memory
  memory_directory: "./memory"

# TTS Settings
tts:
  engine: "pyttsx3"        # pyttsx3, gtts
  rate: 150                # Words per minute
  volume: 0.9              # 0.0 to 1.0
```

### API Keys

Add to `.env`:

```
ANTHROPIC_API_KEY=your_key_here
# or
OPENAI_API_KEY=your_key_here
```

---

## Usage Examples

### Basic Conversation

```
User: "Hey Jarvis"
Jarvis: "Good evening, sir. How may I assist?"

User: "What time is it?"
Jarvis: "The time is currently 7:30 PM, sir."

User: "Take a photo"
Jarvis: "Certainly. *captures* Photo saved, sir."
```

### Using Memory

```
User: "Remember that my favorite coffee is espresso"
Jarvis: "Noted, sir. Espresso it is."

*Later, even after restart*

User: "What's my favorite coffee?"
Jarvis: "Espresso, sir. As you indicated previously."
```

### Tool Integration

```
User: "I need to remember to check the oven in 20 minutes"
Jarvis: "Timer set for 20 minutes, sir. I shall alert you accordingly."

User: "Take a quick video"
Jarvis: "Recording now... Video captured and saved, sir."
```

---

## Architecture

### Class Structure

```
AIAssistant
├── __init__()           # Initialize with camera_manager
├── _build_system_prompt() # Dynamic prompt based on personality
├── _initialize_tools()    # Setup tool definitions
├── process()              # Main entry point
├── process_anthropic()    # Handle Claude with tools
├── _execute_tool()        # Execute tools (camera, timer, etc.)
├── _load_memory()         # Load conversation history
├── _save_memory()         # Save conversations
├── _load_preferences()    # Load user preferences
├── _save_preferences()    # Save preferences
├── set_user_name()        # Set user's name
├── set_location()         # Update location
├── clear_history()        # Clear conversation
└── get_stats()            # Get statistics
```

### Integration Points

```
main.py
├── Creates TTSManager (personality-matched voice)
├── Creates CameraManager
├── Creates AIAssistant (with camera_manager)
└── Passes user input to assistant.process()

AIAssistant
├── Uses CameraManager for photo/video tools
├── Uses memory system for persistence
├── Uses Claude API with tools
└── Returns natural language response

AudioManager/TTSManager
└── Speaks the response with personality voice
```

---

## File Structure

```
src/assistant/
└── ai_assistant.py         # Main AI assistant (750+ lines)

src/audio/
├── tts_manager.py          # Enhanced TTS system
└── audio_manager.py        # Updated to use TTS manager

config/
└── config.yaml             # Personality & TTS config

memory/
├── conversation_memory.json  # Conversation history
└── user_preferences.json     # User preferences

docs/
├── ai_assistant_guide.md     # Complete guide
└── PERSONALITY_EXAMPLES.md   # Example interactions
```

---

## Performance Notes

### Raspberry Pi Zero Considerations

- **Tools add latency**: Camera operations take ~1-2 seconds
- **Memory is lightweight**: JSON files are small
- **Claude API calls**: ~500ms-2s depending on network
- **TTS with pyttsx3**: Nearly instant, offline
- **Total response time**: ~2-4 seconds for tool use, ~1-2s for conversation

### Optimization Tips

1. Use `pyttsx3` for offline TTS (faster)
2. Limit conversation history (default 20 is good)
3. Disable tools if not needed (`use_tools: false`)
4. Clear memory periodically
5. Use shorter responses (controlled by system prompt)

---

## Future Enhancements

### Planned
- [ ] Timer callbacks (actual notifications)
- [ ] Multi-user support (remember different people)
- [ ] Emotion detection from voice
- [ ] Computer vision integration (describe what you see)
- [ ] Calendar and reminder integration
- [ ] Smart home control
- [ ] Custom tool creation via config
- [ ] Voice customization per user

### Advanced
- [ ] ElevenLabs integration (premium natural voices)
- [ ] Long-term memory summarization
- [ ] Context from environment (weather, location, etc.)
- [ ] Multi-language support
- [ ] Offline AI models (llama.cpp)

---

## Testing

### Test Personalities

```bash
# Edit config to change personality
nano config/config.yaml

# Run application
python3 src/main.py

# Try different personalities to find your favorite
```

### Test Tools

```bash
# In conversation mode
"Take a photo"
"Record a 5 second video"
"Set a timer for 2 minutes"
"What time is it?"
"Remember that my name is Tony"
"What's my name?"
```

### Test Memory

```bash
# Session 1
"Remember my favorite color is blue"
"What's my favorite color?"  # Should recall

# Restart application

# Session 2
"What's my favorite color?"  # Should still know!
```

---

## Troubleshooting

### Tools Not Working
- Check `use_tools: true` in config
- Verify camera_manager is passed to assistant
- Ensure using Anthropic provider (tools on Claude)
- Check logs for errors

### Personality Not Right
- Verify spelling in config
- Restart application after config changes
- Check system prompt generation in logs

### Memory Not Saving
- Check `memory/` directory exists
- Verify write permissions
- Look for errors in logs
- Check JSON file validity

### Voice Doesn't Match Personality
- Voice selection is system-dependent
- Install additional voices (see docs)
- May need manual voice configuration
- Consider using gTTS for online voices

---

## Documentation

- `docs/ai_assistant_guide.md` - Complete user guide
- `docs/PERSONALITY_EXAMPLES.md` - Personality examples
- `docs/wake_word_setup.md` - Wake word setup
- `README.md` - Project overview
- `QUICK_START.md` - Quick start guide

---

## Credits

Built with:
- **Anthropic Claude** - AI reasoning and tool use
- **pyttsx3** - Text-to-speech
- **Python** - Core implementation
- **Raspberry Pi** - Hardware platform

Inspired by:
- Iron Man's Jarvis
- Ray-Ban Meta smart glasses
- Science fiction AI assistants

---

## Summary

The AI assistant now features:
- ✅ **5 unique personalities** with distinct behaviors
- ✅ **Personality-matched voices** for natural interaction
- ✅ **Persistent memory** across sessions
- ✅ **6 built-in tools** (camera, timer, time, preferences)
- ✅ **Context awareness** (name, time, location)
- ✅ **Tool calling** via Claude API
- ✅ **Configurable everything** via YAML
- ✅ **Comprehensive documentation**

This transforms the smart glasses from a simple voice assistant into a truly intelligent, personable companion that remembers you, helps you, and adapts to your style! 🎉
