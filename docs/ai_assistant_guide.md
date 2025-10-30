# AI Assistant Guide

Complete guide to the enhanced AI assistant with personality, memory, and tools.

## Overview

The smart glasses AI assistant is powered by Claude or GPT and features:
- **5 Personality types** with unique voices and behaviors
- **Persistent memory** that remembers conversations and preferences
- **Tool calling** for taking photos, videos, timers, and more
- **Context awareness** including time, location, and user info
- **Personality-matched voice** for natural interaction

## Personalities

### 1. Friendly (Default)
- **Tone**: Warm, friendly, conversational
- **Best for**: Daily use, casual conversations
- **Voice**: Female, slightly higher pitch, upbeat
- **Example**: "Hey! I'd be happy to help with that. What would you like to know?"

### 2. Professional
- **Tone**: Professional, clear, efficient
- **Best for**: Work meetings, formal contexts
- **Voice**: Male, neutral pitch, steady pace
- **Example**: "Certainly. I can assist you with that information."

### 3. Witty
- **Tone**: Clever, humorous, entertaining
- **Best for**: Fun interactions, keeping things light
- **Voice**: Male, slightly faster, expressive
- **Example**: "Well, that's an interesting question! Let me think... *dramatic pause* Got it!"

### 4. Jarvis
- **Tone**: Sophisticated British, slightly sarcastic
- **Best for**: Feeling like Iron Man
- **Voice**: British male, slower, refined
- **Example**: "Of course, sir. Though I must say, that's quite an unusual request."

### 5. Casual
- **Tone**: Relaxed, laid-back, friendly
- **Best for**: Everyday use, casual vibes
- **Voice**: Female, conversational pace
- **Example**: "Yeah, totally! Let me grab that for you real quick."

## Configuration

Edit `config/config.yaml`:

```yaml
assistant:
  personality: "jarvis"  # Choose: friendly, professional, witty, jarvis, casual
  name: "Jarvis"        # What to call your assistant
  use_tools: true        # Enable tool calling
  memory_directory: "./memory"
```

## Available Tools

The assistant can use these tools automatically:

### 1. Camera Tools

**Take Photo**
- Command: "Take a photo"
- What it does: Captures a photo and saves it
- Response: "Photo captured and saved to [path]"

**Record Video**
- Command: "Record a 15 second video"
- What it does: Records video for specified duration
- Response: "Video recorded for 15 seconds and saved to [path]"

### 2. Time Tools

**Get Time**
- Command: "What time is it?"
- What it does: Returns current date and time
- Response: "Current time: 3:45 PM, Monday, October 29, 2025"

**Set Timer**
- Command: "Set a timer for 5 minutes"
- What it does: Sets a countdown timer with optional label
- Response: "Timer set for 300 seconds (5.0 minutes)"

### 3. Memory Tools

**Save Preference**
- Command: "Remember that my favorite color is blue"
- What it does: Saves information for future reference
- Response: "Saved preference: favorite_color = blue"

**Recall Preference**
- Command: "What's my favorite color?"
- What it does: Retrieves previously saved information
- Response: "favorite_color: blue"

## Memory System

### Conversation History
- Automatically saves last 20 messages
- Persists across sessions
- Stored in `memory/conversation_memory.json`

### User Preferences
- Manually saved via voice commands
- Permanently stored
- Stored in `memory/user_preferences.json`

### Session Context
- Current session info (start time, location, user name)
- Automatically included in responses
- Resets on restart

## Example Interactions

### First Meeting
```
You: "What's your name?"
Jarvis: "I'm Jarvis, sir. Your AI assistant integrated into these smart glasses."

You: "My name is Tony"
Jarvis: "Pleasure to make your acquaintance, Tony."

You: "Remember that I like my coffee black"
Jarvis: "Noted, sir. Black coffee it is."
```

### Later Session
```
You: "Good morning"
Jarvis: "Good morning, Tony. Shall I remind you of your preferred coffee?"

You: "Yes, what is it?"
Jarvis: "Black coffee, as you indicated previously, sir."
```

### Using Tools
```
You: "Take a photo of this"
Jarvis: "Capturing image now... Photo saved successfully, sir."

You: "Set a timer for 10 minutes"
Jarvis: "Timer set for 10 minutes. I'll notify you when complete."

You: "What time is it?"
Jarvis: "The time is currently 2:30 PM, Monday afternoon."
```

## Voice Customization

### Adjusting TTS Settings

Edit `config/config.yaml`:

```yaml
tts:
  engine: "pyttsx3"  # Options: pyttsx3, gtts
  rate: 150          # Words per minute (120-200)
  volume: 0.9        # 0.0 to 1.0
```

### Voice Characteristics by Personality

| Personality | Gender | Rate (WPM) | Pitch | Style |
|------------|--------|------------|-------|-------|
| Friendly | Female | 160 | Higher | Upbeat |
| Professional | Male | 150 | Neutral | Steady |
| Witty | Male | 170 | Higher | Expressive |
| Jarvis | Male (British) | 145 | Lower | Refined |
| Casual | Female | 165 | Medium | Relaxed |

