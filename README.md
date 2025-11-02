# Smart Glasses Project

Voice-activated smart glasses powered by Raspberry Pi Zero with Ray-Ban Meta functionality and more.

## Features

### Core Features
- **👁️ COMPUTER VISION** - AI can SEE what you're looking at and describe it!
- **📖 Text Reading (OCR)** - Read signs, menus, labels, documents aloud
- **🔍 Enhanced Vision** - Barcode scanning, nutrition labels, color detection, object counting
- **🎤 Voice-activated AI assistant** with 5 unique personalities (Friendly, Professional, Witty, Jarvis, Casual)
- **🔊 Wake word detection** with sleep/active modes (Porcupine, Vosk, or Energy-based)
- **⏸️ Interruptible AI** - Stop long responses mid-speech with your voice
- **🧠 Persistent memory** - Remembers conversations and preferences across sessions
- **🛠️ 60+ AI tools** across 12 feature categories
- **🎙️ Premium voices** - ElevenLabs natural TTS with personality matching
- **📸 Photo and video capture** via voice commands
- **📱 Bluetooth integration** - Music streaming, phone calls, photo sync
- **⚡ Context awareness** - Knows time, location, and user preferences

### 12 Feature Categories (60+ Tools)

**1. Core Conversation & Memory**
- Persistent conversation history and user preferences
- Context-aware responses with personality matching
- Long-term memory across sessions

**2. Smart Home Integration**
- Control lights, switches, climate, locks via Home Assistant
- Voice-activated home automation
- Status checking and scene control

**3. Productivity Tools**
- Note taking and retrieval
- Todo lists with priorities
- Reminders and calendar events
- Timer management

**4. Entertainment & Media**
- Music search and recommendations
- Podcast discovery
- Book recommendations
- Movie and TV show information

**5. Real-time Information**
- Weather forecasts and conditions
- News headlines by category
- Stock prices and market data
- Sports scores and updates

**6. Navigation & Location**
- Current location and coordinates
- Distance and time calculations
- Basic navigation assistance

**7. Quick Tools**
- Calculator for complex math
- Age calculator
- Days until date counter
- Coin flip and dice roll
- Random number generator
- Tip calculator

**8. Enhanced Vision**
- Barcode and QR code scanning
- Nutrition label reading
- Color detection and identification
- Object counting in images

**9. Language & Translation**
- Text translation (100+ languages)
- Language detection
- Sign translation using camera

**10. Fitness & Health**
- Workout timer and tracking
- Water intake logging
- Exercise history and goals

**11. Fun & Games**
- Trivia questions with difficulty levels
- Jokes and riddles
- Inspirational quotes
- Magic 8-ball and yes/no decisions
- Word of the day

**12. Security & Privacy**
- Clear conversation history
- Private mode (no history saving)
- Data export and management
- Privacy status checking

## Hardware Requirements

- **Raspberry Pi Zero W** - Main processor with WiFi/Bluetooth
- **WM8960 Audio HAT** - High-quality audio codec with built-in echo reduction features
- **Raspberry Pi Camera Module** (OV5647 or compatible)
- **Portable battery pack** - 5V USB power
- **Eyeglass frame** for mounting components

## Software Setup

### 1. Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install python3-pip python3-dev -y

# Install audio dependencies
sudo apt-get install portaudio19-dev python3-pyaudio -y

# Install system packages
sudo apt-get install espeak ffmpeg libespeak1 -y

# Install Python packages
pip3 install -r requirements.txt
```

### 2. Configure Audio HAT

#### WM8960 Audio HAT Setup

```bash
# Test microphone
arecord -l

# Test speaker
aplay -l

# Record test audio
arecord -D plughw:1,0 -d 5 test.wav

# Play test audio
aplay test.wav

# Configure echo reduction (recommended)
cd ~/smart-glasses
chmod +x scripts/configure_audio_echo_reduction.sh
./scripts/configure_audio_echo_reduction.sh
```

**Echo Reduction Features:**
The WM8960 configuration script enables hardware-based echo cancellation:
- Noise gate with maximum threshold
- ADC high-pass filter for low-frequency echo removal
- Automatic Level Control (ALC) for dynamic range
- Optimized speaker/microphone volumes to prevent feedback

This is essential for the **interruptible AI feature** to work properly.

### 3. Setup Camera

```bash
# Enable camera interface
sudo raspi-config
# Navigate to: Interfacing Options -> Camera -> Enable

