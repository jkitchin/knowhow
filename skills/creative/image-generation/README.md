# Image Generation Skill

> **Important (December 2025)**: This skill now uses the `google-genai` SDK. The `google-generativeai`
> package has been deprecated. See [migration guide](https://ai.google.dev/gemini-api/docs/migrate).

AI-powered image generation and editing using Google Gemini, Imagen, and OpenAI models.

## Overview

This skill enables Claude Code to generate and edit images using state-of-the-art AI models from Google (Gemini) and OpenAI (DALL-E). Create photorealistic images, illustrations, logos, product mockups, and artistic compositions from natural language descriptions. Edit existing images with text instructions, apply style transfers, and refine outputs through iterative conversation.

**Attribution:** This skill is inspired by the `gemini-imagegen` skill from [Every Marketplace](https://github.com/EveryInc/every-marketplace/tree/main/plugins/compounding-engineering/skills/gemini-imagegen) by Every Inc. We're grateful for their pioneering work in AI image generation skills.

## Quick Start

### Installation

```bash
# Install the skill from the skillin repository
skillin install image-generation

# Or copy to your project
cp -r skills/creative/image-generation .claude/skills/
```

### Requirements

**API Keys:**
```bash
# Set environment variables
export GEMINI_API_KEY="your-gemini-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

**Python Dependencies:**
```bash
pip install google-genai openai pillow requests
```

### Basic Usage

Once installed, simply ask Claude to generate or edit images:

```
"Generate a professional headshot for LinkedIn"
"Create a logo for a coffee shop called Mountain Peak Coffee"
"Change the background of this photo to a beach sunset"
"Make this landscape look like it was painted by Van Gogh"
```

Claude will automatically:
1. Recognize the image generation request
2. Select the appropriate model
3. Craft an effective prompt
4. Generate the image
5. Save it and show you the result

## Available Models

### Google Gemini

- **gemini-2.5-flash-image** - Fast, 1024px, ideal for rapid iteration and editing
- **gemini-3-pro-image-preview** - Up to 4K, professional quality, complex compositions, 14 reference images

### Google Imagen 4

- **imagen-4.0-fast-generate-001** - Cheapest ($0.02/image), rapid generation
- **imagen-4.0-generate-001** - High-quality photorealistic, excellent text rendering
- **imagen-4.0-ultra-generate-001** - Highest quality (single image per request)

### OpenAI

- **gpt-image-1.5** (Recommended) - Fast, affordable, excellent editing & text rendering
- **gpt-image-1** - Maximum resolution (4096x4096)
- **dall-e-3** - Creative interpretations, automatic prompt expansion
- **dall-e-2** - Budget-friendly, supports variations

## Capabilities

### Text-to-Image Generation
Generate images from natural language descriptions:
- Photorealistic photography
- Illustrations and digital art
- Logos and graphic design
- Product photography
- Character designs
- Landscapes and environments
- Abstract and artistic compositions

### Image Editing
Modify existing images with text instructions:
- Background replacement
- Style transfers
- Adding or removing objects
- Lighting and mood changes
- Color grading and filters
- Perspective transformations

### Iterative Refinement
Refine images through conversation:
- Multi-turn improvements
- Progressive edits
- Exploration of variations
- Style and composition adjustments

## Documentation

### Core Files

- **[SKILL.md](SKILL.md)** - Complete skill implementation with detailed instructions
- **README.md** - This file, overview and quick start

### References

- **[references/gemini-models.md](references/gemini-models.md)** - Complete Gemini API documentation
- **[references/dalle-models.md](references/dalle-models.md)** - Complete DALL-E API documentation
- **[references/prompt-engineering.md](references/prompt-engineering.md)** - Comprehensive prompt writing guide

### Examples

- **[examples/text-to-image.md](examples/text-to-image.md)** - 10 detailed text-to-image examples
- **[examples/image-editing.md](examples/image-editing.md)** - 10 image editing examples

## Use Cases

### Business & Marketing
- Product photography for e-commerce
- Marketing visuals and social media graphics
- Brand logos and identity design
- Advertising concept art
- Presentation graphics

### Creative & Artistic
- Character design and concept art
- Book and magazine illustrations
- Album covers and poster designs
- Fantasy and sci-fi artwork
- Abstract and experimental art

### Professional
- Architectural visualizations
- Interior design mockups
- Professional headshots
- Data visualization concepts
- Educational illustrations

### Personal
- Social media content
- Creative projects
- Gift designs
- Personal branding
- Hobby and craft references

## Example Prompts

### Photorealistic Portrait
```
Professional business headshot, confident expression, neutral gray background,
soft studio lighting, shot on 85mm lens, shallow depth of field, high quality
```

### Illustration
```
Cute robot character, kawaii style, pastel colors, bold outlines, cel-shading,
cheerful expression, sticker format with white border, children's illustration
```

### Logo Design
```
Tech startup logo, minimalist geometric design, abstract network nodes, blue
and silver gradient, professional, vector style, clean modern aesthetic
```

### Product Photography
```
Wireless earbuds with charging case, professional product photography, white
seamless background, studio lighting, 3/4 angle view, clean composition,
commercial e-commerce quality
```

### Landscape
```
Mountain valley at sunset, mist over alpine lake, pine trees, warm golden light,
peaceful atmosphere, professional landscape photography, 24mm wide angle, high detail
```

## Model Selection Guide

**Choose gpt-image-1.5 (Recommended) when:**
- Need excellent text rendering
- Iterative editing workflows (preserves faces/logos)
- Fast turnaround with good quality
- Balanced cost/quality

**Choose Gemini Flash when:**
- Multi-turn editing via chat
- Rapid iteration on concepts
- Speed is priority

**Choose Gemini Pro when:**
- Need 4K resolution
- Complex compositions with reference images
- Real-time data visualization (Search grounding)

**Choose Imagen 4 Fast when:**
- Budget is primary concern ($0.02/image)
- High-volume generation
- Text-to-image only (no editing)

**Choose Imagen 4/Ultra when:**
- Photorealistic quality
- Excellent text in images
- No editing needed

**Choose DALL-E 3 when:**
- Creative interpretation preferred
- Artistic/illustrative content

**Choose gpt-image-1 when:**
- Maximum resolution (4096x4096) needed

## Tips for Best Results

### 1. Be Specific
Detailed prompts produce better, more consistent results.

**Vague:** "A nice landscape"
**Specific:** "Mountain valley at sunrise, mist over lake, pine trees, warm golden light, peaceful"

### 2. Include Style Information
Always specify the artistic style or photographic approach.

Examples: `photorealistic`, `digital illustration`, `oil painting`, `3D render`, `vintage photography`

### 3. Describe Lighting
Lighting dramatically affects mood and quality.

Examples: `golden hour lighting`, `studio lighting`, `dramatic side lighting`, `soft diffused light`

### 4. Specify Composition
Guide how elements should be arranged.

Examples: `centered composition`, `rule of thirds`, `close-up`, `wide angle`, `overhead view`

### 5. Iterate Thoughtfully
Use conversation to refine results progressively rather than starting over.

## Troubleshooting

### Image Quality Issues
- Use Gemini Pro or DALL-E 3 for higher quality
- Add technical details: "high resolution", "professional quality", "sharp focus"
- Be more specific about lighting and style

### Unexpected Results
- Make prompts more explicit and detailed
- Specify what you don't want (via positive alternatives)
- Try a different model

### Text in Images
- Use Gemini Pro (best for text rendering)
- Specify exact text in quotes
- Keep text simple and prominent

### API Errors
- Verify API keys are set correctly
- Check rate limits and quotas
- Review content policy compliance
- Implement retry logic with backoff

## Cost Optimization

1. **Prototype with cheaper models** (Gemini Flash, DALL-E 2)
2. **Generate finals with premium models** (Gemini Pro, DALL-E 3)
3. **Use appropriate resolutions** (don't use 4K when 1K suffices)
4. **Batch similar requests** together
5. **Save successful prompts** for reuse

## Content Policies

Both Google and OpenAI have content policies that prohibit:
- Violence, gore, or disturbing content
- Hate symbols or discriminatory content
- Sexual or adult content
- Illegal activities
- Real identifiable people without consent
- Copyrighted characters or IP

Keep prompts appropriate and focused on original creative content.

## Attribution & Credits

### Inspiration
This skill was inspired by the **gemini-imagegen** skill from Every Inc.'s marketplace:
- Repository: https://github.com/EveryInc/every-marketplace
- Path: `plugins/compounding-engineering/skills/gemini-imagegen`
- Credit: Every Inc. for the original Gemini image generation implementation

### Extensions
This implementation extends the original concept by:
- Adding OpenAI DALL-E model support (DALL-E 2 and DALL-E 3)
- Comprehensive documentation for prompt engineering
- Detailed examples for various use cases
- Model selection guidance
- Image editing workflows

### License
This skill follows the skillin repository license. The original gemini-imagegen concept belongs to Every Inc.

## Resources

### API Documentation
- [Google GenAI SDK Migration Guide](https://ai.google.dev/gemini-api/docs/migrate)
- [Google Gemini Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Google Imagen API](https://ai.google.dev/gemini-api/docs/imagen)
- [OpenAI Images API](https://platform.openai.com/docs/api-reference/images)

### Pricing
- [Google AI Studio Pricing](https://ai.google.dev/pricing)
- [OpenAI Pricing](https://openai.com/pricing)

### Community
- [Skillin Repository](https://github.com/your-repo/skillz)
- [Every Marketplace](https://github.com/EveryInc/every-marketplace)

## Contributing

Found ways to improve this skill? Contributions welcome:

1. Additional model support
2. More example use cases
3. Prompt engineering techniques
4. Error handling improvements
5. Documentation enhancements

## Version History

- **v1.2.0** (2025-12-29) - SDK Migration
  - Migrated from deprecated `google-generativeai` to `google-genai` SDK
  - Updated all code examples to new API patterns
  - Added migration guide references

- **v1.1.0** (2025-12-XX) - New Models
  - Added Google Imagen 4 family (Fast, Standard, Ultra)
  - Added OpenAI gpt-image-1.5 and gpt-image-1
  - Updated model selection guidance
  - Added pricing information

- **v1.0.0** (2025-01-23) - Initial release
  - Gemini 2.5 Flash and 3 Pro support
  - DALL-E 2 and 3 support
  - Comprehensive documentation
  - Text-to-image and image editing examples
  - Prompt engineering guide

## Support

For issues or questions:
1. Check the [examples](examples/) directory
2. Review [prompt engineering guide](references/prompt-engineering.md)
3. Consult model-specific documentation ([Gemini](references/gemini-models.md), [DALL-E](references/dalle-models.md))
4. Open an issue in the skillin repository

---

**Happy generating!** 🎨✨

*Built with inspiration from Every Inc.'s gemini-imagegen skill*
