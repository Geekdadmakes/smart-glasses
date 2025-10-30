# Quick Start Guide

Get your smart glasses up and running in minutes!

## 1. Setup on Raspberry Pi

```bash
# Clone or copy the project to your Pi
cd smart-glasses

# Run setup script
bash scripts/setup.sh

# This installs all dependencies
```

## 2. Configure API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your keys
nano .env
```

**Required:**
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` - For AI assistant
- `PORCUPINE_ACCESS_KEY` - For wake word detection (get free at https://console.picovoice.ai/)

**Optional (Highly Recommended):**
- `ELEVENLABS_API_KEY` - For premium natural voices (get at https://elevenlabs.io/)

## 3. Test Audio

```bash
# Test your microphone and speakers
python3 scripts/test_audio.py

# Note the device indices for your mic/speaker
```

## 4. Update Audio Config

Edit `config/config.yaml`:

```yaml
audio:
  mic_device_index: 1  # Use index from test_audio.py
  speaker_device_index: 1  # Use index from test_audio.py
```

## 5. Test Wake Word Detection

```bash
# Test wake word detection
python3 scripts/test_wake_word.py
```

Say "computer" to test (this is the default wake word).

## 6. Run the Application

```bash
python3 src/main.py
```

That's it! Your smart glasses are ready.

## Quick Testing Without Porcupine

If you want to test quickly without setting up Porcupine:

1. Edit `config/config.yaml`:
```yaml
wake_word:
  method: "energy"  # Simple testing mode
```

2. Run `python3 scripts/test_wake_word.py`

3. Speak loudly or clap to trigger detection

**Note:** Energy mode is for testing only. Use Porcupine for production.

## Usage

1. Say the wake word: **"computer"** (or your configured keyword)
2. Wait for the beep
3. Speak your command:
   - "What's the weather?"
   - "Take a photo"
   - "Record a video"
   - "Set a timer for 5 minutes"
   - "Tell me a joke"
   - "Shutdown"

## Troubleshooting

**No wake word detection:**
- Check `PORCUPINE_ACCESS_KEY` in `.env`
- Verify microphone is working: `python3 scripts/test_audio.py`
- Increase sensitivity in `config/config.yaml`

**No audio output:**
- Check speaker device index in config
- Test speakers: `aplay test.wav`

**Camera not working:**
- Enable camera: `sudo raspi-config` → Camera → Enable
- Test: `libcamera-hello`

## Next Steps

- Read `docs/wake_word_setup.md` for detailed wake word configuration
- Customize settings in `config/config.yaml`
- Add Bluetooth audio streaming
- Implement offline speech recognition

## Available Wake Words (Porcupine)

Built-in keywords you can use for free:
- `computer` ⭐ (default)
- `jarvis`
- `alexa`
- `ok google`
- `hey google`
- `porcupine`
- `terminator`

Configure in `config/config.yaml`:
```yaml
wake_word:
  keyword: "jarvis"  # Change to any supported keyword
```

## Documentation

- `README.md` - Full project documentation
- `docs/wake_word_setup.md` - Detailed wake word setup
- `claude.md` - Project planning and features
- `config/config.yaml` - All configuration options

## Support

Issues? Check:
1. Device indices are correct in config
2. API keys are set in `.env`
3. Dependencies are installed
4. Camera/audio hardware is enabled

For more help, see the full README.md