# Test camera
libcamera-hello
```

### 4. Configure API Keys

```bash
# Copy example env file
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your API keys:
```
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PORCUPINE_ACCESS_KEY=your_porcupine_key_here
```

Get a free Porcupine access key at: https://console.picovoice.ai/

### 5. Run the Application

```bash
cd smart-glasses
python3 src/main.py
```

## Configuration

Edit `config/config.yaml` to customize:
- **AI Personality** (friendly, professional, witty, jarvis, casual)
- Assistant name and behavior
- Audio settings (sample rate, device indices)
- Wake word sensitivity and method
- AI model selection
- Camera resolution
- TTS voice settings (rate, volume, engine)
- Memory directory

### Choosing a Personality

```yaml
assistant:
  personality: "jarvis"  # friendly, professional, witty, jarvis, casual
  name: "Jarvis"         # What to call your assistant
  use_tools: true        # Enable camera, timers, etc.
```

## Usage

### Operating Modes

The smart glasses operate in two modes:

**SLEEP MODE:**
- Low power state, listening only for wake word
- Say "computer" (or your configured keyword) to activate
- LED indicator shows sleep state

**ACTIVE MODE:**
- Continuous listening for 60 seconds after last command
- Speak naturally without saying wake word again
- AI responses are interruptible - just start speaking!
- Automatically returns to sleep after timeout

### How to Use

1. **Startup**: Run the application, wait for "Smart glasses ready"
2. **Wake Up**: Say "computer" to enter ACTIVE mode
3. **Interact**: Ask questions or give commands naturally
4. **Interrupt**: If AI gives a long response, just start speaking to interrupt
5. **Continue**: Keep talking within 60 seconds to stay active
6. **Sleep**: Say "go to sleep" or wait for timeout

### Voice Commands

**Basic Interaction:**
- "What time is it?"
- "Tell me a joke"
- "Tell me a riddle"
- "Give me an inspirational quote"
- "What's the word of the day?"
- "Go to sleep" / "Shutdown"

**Vision Commands (AI can SEE!):**
- "What am I looking at?"
- "Describe what you see"
- "Read this menu / sign / label"
- "What color is this?"
- "How many objects are here?"
- "Scan this barcode"
- "Read this nutrition label"

**Camera Commands:**
- "Take a photo"
- "Record a video"
- "Record a 15 second video"

**Smart Home:**
- "Turn on the living room lights"
- "Set bedroom temperature to 72 degrees"
- "Lock the front door"
- "What's the status of the kitchen lights?"

**Productivity:**
- "Add a note: remember to buy milk"
- "Add todo: finish project report"
- "Set a reminder for 3pm to call mom"
- "Set a timer for 10 minutes"
- "What are my notes?"
- "What's on my todo list?"

**Quick Tools:**
- "Calculate 234 times 567"
- "How old am I if I was born March 15, 1990?"
- "How many days until Christmas?"
- "Flip a coin"
- "Roll a dice"
- "Calculate 20% tip on $45.50"

**Entertainment & Information:**
- "Search for songs by Taylor Swift"
- "Find me a podcast about technology"
- "Recommend a sci-fi book"
- "What's the weather like?"
- "Give me the latest tech news"
- "What's the price of Apple stock?"

**Translation:**
- "Translate hello to Spanish"
- "What language is this?"
- "Translate this sign" (uses camera)

**Fitness & Health:**
- "Start a workout timer"
- "Log 16 ounces of water"
- "What's my water intake today?"
- "Show my workout history"

**Games:**
- "Ask me a trivia question"
- "Tell me a joke"
- "Give me a riddle"
- "Magic 8-ball: will it rain tomorrow?"
- "Yes or no?"

**Security & Privacy:**
- "Enable private mode"
- "Clear my conversation history"
- "What data do you have stored?"
- "What's my privacy status?"

