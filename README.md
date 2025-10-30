# Smart Glasses Project

Voice-activated smart glasses powered by Raspberry Pi Zero with Ray-Ban Meta functionality and more.

## Features

### Core Features
- **👁️ COMPUTER VISION** - AI can SEE what you're looking at and describe it!
- **📖 Text Reading (OCR)** - Read signs, menus, labels, documents aloud
- **🔍 Object Identification** - Identify objects and get information about them
- **🎤 Voice-activated AI assistant** with 5 unique personalities (Friendly, Professional, Witty, Jarvis, Casual)
- **🔊 Wake word detection** (Porcupine, Vosk, or Energy-based)
- **🧠 Persistent memory** - Remembers conversations and preferences across sessions
- **🛠️ 13 AI tools** - Camera, vision, timers, Bluetooth, preferences, and more
- **🎙️ Premium voices** - ElevenLabs natural TTS with personality matching
- **📸 Photo and video capture** via voice commands
- **📱 Bluetooth integration** - Music streaming, phone calls, photo sync
- **⚡ Context awareness** - Knows time, location, and user preferences

### Upcoming Features
- Bluetooth audio streaming
- Music playback
- Object recognition and OCR
- Real-time translation
- Smart home integration

## Hardware Requirements

- Raspberry Pi Zero W
- Sound/Mic HAT
- Raspberry Pi Camera Module
- Portable battery pack
- Eyeglass frame for mounting

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

Follow your sound HAT's specific setup instructions. Common steps:

```bash
# Test microphone
arecord -l

# Test speaker
aplay -l

# Record test audio
arecord -D plughw:1,0 -d 5 test.wav

# Play test audio
aplay test.wav
```

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

1. **Startup**: Run the application, wait for "Smart glasses ready"
2. **Wake Word**: Say "computer" (or your configured keyword)
3. **Command**: After the beep, speak naturally
4. **Response**: The AI responds with personality and takes actions

### Voice Commands

**Basic Interaction:**
- "What time is it?"
- "What's the weather?" (via AI knowledge)
- "Tell me a joke"
- "Shutdown"

**Vision Commands (AI can SEE!):**
- "What am I looking at?"
- "Describe what you see"
- "Read this menu"
- "What does this sign say?"
- "What is this object?"
- "How many people do you see?"
- "What color is this?"

**Camera Commands:**
- "Take a photo"
- "Record a video"
- "Record a 15 second video"

**Timers:**
- "Set a timer for 5 minutes"
- "Set a timer for my tea"

**Memory (persistent across sessions):**
- "Remember that my name is Tony"
- "My favorite coffee is espresso"
- "What's my name?"
- "What's my favorite coffee?"

**The AI will:**
- Automatically use tools when needed
- Remember your preferences forever
- Respond with chosen personality
- Maintain conversation context

## Project Structure

```
smart-glasses/
├── src/
│   ├── audio/              # Audio input/output
│   │   ├── audio_manager.py
│   │   ├── wake_word.py
│   │   └── speech_recognition.py
│   ├── camera/             # Camera operations
│   │   └── camera_manager.py
│   ├── assistant/          # AI assistant
│   │   └── ai_assistant.py
│   ├── bluetooth/          # Bluetooth (TODO)
│   ├── vision/             # Computer vision (TODO)
│   └── main.py             # Main application
├── config/                 # Configuration files
├── photos/                 # Captured photos
├── videos/                 # Recorded videos
├── logs/                   # Application logs
└── tests/                  # Unit tests
```

## Development Status

### Implemented
- [x] Project structure
- [x] Configuration system
- [x] Audio input/output
- [x] Speech recognition (Google Speech API)
- [x] **👁️ COMPUTER VISION** - Scene description, OCR, object ID
- [x] **AI assistant with 5 personalities** (Friendly, Professional, Witty, Jarvis, Casual)
- [x] **13 AI tools** (vision, camera, Bluetooth, timers, preferences)
- [x] **Persistent memory** (conversations & preferences)
- [x] **ElevenLabs premium voices** with personality matching
- [x] **Bluetooth integration** (music, calls, photo sync)
- [x] Camera photo/video capture (voice-activated)
- [x] Wake word detection (Porcupine/Vosk/Energy)
- [x] **Context awareness** (time, location, user info)

### In Progress
- [ ] Offline speech recognition (Vosk)
- [ ] Bluetooth audio streaming

### Planned
- [ ] Object recognition
- [ ] OCR text reading
- [ ] Real-time translation
- [ ] Face recognition
- [ ] Mobile companion app
- [ ] Power optimization
- [ ] Custom wake word training

## Troubleshooting

### Audio Issues
- Check device indices with `python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'[{i}] {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"`
- Update device indices in `config/config.yaml`

### Camera Issues
- Ensure camera is enabled: `sudo raspi-config`
- Check connection: `libcamera-hello`

### API Issues
- Verify API keys in `.env`
- Check internet connection for online services

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
