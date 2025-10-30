# ElevenLabs TTS Setup Guide

Complete guide to setting up premium ElevenLabs voices for your smart glasses.

## Why ElevenLabs?

ElevenLabs provides **incredibly natural, human-like voices** that are far superior to traditional TTS:

- **Natural prosody** - Sounds like a real person speaking
- **Emotion and expression** - Voices convey personality
- **Multiple languages** - 29+ languages supported
- **Voice cloning** - Create custom voices (premium)
- **Low latency** - Fast generation for real-time use

Perfect for smart glasses where you'll be hearing the voice all day!

## Quick Setup

### 1. Get API Key

1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for an account (free tier available)
3. Navigate to your profile → API Keys
4. Generate a new API key
5. Copy the key

### 2. Add to Environment

Edit your `.env` file:

```bash
ELEVENLABS_API_KEY=your_actual_api_key_here
```

### 3. Configure Engine

Edit `config/config.yaml`:

```yaml
tts:
  engine: "elevenlabs"  # Change from pyttsx3 to elevenlabs
```

### 4. Install Package

```bash
pip3 install elevenlabs pygame
```

### 5. Test It

```bash
python3 src/main.py
```

Say the wake word and speak - you should hear a natural voice!

---

## Default Voice Mapping

Each personality is pre-configured with a great ElevenLabs voice:

| Personality | Voice | Description | Voice ID |
|------------|-------|-------------|----------|
| **Friendly** | Bella | Warm, upbeat female | `EXAVITQu4vr4xnSDxMaL` |
| **Professional** | Adam | Clear, professional male | `pNInz6obpgDQGcFmaJgB` |
| **Witty** | Josh | Energetic, expressive male | `TxGEqnHWrfWFTfGW9XjX` |
| **Jarvis** | Arnold | British, sophisticated male | `VR6AewLTigWG4xSOukaG` |
| **Casual** | Freya | Relaxed, friendly female | `jsCqWAovK2LkecY7zXl4` |

These are carefully selected to match each personality's characteristics.

---

## Custom Voice Selection

Want to use different voices? You can customize each personality!

### Step 1: Browse Voice Library

