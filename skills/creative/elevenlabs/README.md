# ElevenLabs Audio Generation Skill

AI-powered audio generation using ElevenLabs API - text-to-speech, sound effects, and music creation.

## Overview

This skill enables Claude Code to generate professional-quality audio using ElevenLabs API. Create lifelike text-to-speech in 32 languages with 100+ voices, generate custom sound effects for games and videos, and compose royalty-free music from text descriptions. Perfect for content creation, game development, e-learning, podcasts, and multimedia production.

## Quick Start

### Installation

```bash
# Install the skill
knowhow install elevenlabs

# Or copy to your project
cp -r skills/creative/elevenlabs .claude/skills/
```

### Requirements

**API Key:**
```bash
# Get API key from https://elevenlabs.io/app/settings/api-keys
export ELEVENLABS_API_KEY="your-api-key-here"
```

**Python Dependencies:**
```bash
pip install elevenlabs pydub python-dotenv
```

**System:**
- Python 3.8+
- ffmpeg (for audio processing with pydub)
- Internet connection

### Basic Usage

Once installed, simply ask Claude to generate audio:

```
"Convert this text to speech using a professional voice"
"Generate footstep sound effects for my game"
"Create upbeat background music for my video"
"Make an audiobook narration of this chapter"
```

Claude will automatically:
1. Recognize the audio generation request
2. Select the appropriate model/voice
3. Generate the audio
4. Save it and show you the result

## Capabilities

### 1. Text-to-Speech (Voice Generation)

**Features:**
- 🗣️ **100+ Professional Voices** - Male, female, various ages and accents
- 🌍 **32 Languages** - Multilingual support
- 🎭 **Emotional & Natural** - Lifelike intonation and expression
- ⚡ **Real-time Streaming** - Ultra-low 75ms latency
- 🎤 **Custom Voice Cloning** - Create voices from audio samples
- 👥 **Multi-speaker Dialogue** - Generate conversations

**Models:**
- **Eleven Multilingual v2** - Highest quality, 29 languages
- **Eleven Flash v2.5** - Ultra-low latency, 50% cheaper
- **Eleven Turbo v2.5** - Balanced quality and speed

**Use Cases:**
- Audiobooks and narration
- Video voice-overs
- E-learning courses
- Podcast production
- IVR and voice assistants
- Accessibility features

### 2. Sound Effects Generation

**Features:**
- 🎮 **Game Audio** - Combat, UI, environmental sounds
- 🎬 **Video Production** - Transitions, ambiences, effects
- 🔊 **Custom Duration** - 0.3 to 22 seconds
- 🔁 **Looping Support** - Seamless audio loops
- 🎚️ **Prompt Control** - Adjust creative interpretation

**Use Cases:**
- Video game sound design
- YouTube video production
- Mobile app UI sounds
- Podcast transitions
- Motion graphics audio

### 3. Music Generation

**Features:**
- 🎵 **Text-to-Music** - Generate tracks from descriptions
- 🎹 **Vocal & Instrumental** - Both singing and instrumental
- 🎼 **Multiple Genres** - Pop, electronic, orchestral, jazz, and more
- ⏱️ **Custom Duration** - Control track length
- 📜 **Composition Plans** - Structured music blueprints
- 💰 **Royalty-Free** - Commercial usage rights

**Requirements:**
- Paid ElevenLabs subscription
- Music generation not available on free tier

**Use Cases:**
- Video backgrounds
- Game soundtracks
- Podcast themes
- Commercial advertising
- Content creation

## Documentation

### Core Files

- **[SKILL.md](SKILL.md)** - Complete skill implementation with instructions
- **README.md** - This file, overview and quick start

### References

- **[references/text-to-speech.md](references/text-to-speech.md)** - Complete TTS documentation
  - Models and voices
  - API usage
  - Output formats
  - Multi-speaker dialogue
  - Supported languages

