# Video Storytelling Skill

AI-powered video storytelling that creates coherent multi-scene narratives with consistent visuals and narrated audio, assembled into professional MP4 videos.

## Overview

This skill combines image generation and audio synthesis to create complete video stories with:

- **Visual Consistency** - Characters and style remain coherent across all scenes
- **Narrative Audio** - Professional voice narration with emotional expression
- **Automated Assembly** - Images and audio merged into final MP4 video
- **Multi-Scene Stories** - Default 6 scenes (1 title + 5 story scenes)
- **Customizable** - Flexible story structure, characters, and visual styles

Perfect for creating educational content, children's stories, social media videos, presentations, and creative projects.

## Quick Start

### Installation

```bash
# Install the skill
knowhow install video-storytelling

# Or copy to your project
cp -r skills/creative/video-storytelling .claude/skills/
```

### Requirements

**Python Dependencies:**
```bash
pip install openai elevenlabs pillow requests
```

**System Requirements:**
- Python 3.8+
- ffmpeg (for video assembly)
- Internet connection

**API Keys:**
```bash
# Required for image generation (choose one)
export OPENAI_API_KEY="your-openai-key"  # For DALL-E
# OR
export GOOGLE_API_KEY="your-google-key"  # For Gemini

# Required for audio narration
export ELEVENLABS_API_KEY="your-elevenlabs-key"
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Google AI: https://makersuite.google.com/app/apikey
- ElevenLabs: https://elevenlabs.io/app/settings/api-keys

**Install ffmpeg:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify installation
ffmpeg -version
```

### Basic Usage

Once installed, simply ask Claude to create a video story:

```
"Create a video story about a robot learning to paint"

"Make a 6-scene educational video about photosynthesis"

"Create a children's story about a brave mouse exploring a library"
```

Claude will automatically:
1. Plan the story structure and characters
2. Generate consistent images for each scene
3. Create narrated audio with emotion
4. Assemble everything into final MP4 video

## Features

### Visual Consistency

**STYLE_LOCK** - Global visual rules:
- Aspect ratio: 1080×1080 (square, Instagram-ready)
- Lighting: Soft three-point lighting, warm 4500K
- Colors: Consistent palette with hex codes
- Style: Semi-realistic cartoon (customizable)
- Camera: 50mm lens, eye-level perspective

**CHARACTER_LOCK** - Maintain character appearance:
- Exact colors and features
- Consistent clothing and accessories
- Same art style across scenes
- Scale and proportions maintained

**Multi-Turn Generation** - Each scene references previous:
- Scene 0 establishes visual foundation
- Scenes 1-5 reference Scene 0 for consistency
- Prevents style drift and character changes

### Narrative Audio

**Text-to-Speech with ElevenLabs:**
- 100+ professional voices
- Emotional expression tags
- 32 languages supported
- Natural intonation and pacing

**Default Voices:**
- George (male narrator) - Warm professional
- Rachel (female narrator) - Calm soothing
- Josh (young male) - Energetic upbeat
- Bella (young female) - Bright expressive

**Emotion Tags:**
- neutral, happy, sad, surprised
- excited, focused, curious, triumphant
- And many more for nuanced delivery

### Video Assembly

**Automated Pipeline:**
- Concatenate all scene audio → merged_audio.mp3
- Calculate timing: total_duration / num_scenes
- Create video from images with equal timing
- Merge video and audio → final_video.mp4

**Output Specifications:**
- Resolution: 1080x1080 (square)
- Frame rate: 30 fps
- Video codec: H.264
- Audio codec: AAC (192 kbps)
- Duration: ~90-120 seconds typical
- File size: ~10-15 MB

## Default Story Structure

### 6 Scenes (Recommended)

**Scene 0: Title Scene**
- Introduce protagonist and premise
- 10-15 seconds
- Sets visual foundation
- Neutral or slightly positive emotion

**Scenes 1-5: Story Arc**
- Follow three-act structure
- 15-20 seconds each
- Total: 75-100 seconds of story
- Varied emotions for engagement

### Three-Act Structure

**Act 1 - Setup (Scenes 0-1):**
- Introduce protagonist
- Establish normal world
- Present inciting incident

**Act 2 - Conflict (Scenes 2-4):**
- Character faces challenges
- Rising tension and obstacles
- Build toward climax

**Act 3 - Resolution (Scene 5):**
- Climax and resolution
- Character transformation
- Satisfying conclusion

## Example Story: Pyter's First Bug

A Python snake programmer encounters a real bug on his keyboard:

**Scene 0:** Meet Pyter, a Python snake who loves to code
**Scene 1:** Pyter coding happily, everything working smoothly
**Scene 2:** A tiny orange bug appears on the keyboard!
**Scene 3:** Pyter investigates the curious bug
**Scene 4:** Together they find and fix a code bug
**Scene 5:** Success! Bug becomes a helpful friend