**Memory (persistent across sessions):**
- "Remember my name is Tony"
- "My favorite coffee is espresso"
- "What's my name?"
- "What's my favorite coffee?"

**The AI will:**
- Automatically use the right tool for each task
- Remember your preferences forever
- Be interruptible during long responses
- Respond with chosen personality
- Maintain conversation context across sessions

## Project Structure

```
smart-glasses/
├── src/
│   ├── main.py                          # Main application with sleep/active modes
│   ├── audio/                           # Audio input/output
│   │   ├── audio_manager.py             # Non-blocking TTS with interruption
│   │   ├── tts_manager.py               # Multi-engine TTS (gTTS, ElevenLabs, pyttsx3)
│   │   ├── wake_word.py                 # Porcupine/Vosk wake word detection
│   │   └── speech_recognition.py        # Google/Vosk speech-to-text
│   ├── camera/                          # Camera operations
│   │   └── camera_manager.py            # Photo/video capture
│   ├── assistant/                       # AI assistant (60+ tools)
│   │   ├── ai_assistant.py              # Main AI with tool calling
│   │   ├── memory_manager.py            # Persistent conversation & preferences
│   │   ├── smart_home_manager.py        # Home Assistant integration
│   │   ├── productivity_manager.py      # Notes, todos, reminders, timers
│   │   ├── entertainment_manager.py     # Music, podcasts, books, movies
│   │   ├── information_manager.py       # Weather, news, stocks, sports
│   │   ├── location_manager.py          # GPS and navigation
│   │   ├── quick_tools_manager.py       # Calculator, age, dates, random
│   │   ├── vision_manager.py            # Barcode, nutrition, colors, counting
│   │   ├── translation_manager.py       # Text & sign translation
│   │   ├── fitness_manager.py           # Workout timer, water logging
│   │   ├── games_manager.py             # Trivia, jokes, riddles, quotes
│   │   └── security_manager.py          # Privacy controls & data management
│   ├── bluetooth/                       # Bluetooth connectivity
│   │   └── bluetooth_manager.py         # Music, calls, photo sync
│   └── vision/                          # Computer vision (future)
├── config/                              # Configuration files
│   └── config.yaml                      # Main configuration
├── scripts/                             # Setup & utility scripts
│   ├── configure_audio_echo_reduction.sh  # WM8960 echo cancellation
│   └── audio-echo-reduction.service     # Systemd service for audio config
├── memory/                              # Persistent data storage
│   ├── conversation_memory.json
│   ├── user_preferences.json
│   ├── productivity/                    # Notes, todos, reminders
│   ├── fitness/                         # Workout & water logs
│   └── communications/                  # Contacts & messages
├── photos/                              # Captured photos
├── videos/                              # Recorded videos
└── logs/                                # Application logs
```

## Development Status

### ✅ Fully Implemented
- [x] **Project structure** - Complete modular architecture
- [x] **Configuration system** - YAML-based with environment variables
- [x] **Audio system** - WM8960 with hardware echo reduction
- [x] **Speech recognition** - Google/Vosk with offline support
- [x] **👁️ COMPUTER VISION** - Scene description, OCR, barcode scanning
- [x] **Enhanced vision** - Nutrition labels, color detection, object counting
- [x] **AI assistant with 5 personalities** (Friendly, Professional, Witty, Jarvis, Casual)
- [x] **60+ AI tools across 12 categories**
- [x] **Persistent memory** - Conversations, preferences, notes, fitness data
- [x] **Multi-engine TTS** - gTTS, ElevenLabs, pyttsx3 with personality matching
- [x] **Bluetooth integration** - Music, calls, photo sync
- [x] **Camera photo/video capture** - Voice-activated
- [x] **Wake word detection** - Porcupine/Vosk/Energy-based
- [x] **Sleep/Active modes** - Power-efficient operation
- [x] **Interruptible AI** - Stop responses mid-speech
- [x] **Smart home control** - Home Assistant integration
- [x] **Productivity suite** - Notes, todos, reminders, timers
- [x] **Entertainment** - Music search, podcasts, books, movies
- [x] **Real-time info** - Weather, news, stocks, sports
- [x] **Quick tools** - Calculator, dates, random generators
- [x] **Translation** - 100+ languages, sign translation
- [x] **Fitness tracking** - Workouts, water logging
- [x] **Games & fun** - Trivia, jokes, riddles, quotes
- [x] **Privacy controls** - Private mode, data management