1. Go to [ElevenLabs Voice Library](https://elevenlabs.io/app/voice-library)
2. Listen to different voices
3. Find ones you like for each personality

### Step 2: Get Voice ID

**From Voice Library:**
- Click on a voice
- Look for the voice ID in the URL or details
- Format: `AbCd1234EfGh5678IjKl`

**From Your Voices:**
- Go to [Voice Lab](https://elevenlabs.io/app/voice-lab)
- Click on a voice you own
- Copy the voice ID

### Step 3: Configure Voice IDs

Add to your `.env` file:

```bash
# Custom voice for Jarvis personality - use a British voice
ELEVENLABS_VOICE_JARVIS=VR6AewLTigWG4xSOukaG

# Custom voice for Friendly personality - use an upbeat voice
ELEVENLABS_VOICE_FRIENDLY=EXAVITQu4vr4xnSDxMaL

# Add more as needed...
```

### Step 4: Restart Application

```bash
python3 src/main.py
```

Your new voices will be used automatically!

---

## Voice Recommendations

### For Jarvis Personality

**Best Matches:**
- **Arnold** (British, sophisticated) - Default
- **Harry** (British narrator)
- **George** (British, warm)
- **Callum** (British, professional)

**Why:** Jarvis should sound British and refined, like Tony Stark's AI.

### For Friendly Personality

**Best Matches:**
- **Bella** (Warm, expressive) - Default
- **Rachel** (Upbeat, friendly)
- **Domi** (Energetic, young)
- **Elli** (Friendly, clear)

**Why:** Friendly needs an upbeat, warm voice that makes you smile.

### For Professional Personality

**Best Matches:**
- **Adam** (Professional, clear) - Default
- **Sam** (Neutral, reliable)
- **Antoni** (Formal, precise)
- **Patrick** (Professional narrator)

**Why:** Professional needs clarity and formality.

### For Witty Personality

**Best Matches:**
- **Josh** (Energetic, expressive) - Default
- **Clyde** (Dynamic range)
- **Ethan** (Playful)

**Why:** Witty needs expressiveness for humor and jokes.

### For Casual Personality

**Best Matches:**
- **Freya** (Relaxed, friendly) - Default
- **Nicole** (Casual American)
- **Natasha** (Laid-back)

**Why:** Casual needs a relaxed, conversational tone.

---

## Advanced Settings

### Voice Settings

You can customize voice parameters in `src/audio/tts_manager.py`:

```python
VoiceSettings(
    stability=0.5,          # 0.0-1.0: Lower = more variable, Higher = more stable
    similarity_boost=0.75,  # 0.0-1.0: How closely to match the original voice
    style=0.0,              # 0.0-1.0: Style exaggeration
    use_speaker_boost=True  # Boost clarity
)
```

**Recommended Settings by Use Case:**

**For Jarvis (British, sophisticated):**
```python
stability=0.6,           # Stable and consistent
similarity_boost=0.8,    # Close to original voice
style=0.1,              # Subtle style
use_speaker_boost=True
```

**For Witty (Expressive, dynamic):**
```python
stability=0.3,           # More variation for humor
similarity_boost=0.7,
style=0.4,              # More expressive
use_speaker_boost=True
```

**For Professional (Clear, consistent):**
```python
stability=0.8,           # Very stable
similarity_boost=0.9,    # Stick to voice characteristics
style=0.0,              # No exaggeration
use_speaker_boost=True
```

### Model Selection

Two models available:

1. **eleven_monolingual_v1** (default)
   - English only
   - Fastest
   - Great quality
   - Lowest latency

2. **eleven_multilingual_v2**
   - 29+ languages
   - Slightly slower
   - Use for non-English

Change in `src/audio/tts_manager.py`:
```python
model="eleven_multilingual_v2"
```

---

## Voice Cloning (Premium)

With ElevenLabs premium, you can clone your own voice or create custom voices!

### Clone Your Voice

1. Go to [Voice Lab](https://elevenlabs.io/app/voice-lab)
2. Click "Add Voice" → "Instant Voice Cloning"
3. Upload 1-5 minutes of clean audio
4. Name your voice
5. Copy the voice ID
6. Add to `.env`:

```bash
ELEVENLABS_VOICE_JARVIS=your_cloned_voice_id_here
```

### Use Cases

- **Your own voice** as the assistant
- **A friend's voice** (with permission!)
- **Character voices** for themed experiences
- **Professional voice actor** recordings

---

## Pricing & Limits

### Free Tier
- **10,000 characters/month**
- ~3-5 minutes of speech/month
- Access to pre-made voices
- Basic quality

**Good for:** Testing, light use

### Starter ($5/month)
- **30,000 characters/month**
- ~10-15 minutes/month
- Voice cloning (1 voice)
- Commercial use

**Good for:** Regular smart glasses use

### Creator ($22/month)
- **100,000 characters/month**
- ~30-50 minutes/month
- Voice cloning (10 voices)
- Higher quality

**Good for:** Heavy daily use

### Pro ($99/month)
- **500,000 characters/month**
- ~150-250 minutes/month
- Voice cloning (30 voices)
- Priority access

**Good for:** Professional/commercial use

### Usage Estimate for Smart Glasses

**Light use (testing, occasional):**
- ~50 responses/day × 30 characters = 1,500 chars/day
- ~45,000 chars/month
- **Starter tier recommended**

**Regular use (daily assistant):**
- ~200 responses/day × 30 characters = 6,000 chars/day
- ~180,000 chars/month
- **Creator tier recommended**

**Check your usage:**
```bash
# View your character count in ElevenLabs dashboard
# https://elevenlabs.io/app/usage
```

---

## Performance on Raspberry Pi

### Latency

- **Generation time:** ~500ms-1s (cloud processing)
- **Download time:** ~200-500ms (depends on network)
- **Playback:** Real-time

**Total:** ~1-2 seconds from request to speech

### Optimization Tips

1. **Use WiFi** instead of cellular (faster download)
2. **Cache common phrases** (future enhancement)
3. **Pre-generate startup sounds**
4. **Monitor usage** to stay within limits

### Comparison to Other TTS

| Engine | Quality | Speed | Offline | Cost |
|--------|---------|-------|---------|------|
| pyttsx3 | ⭐⭐ | Instant | ✅ | Free |
| gTTS | ⭐⭐⭐ | ~1s | ❌ | Free |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | ~1-2s | ❌ | $5-99/mo |

**Verdict:** ElevenLabs is worth it for daily use - the quality difference is massive!

---

## Troubleshooting

### Error: "ELEVENLABS_API_KEY not found"

**Fix:**
1. Check `.env` file exists
2. Verify key is correct (no quotes, no spaces)
3. Restart application after adding key

### Error: "elevenlabs library not installed"

**Fix:**
```bash
pip3 install elevenlabs pygame
```

### Error: "Voice not found" or "Invalid voice ID"

**Fix:**
1. Verify voice ID in ElevenLabs dashboard
2. Check for typos in `.env`
3. Ensure voice is public or owned by you
4. Try default voice: `pNInz6obpgDQGcFmaJgB` (Adam)

### Poor Audio Quality

**Fixes:**
- Increase `similarity_boost` (0.7-0.9)
- Increase `stability` (0.5-0.8)
- Use `eleven_monolingual_v1` for English
- Check internet connection speed
- Try a different voice

### Voice Cuts Off or Stutters

**Fixes:**
- Check internet stability
- Increase buffer (modify code)
- Use wired Ethernet instead of WiFi
- Reduce other network usage

### Running Out of Characters

**Solutions:**
1. Upgrade tier
2. Make responses shorter (adjust system prompt)
3. Use pyttsx3 for non-critical responses
4. Hybrid mode: ElevenLabs for important, pyttsx3 for simple

---

## Hybrid Mode (Advanced)

Use ElevenLabs for important responses, fallback to pyttsx3 for simple ones:

```python
# In src/audio/tts_manager.py
def speak(self, text):
    # Use ElevenLabs for longer, important responses
    if len(text) > 50 or self.is_important_response(text):
        self._speak_elevenlabs(text)
    else:
        # Use free pyttsx3 for short confirmations
        self._speak_pyttsx3(text)
```

---

## Voice Testing

### Test Individual Voices

Create a test script:

```python
from elevenlabs import generate, play, set_api_key
import os
from dotenv import load_dotenv

load_dotenv()
set_api_key(os.getenv('ELEVENLABS_API_KEY'))

# Test different voices
voices = {
    'Bella': 'EXAVITQu4vr4xnSDxMaL',
    'Adam': 'pNInz6obpgDQGcFmaJgB',
    'Arnold': 'VR6AewLTigWG4xSOukaG'
}

test_text = "Hello! This is a test of my voice for the smart glasses assistant."

for name, voice_id in voices.items():
    print(f"Testing {name}...")
    audio = generate(text=test_text, voice=voice_id)
    play(audio)
    input("Press Enter for next voice...")
```

### Test Your Setup

```bash
# Run application
python3 src/main.py

# Say wake word
# Then say: "Tell me a short story"

# This will generate enough speech to test quality and latency
```

---

## Best Practices

1. **Choose the right voice** - Listen to many options before deciding
2. **Match personality** - Voice should fit the assistant's character
3. **Monitor usage** - Check dashboard regularly
4. **Optimize prompts** - Shorter responses = less character usage
5. **Test thoroughly** - Try different phrases, lengths, contexts
6. **Update voices seasonally** - Keep it fresh!
7. **Get user feedback** - Ask friends which voice they prefer

---

## Next Steps

1. **Set up your API key** in `.env`
2. **Try default voices** with each personality
3. **Browse voice library** for favorites
4. **Customize voice IDs** for perfect match
5. **Adjust settings** for optimal quality
6. **Monitor usage** and upgrade tier if needed

---

## Resources

- [ElevenLabs Dashboard](https://elevenlabs.io/app)
- [Voice Library](https://elevenlabs.io/app/voice-library)
- [Voice Lab (Cloning)](https://elevenlabs.io/app/voice-lab)
- [API Documentation](https://elevenlabs.io/docs)
- [Pricing](https://elevenlabs.io/pricing)
- [Python SDK](https://github.com/elevenlabs/elevenlabs-python)

---

## Summary

ElevenLabs integration gives your smart glasses **incredibly natural, human-like voices** that make the experience delightful. The default voice mapping is carefully chosen for each personality:

- **Jarvis** → Arnold (British, sophisticated)
- **Friendly** → Bella (warm, upbeat)
- **Professional** → Adam (clear, formal)
- **Witty** → Josh (expressive, energetic)
- **Casual** → Freya (relaxed, friendly)

Just add your API key, and you're ready to go! 🎙️✨