### Installing Better Voices (Raspberry Pi)

```bash
# Install espeak-ng for more voices
sudo apt-get install espeak-ng

# Install festival voices
sudo apt-get install festival festvox-kallpc16k

# Install additional espeak voices
sudo apt-get install espeak-ng-data
```

## Advanced Features

### Custom Personality

You can create custom personalities by editing `src/assistant/ai_assistant.py`:

```python
personalities = {
    'custom': {
        'tone': 'your custom tone here',
        'traits': 'personality traits',
        'greeting': 'greeting style'
    }
}
```

### Tool Development

Add new tools in `src/assistant/ai_assistant.py`:

```python
{
    "name": "custom_tool",
    "description": "What this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param"]
    }
}
```

Then implement in `_execute_tool()`:

```python
elif tool_name == "custom_tool":
    param = tool_input.get('param')
    # Your tool logic here
    return f"Tool result: {param}"
```

## Memory Management

### View Memory

```python
# In your code
stats = glasses.ai_assistant.get_stats()
print(stats)
```

### Clear History

```python
glasses.ai_assistant.clear_history()
```

### Export Preferences

Memory files are JSON:
- `memory/conversation_memory.json` - Recent conversations
- `memory/user_preferences.json` - Saved preferences

You can edit these files directly if needed.

## Tips & Best Practices

### 1. Be Specific
**Good**: "Set a timer for 5 minutes for my tea"
**Better**: The label helps you remember what the timer is for

### 2. Use Memory
- Save important preferences early
- Reference them naturally in conversation
- The assistant will remember across sessions

### 3. Personality Matching
- Choose personality based on your use case
- Professional for work, Casual for everyday
- Jarvis for fun/sci-fi feel

### 4. Tool Usage
- Tools activate automatically when needed
- Just ask naturally: "Take a photo" vs "Use the camera tool"
- Assistant chooses the right tool

### 5. Context Awareness
- Assistant knows current time automatically
- Set your name for personalized responses
- Update location for location-aware help

## Troubleshooting

### Assistant Not Responding
- Check API key in `.env`
- Verify internet connection (for Claude/GPT APIs)
- Check logs: `logs/smart_glasses.log`

### Tools Not Working
- Ensure `use_tools: true` in config
- Check camera is initialized
- Verify using Anthropic provider (OpenAI tools not yet implemented)

### Memory Not Persisting
- Check `memory/` directory exists
- Verify write permissions
- Look for errors in logs

### Voice Sounds Wrong
- Try different personality settings
- Adjust rate and pitch in config
- Install additional voices (see above)

### Personality Not Matching Voice
- Voice selection is automatic but system-dependent
- Raspberry Pi may have limited voices
- Consider using gTTS for online voices

## Performance Optimization

### For Raspberry Pi Zero

1. **Use Anthropic Claude** - More efficient than GPT
2. **Limit history** - Default 20 messages is good
3. **Disable unused tools** - Set `use_tools: false` if not needed
4. **Use pyttsx3** - Offline, faster than gTTS
5. **Clear memory periodically** - Prevents file bloat

### Battery Life

- Tools use camera/processing power
- Memory saves are lightweight
- Voice synthesis is efficient with pyttsx3
- Consider disabling persistent memory for longer battery

## Future Enhancements

Planned features:
- [ ] Timer notifications and callbacks
- [ ] Multi-user support (remember multiple people)
- [ ] Voice emotion detection
- [ ] Context from computer vision (describe what you see)
- [ ] Integration with calendar/reminders
- [ ] Smarthome control
- [ ] ElevenLabs premium voices
- [ ] Custom wake word responses per personality

## Resources

- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)
- [Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)
- [Voice Installation Guide](https://github.com/espeak-ng/espeak-ng)

## Examples by Personality

### Jarvis Example
```
User: "Jarvis, what's the weather like?"
Jarvis: "I'm afraid I don't have access to weather data at present, sir. Might I suggest checking your phone, or would you prefer I note this as a feature request?"

User: "Take a photo of this sunset"
Jarvis: "Capturing the moment, sir. Quite a lovely view, if I may say so."

User: "Set a timer for my workout"
Jarvis: "Timer initiated for your fitness regimen, sir. Do push yourself, but do remember to stay hydrated."
```

### Friendly Example
```
User: "Hey, can you help me?"
Assistant: "Of course! I'm here to help. What do you need?"

User: "Take a picture"
Assistant: "Got it! Taking a photo now... Perfect! It's saved and ready!"

User: "Remember my dog's name is Max"
Assistant: "Aww, Max! I'll remember that. Such a great name!"
```

### Professional Example
```
User: "I need to document this meeting"
Assistant: "Understood. I can take photos or record video. Which would you prefer?"

User: "Photos please"
Assistant: "Capturing image now. Photo saved successfully."

User: "Set a 30 minute timer for the next session"
Assistant: "Timer configured for 30 minutes. You will be notified when time expires."
```