**Generated Output:**
- 6 images (scene_000.png through scene_005.png)
- 6 audio files (scene_000.mp3 through scene_005.mp3)
- Final video: ~102 seconds, 12 MB, 1080x1080

## Customization

### Custom Style Locks

Define your own visual style:

```python
CUSTOM_STYLE = """
Aspect ratio: 1920×1080 (widescreen)
Camera: 35mm lens, cinematic low angle
Lighting: dramatic rim lighting, 6500K cool tone
Color palette: #1A1A2E, #16213E, #E94560, #F39C12
Style: photorealistic with cinematic grading
"""
```

### Custom Characters

Create detailed character profiles:

```python
CHARACTER_LOCK = {
    "Luna": """
        Species: black cat
        Colors: pure black (#000000), yellow eyes (#FFD700)
        Features: sleek body, alert ears, long tail
        Clothing: small astronaut helmet
        Size: typical housecat
        Style: semi-realistic cartoon
    """
}
```

### Custom Scene Count

Change from default 6 scenes:

```python
# Shorter story (4 scenes)
scenes = ["title", "problem", "solution", "success"]

# Longer story (10 scenes)
scenes = ["title"] + [f"scene_{i}" for i in range(1, 10)]
```

### Multi-Character Dialogue

Create conversations between characters:

```python
dialogue = [
    {
        "character": "Alex",
        "text": "I found a bug!",
        "emotion": "excited",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX"  # Josh
    },
    {
        "character": "Sage",
        "text": "Let's debug it together.",
        "emotion": "calm",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O"  # Elli
    }
]
```

## Documentation

### Core Files

- **[SKILL.md](SKILL.md)** - Complete implementation with code examples
- **README.md** - This file, overview and quick start

### References

- **[references/style-locks.md](references/style-locks.md)** - Visual consistency guide
  - STYLE_LOCK, CHARACTER_LOCK, NEGATIVE_LOCK
  - Custom lock creation
  - Troubleshooting consistency issues

- **[references/narrative-design.md](references/narrative-design.md)** - Story structure
  - Story arc templates
  - Scene design principles
  - Dialogue and narration writing
  - Emotion tag usage
  - Character voice assignment

- **[references/video-assembly.md](references/video-assembly.md)** - Technical pipeline
  - ffmpeg usage and parameters
  - Bash script explanation
  - Troubleshooting video issues
  - Quality and compression settings

### Examples

- **[examples/example-stories.md](examples/example-stories.md)** - Complete walkthroughs
  - Pyter's First Bug (educational)
  - Luna's Lunar Landing (adventure)
  - The Chef's Secret Ingredient (transformation)
  - Multi-character dialogue examples

- **[examples/character-profiles.md](examples/character-profiles.md)** - Character templates
  - Profile structure and examples
  - Voice assignment guide
  - Multi-character stories
  - Character consistency tips

### Scripts

- **[scripts/assemble_video.sh](scripts/assemble_video.sh)** - Video assembly script
  - Standalone bash script for video creation
  - Can be used independently of Python

## Common Use Cases

### Educational Content

```
"Create a video explaining how plants make food through photosynthesis"
"Make a story about a water droplet traveling through the water cycle"
"Create an educational video about the solar system for children"
```

### Children's Stories

```
"Create a bedtime story about a brave mouse exploring a library"
"Make a story about a young dragon learning to fly"
"Create a video about a robot making friends at school"
```

### Social Media Content

```
"Create a 90-second inspirational story about pursuing your dreams"
"Make a funny story about a cat trying to catch a laser pointer"
"Create a video story showcasing a day in the life of a developer"
```

### Presentations

```
"Create a video introducing our company's mission and values"
"Make a story-format product demo showing key features"
"Create a visual narrative about our team's journey"
```

## Workflow Overview

### 1. Story Planning

```python
# Define story premise, characters, and structure
story = {
    "title": "The Lost Star",
    "scenes": 6,
    "protagonist": "Mira, a curious child",
    "theme": "Courage and discovery"
}
```

### 2. Character Definition

```python
# Create character appearance locks
characters = {
    "Mira": {
        "appearance": "...",
        "voice_id": "EXAVITQu4vr4xnSDxMaL"
    }
}
```

### 3. Scene Generation

```python
# For each scene:
# - Generate image with style/character locks
# - Generate narrated audio with emotion
# - Reference previous scene for consistency
```

### 4. Video Assembly

```bash
# Automated with bash script
bash scripts/assemble_video.sh ./output final_video.mp4
```

### 5. Review and Iterate

```python
# Review output, adjust:
# - Narration text
# - Emotion tags
# - Character descriptions
# - Style parameters
```

## Best Practices

### Visual Consistency

1. **Use hex codes for colors** - Prevents drift
2. **Reference previous scenes** - Maintains continuity
3. **Keep style descriptions detailed** - More control
4. **Test early** - Generate scenes 0-2 first to verify

### Narrative Quality