### 🔧 Future Enhancements
- [ ] Advanced object recognition (YOLO/TensorFlow)
- [ ] Face recognition with name recall
- [ ] Mobile companion app
- [ ] Power optimization for longer battery life
- [ ] Custom wake word training
- [ ] Offline LLM (Llama, Mistral)
- [ ] AR markers and navigation

## Troubleshooting

### Audio Issues

**Microphone not working:**
- Check device indices: `python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'[{i}] {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"`
- Update device indices in `config/config.yaml`
- Test recording: `arecord -D plughw:1,0 -d 5 test.wav`

**Echo or feedback issues:**
- Run echo reduction script: `./scripts/configure_audio_echo_reduction.sh`
- Lower TTS volume in `config/config.yaml` (try 0.5-0.6)
- Ensure speakers aren't too close to microphone
- Check that noise gate is enabled: `amixer -c 0 sget 'Noise Gate'`

**Interruption not working:**
- Echo reduction must be configured properly (see above)
- Speaker volume must be low enough that mic doesn't pick it up
- Verify interruption detection is running (check logs for "Interruption detected")
- Try speaking louder or closer to microphone

**Wake word not detecting:**
- Adjust sensitivity in `config/config.yaml` (try 0.5-0.7)
- Check Porcupine access key in `.env`
- Verify wake word is available: see `src/audio/wake_word.py` for supported keywords
- Test microphone: `arecord -D plughw:1,0 -d 5 test.wav && aplay test.wav`

### Camera Issues
- Ensure camera is enabled: `sudo raspi-config`
- Check connection: `libcamera-hello`
- Verify camera interface is enabled in `/boot/config.txt`

### API Issues
- Verify API keys in `.env` file
- Check internet connection for online services (Google Speech, OpenAI, Home Assistant)
- Test API keys directly with curl or API clients
- Check API quotas and limits

### Sleep Mode Issues
- If wake word stops working after timeout, check logs for "SLEEP mode" messages
- Restart the application to reset state
- Adjust sleep timeout in `src/main.py` (default: 60 seconds)

## Documentation

### Quick Start
- **[QUICK_START.md](QUICK_START.md)** - Get up and running in minutes
- **[claude.md](claude.md)** - Project planning and feature overview

### Features & Guides
- **[AI_ASSISTANT_FEATURES.md](AI_ASSISTANT_FEATURES.md)** - Complete AI assistant feature summary
- **[VISION_FEATURES.md](VISION_FEATURES.md)** - 👁️ Computer vision capabilities guide
- **[BLUETOOTH_COMPLETE.md](BLUETOOTH_COMPLETE.md)** - Bluetooth integration reference
- **[docs/ai_assistant_guide.md](docs/ai_assistant_guide.md)** - Comprehensive AI assistant guide
- **[docs/PERSONALITY_EXAMPLES.md](docs/PERSONALITY_EXAMPLES.md)** - Personality examples and comparisons
- **[docs/wake_word_setup.md](docs/wake_word_setup.md)** - Wake word detection setup
- **[docs/elevenlabs_setup.md](docs/elevenlabs_setup.md)** - ElevenLabs premium voices setup

### Configuration
- **[config/config.yaml](config/config.yaml)** - Main configuration file
- **[.env.example](.env.example)** - API keys template

## Contributing

This is a personal project, but suggestions and improvements are welcome!

## License

MIT License - See LICENSE file for details

## External Resources

- [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use)
- [OpenAI API Documentation](https://platform.openai.com/docs/)
- [Vosk Speech Recognition](https://alphacephei.com/vosk/)
- [Picovoice Porcupine](https://picovoice.ai/platform/porcupine/)
- [pyttsx3 Documentation](https://pyttsx3.readthedocs.io/)
