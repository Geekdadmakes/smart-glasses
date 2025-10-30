# Wake Word Detection Setup Guide

This guide will help you set up wake word detection for your smart glasses.

## Overview

The smart glasses support three wake word detection methods:

1. **Porcupine** (Recommended) - Production-ready, accurate, requires free API key
2. **Energy Detection** (Testing only) - Simple, no setup, not reliable
3. **Vosk** (Advanced) - Fully offline, requires model download

## Method 1: Porcupine (Recommended)

Porcupine by Picovoice is the recommended method for production use. It's highly accurate, lightweight, and optimized for embedded devices like the Raspberry Pi Zero.

### Setup Steps

#### 1. Get Free Access Key

1. Go to [Picovoice Console](https://console.picovoice.ai/)
2. Sign up for a free account
3. Create a new access key
4. Copy the access key

#### 2. Add to Environment File

Edit your `.env` file and add:

```bash
PORCUPINE_ACCESS_KEY=your_access_key_here
```

#### 3. Install Porcupine

```bash
pip3 install pvporcupine
```

#### 4. Configure Keyword

Edit `config/config.yaml`:

```yaml
wake_word:
  enabled: true
  method: "porcupine"
  keyword: "computer"  # See available keywords below
  sensitivity: 0.5
```

### Available Porcupine Keywords

Porcupine comes with built-in keywords (free tier):

- `computer` (recommended for "hey glasses")
- `jarvis`
- `alexa`
- `ok google`
- `hey google`
- `hey siri`
- `porcupine`
- `terminator`
- `americano`
- `blueberry`
- `bumblebee`
- `grapefruit`
- `grasshopper`

**Note**: The config maps your chosen keyword to a Porcupine built-in. For example:
- `"hey glasses"` → uses `"computer"`
- `"hey jarvis"` → uses `"jarvis"`

For truly custom wake words, you need Porcupine's paid tier.

### Test Porcupine

```bash
python3 scripts/test_wake_word.py
```

Say "computer" (or your chosen keyword) to test detection.

## Method 2: Energy Detection (Testing Only)

Simple energy-based detection for testing audio setup. **NOT recommended for production** - triggers on any loud sound.

### Setup Steps

#### 1. Configure Method

Edit `config/config.yaml`:

```yaml
wake_word:
  enabled: true
  method: "energy"
  keyword: "hey glasses"  # Not actually used
  sensitivity: 0.5  # Not used for energy detection
```

#### 2. Test

```bash
python3 scripts/test_wake_word.py
```

Speak loudly or clap to trigger detection.

### Use Cases

- Testing audio input is working
- Debugging microphone setup
- Quick prototyping

## Method 3: Vosk (Advanced)

Vosk provides fully offline wake word detection using speech recognition models.

### Setup Steps

#### 1. Download Model

```bash
# Create models directory
mkdir -p models

# Download small English model (40MB)
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Extract
unzip vosk-model-small-en-us-0.15.zip

# Clean up
rm vosk-model-small-en-us-0.15.zip
cd ..
```

#### 2. Install Vosk

```bash
pip3 install vosk
```

#### 3. Configure

Edit `config/config.yaml`:

```yaml
wake_word:
  enabled: true
  method: "vosk"
  keyword: "hey glasses"  # Any custom phrase
  sensitivity: 0.5
```

Add to `.env`:

```bash
VOSK_MODEL_PATH=models/vosk-model-small-en-us-0.15
```

#### 4. Test

```bash
python3 scripts/test_wake_word.py
```

### Pros & Cons

**Pros**:
- Fully offline
- Custom wake words
- No API key needed
- Free

**Cons**:
- Larger memory footprint
- May be slower on Pi Zero
- Less accurate than Porcupine
- Requires model download

## Comparison

| Method | Accuracy | Speed | Offline | Setup | Pi Zero |
|--------|----------|-------|---------|-------|---------|
| Porcupine | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ | Easy | ✅ |
| Energy | ⭐ | ⭐⭐⭐⭐⭐ | ✅ | None | ✅ |
| Vosk | ⭐⭐⭐ | ⭐⭐⭐ | ✅ | Medium | ⚠️ |

## Troubleshooting

### Porcupine Issues

**Error: "PORCUPINE_ACCESS_KEY not found"**
- Check `.env` file exists and contains your key
- Make sure no quotes around the key in `.env`
- Restart your terminal/application after adding the key

**Error: "pvporcupine not installed"**
```bash
pip3 install pvporcupine
```

**No detection happening**
- Try increasing sensitivity in config.yaml (0.0 to 1.0)
- Check microphone is working: `python3 scripts/test_audio.py`
- Make sure you're using a supported keyword

### Vosk Issues

**Error: "Model not found"**
- Check model path in `.env`
- Verify model was extracted correctly
- Use absolute path if relative path doesn't work

**Slow performance on Pi Zero**
- Use the smallest model (vosk-model-small-en-us-0.15)
- Consider using Porcupine instead

### General Issues

**No audio input**
```bash
# List audio devices
python3 scripts/test_audio.py

# Update device index in config/config.yaml
audio:
  mic_device_index: 1  # Use correct index
```

**High CPU usage**
- Normal for continuous wake word detection
- Porcupine is most efficient
- Energy detection is simplest

## Performance Tips

### For Raspberry Pi Zero

1. **Use Porcupine** - Most optimized for embedded devices
2. **Adjust sensitivity** - Lower sensitivity = less false positives
3. **Disable unnecessary features** - Comment out unused modules
4. **Monitor CPU** - Use `htop` to check resource usage

### Battery Life

Wake word detection runs continuously and uses power. To optimize:

1. Lower sample rate if possible (check detector requirements)
2. Use Porcupine (most efficient)
3. Consider adding a physical button to enable/disable detection
4. Implement sleep mode after inactivity

## Next Steps

Once wake word detection is working:

1. Test in various environments (quiet, noisy, etc.)
2. Adjust sensitivity for your use case
3. Integrate with voice commands (already done in main.py)
4. Consider adding visual/audio feedback for activation

## Resources

- [Porcupine Documentation](https://picovoice.ai/docs/quick-start/porcupine/)
- [Vosk Models](https://alphacephei.com/vosk/models)
- [Project Issue Tracker](https://github.com/anthropics/claude-code/issues)