- **[references/sound-effects.md](references/sound-effects.md)** - Sound effects generation guide
  - Prompt engineering
  - Duration guidelines
  - Batch generation
  - Use case examples

- **[references/music-generation.md](references/music-generation.md)** - Music creation documentation
  - Genre-specific prompts
  - Composition plans
  - Content policy
  - Advanced techniques

### Examples

- **[examples/complete-examples.md](examples/complete-examples.md)** - 10 complete examples
  - Audiobook narration
  - Multi-language content
  - Game sound effects
  - Podcast production
  - Video workflows

## Common Use Cases

### Audiobook Production

```python
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key="your-key")

audio = client.text_to_speech.convert(
    text="Chapter text here...",
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George - narrative voice
    model_id="eleven_multilingual_v2"
)

# Save to file
with open("chapter.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### Game Sound Effects

```python
audio = client.text_to_sound_effects.convert(
    text="sword whooshing through air, fast combat swing",
    duration_seconds=1.5
)

with open("sword_swing.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

### Background Music

```python
audio = client.music_generation.compose(
    prompt="""Upbeat corporate background music with piano and strings,
    professional and inspiring""",
    music_length_ms=60000  # 60 seconds
)

with open("background.mp3", "wb") as f:
    for chunk in audio:
        f.write(chunk)
```

## Key Features

### Voice Selection

**Popular Voices:**
- **George** (`JBFqnCBsd6RMkjVDRZzb`) - Male, narrative
- **Rachel** (`21m00Tcm4TlvDq8ikWAM`) - Female, calm
- **Josh** (`TxGEqnHWrfWFTfGW9XjX`) - Male, energetic
- **Bella** (`EXAVITQu4vr4xnSDxMaL`) - Female, expressive

List all voices:
```python
voices = client.voices.get_all()
for voice in voices.voices:
    print(f"{voice.name}: {voice.voice_id}")
```

### Streaming Audio

```python
from elevenlabs import stream

audio_stream = client.text_to_speech.convert_as_stream(
    text="This is streamed in real-time",
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_flash_v2_5"  # Low latency
)

stream(audio_stream)  # Play immediately
```

### Multi-Speaker Dialogue

```python
speakers = [
    ("JBFqnCBsd6RMkjVDRZzb", "Hello, how are you?"),
    ("21m00Tcm4TlvDq8ikWAM", "I'm doing great, thanks!"),
]

# Generate and combine (see examples for full implementation)
```

## Pricing & Limits

### Free Tier
- ✅ Text-to-speech (10,000 characters/month)
- ✅ Sound effects
- ❌ Music generation (paid only)

### Paid Tiers
- ✅ Higher character quotas
- ✅ Music generation
- ✅ Commercial usage rights
- ✅ Priority processing

Check current pricing: https://elevenlabs.io/pricing

## Best Practices

### Text-to-Speech

1. **Choose Right Model:**
   - Quality priority → Multilingual v2
   - Speed priority → Flash v2.5
   - Balanced → Turbo v2.5

2. **Select Appropriate Voice:**
   - Match voice to content type
   - Test multiple voices
   - Use voice labels to filter

3. **Optimize for Use Case:**
   - Long content: Standard generation
   - Real-time: Streaming with Flash
   - Dialogue: Separate audio per speaker

### Sound Effects

1. **Be Descriptive:**
   - "footsteps on gravel, slow walking pace"
   - "creaky door opening, horror atmosphere"
   - "explosion with debris, action movie"

2. **Set Appropriate Duration:**
   - UI sounds: 0.3-0.8 seconds
   - Actions: 1-3 seconds
   - Ambiences: 5-20 seconds

3. **Adjust Prompt Influence:**
   - 0.5 (default): Balanced
   - 0.7-1.0: More literal
   - 0.0-0.3: More creative

### Music Generation

1. **Detailed Prompts:**
   - Specify genre, instruments, mood
   - Include use case context
   - Describe structure if important

2. **Avoid Copyrighted Material:**
   - No artist or band names
   - No song titles
   - Use generic descriptions

3. **Plan Duration:**
   - Short clips: 10-30 seconds
   - Full tracks: 60-120 seconds
   - Consider processing time

## Troubleshooting

### API Key Issues

```bash
# Verify API key is set
echo $ELEVENLABS_API_KEY

# Set if missing
export ELEVENLABS_API_KEY="your-key-here"
```

### Quota Exceeded

- Check usage: https://elevenlabs.io/app/usage
- Upgrade plan if needed
- Monitor character count

### Poor Audio Quality

- Use higher bitrate format
- Try different voice
- Use Multilingual v2 model
- Check input text quality

### Music Generation Error

- Verify paid subscription
- Remove copyrighted references
- Check prompt for restricted content

## Model Selection Guide

**Text-to-Speech:**
```
Need highest quality? → eleven_multilingual_v2
Need low latency?     → eleven_flash_v2_5
General use?          → eleven_turbo_v2_5
Cost-conscious?       → eleven_flash_v2_5
```

**Sound Effects:**
- All use `eleven_text_to_sound_v2`
- Adjust duration and prompt_influence

**Music:**
- Requires paid subscription
- Use composition plans for complex tracks

## Integration Examples

### With Python Scripts

```python
#!/usr/bin/env python3
import os
from elevenlabs.client import ElevenLabs

client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

# Your audio generation code
```

### With Web Applications

```python
# Flask example
from flask import Flask, send_file
from elevenlabs.client import ElevenLabs

app = Flask(__name__)
client = ElevenLabs()

@app.route("/generate/<text>")
def generate(text):
    audio = client.text_to_speech.convert(text=text, ...)
    return send_file(audio, mimetype="audio/mpeg")
```

### Batch Processing

```python
texts = ["Text 1", "Text 2", "Text 3"]

for i, text in enumerate(texts):
    audio = client.text_to_speech.convert(text=text, ...)
    with open(f"output_{i}.mp3", "wb") as f:
        for chunk in audio:
            f.write(chunk)
```

## Related Skills

- `image-generation` - AI image creation (Gemini, DALL-E)
- `python-plotting` - Audio visualization
- `scientific-writing` - Generate narration text
- `python-best-practices` - Clean audio processing code

## Resources

### Official Documentation
- **API Docs**: https://elevenlabs.io/docs
- **Python SDK**: https://github.com/elevenlabs/elevenlabs-python
- **API Reference**: https://elevenlabs.io/docs/api-reference

### Tools & Dashboards
- **Voice Library**: https://elevenlabs.io/voice-library
- **Usage Dashboard**: https://elevenlabs.io/app/usage
- **API Keys**: https://elevenlabs.io/app/settings/api-keys

### Pricing & Plans
- **Pricing**: https://elevenlabs.io/pricing
- **Feature Comparison**: https://elevenlabs.io/pricing#compare

### Community
- **Showcase**: https://elevenlabs.io/showcase
- **Discord**: Join the ElevenLabs community
- **GitHub**: https://github.com/elevenlabs

## Contributing

Improvements welcome:
- Additional example use cases
- Prompt engineering techniques
- Integration patterns
- Error handling improvements
- Performance optimizations

## Version History

- **v1.0.0** (2025-01-23) - Initial release
  - Text-to-speech (32 languages, 3 models)
  - Sound effects generation
  - Music generation (paid users)
  - Comprehensive documentation
  - 10 complete examples

## Support

For issues or questions:
1. Check the [examples](examples/) directory
2. Review model-specific documentation
3. Consult [ElevenLabs docs](https://elevenlabs.io/docs)
4. Open an issue in the knowhow repository

---

**Ready to create amazing audio!** 🎵🎙️🔊

*Using ElevenLabs API for professional audio generation*