1. **Target 50-80 words per scene** - Natural pacing
2. **Vary emotion tags** - Keeps engaging
3. **Show don't tell** - Use visual descriptions
4. **End with resolution** - Satisfying conclusion

### Technical

1. **Verify ffmpeg installed** - Required for assembly
2. **Check API quotas** - Monitor usage limits
3. **Use appropriate models** - DALL-E 3 for quality, DALL-E 2 for consistency
4. **Keep output organized** - Separate directory per story

## Limitations and Considerations

### Image Generation

- DALL-E 3: Highest quality but harder to maintain consistency
- DALL-E 2: Better for variations but lower quality
- Gemini: Fast but may have quota limits

**Recommendation:** Use DALL-E 3 for Scene 0, then DALL-E 2 with variations for consistency.

### Audio Generation

- ElevenLabs free tier: 10,000 characters/month
- Music generation requires paid subscription
- Voice cloning requires paid tier

### Video Assembly

- ffmpeg required (must be installed separately)
- Processing time: ~30-60 seconds for 6-scene video
- File size: ~10-15 MB typical for 100-second video

## Troubleshooting

### Images Look Different Between Scenes

**Problem:** Character appearance changes scene to scene

**Solution:**
- Make CHARACTER_LOCK more specific
- Add exact hex codes for all colors
- Use image variations (DALL-E 2) referencing Scene 0
- Check that previous scene reference is working

### Audio Doesn't Match Video Length

**Problem:** Narration too long or too short

**Solution:**
- Target 50-80 words per scene
- Video auto-adjusts timing to match total audio
- Check that all audio files generated successfully

### Video Assembly Fails

**Problem:** ffmpeg errors or missing files

**Solution:**
```bash
# Verify ffmpeg installed
ffmpeg -version

# Check all files present
ls output/scene_*.png
ls output/scene_*.mp3

# Verify file naming: scene_000.png not scene_0.png
```

### Poor Visual Quality

**Problem:** Images look low quality or pixelated

**Solution:**
- Use DALL-E 3 instead of DALL-E 2
- Ensure 1024x1024 or 1080x1080 generation
- Check ffmpeg CRF setting (lower = better quality)

## Performance Tips

### Faster Generation

- Use DALL-E 2 (faster than DALL-E 3)
- Use Flash v2.5 for audio (faster than Multilingual v2)
- Generate fewer scenes for testing

### Cost Optimization

- Use DALL-E 2 ($0.02/image vs $0.04-$0.08 for DALL-E 3)
- Monitor ElevenLabs character usage
- Cache and reuse successful generations

### Quality Optimization

- Use DALL-E 3 for highest quality images
- Use Multilingual v2 for best audio quality
- Lower ffmpeg CRF to 18 for better video quality

## Pricing Reference

**OpenAI (DALL-E):**
- DALL-E 3 Standard: $0.040 per image (1024x1024)
- DALL-E 3 HD: $0.080 per image
- DALL-E 2: $0.020 per image

**6-scene story cost: $0.12-$0.48**

**ElevenLabs:**
- Free tier: 10,000 characters/month
- Starter ($5/mo): 30,000 characters/month
- Creator ($22/mo): 100,000 characters/month

**6-scene story (400 words): ~2,400 characters**

**Total 6-scene video: ~$0.12-$0.50 depending on settings**

## Related Skills

- **image-generation** - Standalone image creation (Gemini, DALL-E)
- **elevenlabs** - Audio generation (TTS, sound effects, music)
- **python-plotting** - Video visualization and analysis
- **scientific-writing** - Narrative and storytelling writing

## Resources

### Official Documentation

- **OpenAI DALL-E**: https://platform.openai.com/docs/guides/images
- **ElevenLabs API**: https://elevenlabs.io/docs
- **ffmpeg**: https://ffmpeg.org/documentation.html

### Tools & Services

- **OpenAI API Keys**: https://platform.openai.com/api-keys
- **ElevenLabs Dashboard**: https://elevenlabs.io/app
- **ElevenLabs Voice Library**: https://elevenlabs.io/voice-library

### Inspiration

- **Pixar Storytelling**: Story structure and emotional arcs
- **Children's Books**: Visual consistency and pacing
- **Motion Graphics**: Scene transitions and composition

## Contributing

Improvements welcome:
- Additional story examples
- Character profile templates
- Custom style lock examples
- Workflow optimizations
- Integration with other tools

## Version History

- **v1.0.0** (2025-01-23) - Initial release
  - 6-scene default structure
  - DALL-E and Gemini image support
  - ElevenLabs audio integration
  - Automated video assembly
  - Comprehensive documentation

## Support

For issues or questions:
1. Check the [examples](examples/) directory
2. Review [references](references/) documentation
3. Consult [SKILL.md](SKILL.md) for implementation
4. Open an issue in the knowhow repository

---

**Ready to create amazing video stories!** 🎬📖🎨

*Combining image-generation and elevenlabs skills for coherent AI video storytelling*
