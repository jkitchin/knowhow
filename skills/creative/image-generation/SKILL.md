---
name: image-generation
description: |
  AI-powered image generation and editing using Google Gemini, Google Imagen, and OpenAI models.
  Generate images from text descriptions, edit existing images, create logos/stickers,
  apply style transfers, and produce product mockups.

  Use this skill when the user requests:
  - Image generation from text descriptions
  - Image editing or modifications
  - Logos, stickers, or graphic design assets
  - Product mockups or visualizations
  - Style transfers or artistic effects
  - Iterative image refinement

  Available models:
  - Google Gemini: gemini-2.5-flash-image (Nano Banana), gemini-3-pro-image-preview (Nano Banana Pro)
  - Google Imagen: imagen-4.0-generate-001, imagen-4.0-ultra-generate-001, imagen-4.0-fast-generate-001
  - OpenAI: gpt-image-1.5 (recommended), gpt-image-1, dall-e-3, dall-e-2

  Inspired by: https://github.com/EveryInc/every-marketplace/tree/main/plugins/compounding-engineering/skills/gemini-imagegen
allowed-tools: ["Bash", "Read", "Write", "AskUserQuestion", "WebFetch"]
---

# Image Generation

> **Important (December 2025)**: The `google-generativeai` package has been deprecated.
> This skill now uses the `google-genai` SDK. If upgrading from older code, see the
> [migration guide](https://ai.google.dev/gemini-api/docs/migrate).

## Purpose

This skill enables AI-powered image generation and editing through Google's Gemini image models and OpenAI's DALL-E models. Create photorealistic images, illustrations, logos, stickers, and product mockups from natural language descriptions. Edit existing images with text instructions, apply style transfers, and refine outputs through iterative conversation.

**Attribution:** This skill is inspired by the `gemini-imagegen` skill from [Every Marketplace](https://github.com/EveryInc/every-marketplace/tree/main/plugins/compounding-engineering/skills/gemini-imagegen) by Every Inc.

## When to Use

This skill should be invoked when the user asks to:
- Generate images from text descriptions ("create an image of...", "generate a picture...")
- Create logos, icons, or stickers ("design a logo for...", "make a sticker...")
- Edit or modify existing images ("change the background to...", "add... to this image")
- Apply artistic styles or effects ("make it look like...", "stylize as...")
- Create product mockups or visualizations ("product photo of...", "mockup showing...")
- Refine or iterate on images ("make it more...", "adjust the...", "try again with...")
- Generate variations with different styles or compositions

## Available Models

### Google Gemini Models (Nano Banana)

1. **gemini-2.5-flash-image** ("Nano Banana")
   - Resolution: 1K (1024px), supports 2K
   - Aspect ratios: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
   - Best for: Speed, high-volume operations, rapid iteration, image editing
   - Use when: Quick prototypes, multiple variations, time-sensitive requests
   - Cost: ~$0.039 per image (~$30/million output tokens)

2. **gemini-3-pro-image-preview** ("Nano Banana Pro")
   - Resolution: 1K default, supports 2K and 4K
   - Aspect ratios: Same as Flash
   - Best for: Professional assets, complex instructions, highest quality
   - Use when: Final deliverables, detailed compositions, text-heavy designs
   - Special features:
     - Google Search grounding for real-time data visualization
     - "Thinking" mode with interim composition refinement
     - Up to 14 reference images (6 objects, 5 humans for character consistency)
     - Advanced text rendering

### Google Imagen 4 Family (New)

3. **imagen-4.0-fast-generate-001** ("Imagen 4 Fast")
   - Resolution: Standard
   - Best for: Rapid generation, high-volume tasks
   - Use when: Speed is priority, budget-conscious
   - Cost: $0.02 per image
   - Note: Text-only input (no image editing)

4. **imagen-4.0-generate-001** ("Imagen 4")
   - Resolution: Up to 2K
   - Best for: High-quality photorealistic images, excellent text rendering
   - Use when: Professional quality needed, text in images
   - Features: Significant improvements in text rendering over previous Imagen models

5. **imagen-4.0-ultra-generate-001** ("Imagen 4 Ultra")
   - Resolution: Up to 2K
   - Best for: Highest quality, detailed visuals
   - Use when: Maximum quality is essential (one image at a time)
   - Limitation: Only generates one image per request

### OpenAI GPT Image Models

6. **gpt-image-1.5** (Recommended - December 2025)
   - Resolution: 1024x1024, 1536x1024, 1024x1536, or auto
   - Best for: Production-quality visuals, precise editing, character consistency
   - Use when: Professional design, iterative workflows, text-heavy images
   - Features:
     - 4x faster than gpt-image-1, 20% lower cost
     - Built-in reasoning and world knowledge
     - Precise logo & face preservation during edits
     - Excellent text rendering (crisp lettering, dense text)
     - Complex structured visuals (infographics, diagrams, multi-panel)
     - Streaming support
   - Output formats: png, jpeg, webp (with compression control)
   - Transparency: transparent, opaque, or auto background

7. **gpt-image-1** (April 2025)
   - Resolution: Up to 4096x4096
   - Best for: High-resolution images, creative workflows
   - Use when: Maximum resolution needed
   - Cost: ~$0.02 (low), ~$0.07 (medium), ~$0.19 (high) per image
   - Output formats: png, jpeg, webp
   - Note: Single image per request, no inpainting

### Legacy OpenAI DALL-E Models

8. **dall-e-3**
   - Resolution: 1024x1024, 1024x1792, 1792x1024
   - Best for: Creative interpretations, artistic renders
   - Use when: Natural artistic style preferred
   - Note: Automatic prompt expansion

9. **dall-e-2**
   - Resolution: 1024x1024, 512x512, 256x256
   - Best for: Faster generation, lowest cost, variations
   - Use when: Budget-conscious, simpler images
   - Unique feature: Can generate variations of existing images

## Model Selection Logic

Ask the user or use this decision tree:

```
Need image editing or iterative refinement?
├─ Yes → gpt-image-1.5 (best editing) or gemini-2.5-flash-image (multi-turn chat)
└─ No → Text-to-image only
    ├─ Need highest quality?
    │   ├─ Text rendering critical → gpt-image-1.5 or imagen-4.0-generate-001
    │   ├─ Maximum resolution (4K) → gemini-3-pro-image-preview
    │   ├─ Ultra quality (single image) → imagen-4.0-ultra-generate-001
    │   └─ Character consistency → gpt-image-1.5 or gemini-3-pro-image-preview
    ├─ Need speed/volume?
    │   ├─ Cheapest → imagen-4.0-fast-generate-001 ($0.02)
    │   └─ Fast + editing → gemini-2.5-flash-image
    └─ Balanced default → gpt-image-1.5 (recommended)
```

**Quick Reference:**
- **Best overall**: `gpt-image-1.5` - fast, affordable, great editing & text
- **Best for text rendering**: `gpt-image-1.5` or `imagen-4.0-generate-001`
- **Best for 4K resolution**: `gemini-3-pro-image-preview`
- **Cheapest per image**: `imagen-4.0-fast-generate-001` ($0.02)
- **Best for reference images**: `gemini-3-pro-image-preview` (up to 14 refs)
- **Best for iterative editing**: `gpt-image-1.5` (face/logo preservation)

If the user has specific model preference, use that.

## Capabilities

1. **Text-to-Image Generation**: Create images from detailed text descriptions
2. **Image Editing**: Modify existing images with text instructions
3. **Style Transfer**: Apply artistic styles, filters, and effects
4. **Logo & Sticker Design**: Generate branded assets with specific styles
5. **Product Mockups**: Create professional product photography and presentations
6. **Multi-turn Refinement**: Iteratively improve images through conversation
7. **Aspect Ratio Control**: Generate images in various formats (square, portrait, landscape, wide)
8. **Reference-based Generation**: Use existing images as compositional references (Gemini Pro)

## Instructions

### Step 1: Understand the Request

Analyze the user's request to determine:
- **Type**: Text-to-image, image editing, style transfer, logo/sticker, mockup
- **Subject**: What should be in the image
- **Style**: Photorealistic, illustration, artistic, minimalist, etc.
- **Details**: Colors, lighting, composition, mood, specific elements
- **Format**: Aspect ratio, resolution requirements
- **Urgency**: Speed vs. quality trade-off

### Step 2: Select Model

Based on requirements:
- **High quality + complexity** → `gemini-3-pro-image-preview`
- **Speed + iterations** → `gemini-2.5-flash-image`
- **DALL-E preference** → `dall-e-3` or `dall-e-2`

If unclear, use `AskUserQuestion` tool to clarify model preference.

### Step 3: Craft Effective Prompt

Build a detailed prompt following these patterns:

**For Photorealistic Images:**
```
[Subject], [camera details], [lighting], [mood/atmosphere], [composition]

Example: "Close-up portrait of a woman, 85mm lens, soft golden hour lighting,
serene mood, shallow depth of field, professional photography"
```

**For Illustrations/Art:**
```
[Subject], [art style], [color palette], [details], [mood]

Example: "Kawaii cat sticker, bold black outlines, cel-shading, pastel colors,
cute expression, chibi style"
```

**For Logos:**
```
[concept], [style], [elements], [colors], [context]

Example: "Tech startup logo, minimalist geometric design, abstract network nodes,
blue and silver gradient, professional, vector style"
```

**For Product Photography:**
```
[product], [setting], [lighting], [presentation], [context]

Example: "Wireless earbuds, white background, studio lighting, 3/4 angle view,
clean minimal composition, e-commerce product shot"
```

**Key principles:**
- Be specific and detailed
- Include lighting, composition, and mood
- Specify style clearly (photorealistic, illustration, etc.)
- Mention camera/lens for photorealistic (85mm, wide angle, macro)
- For text in images, use Pro model and specify exact text

### Step 4: Implement API Call

#### For Gemini Models:

> **Note**: The `google.generativeai` package has been deprecated. Use `google.genai` instead.
> See migration guide: https://ai.google.dev/gemini-api/docs/migrate

```python
from google import genai
from google.genai import types
from pathlib import Path

# Initialize client (uses GEMINI_API_KEY or GOOGLE_API_KEY env var automatically)
client = genai.Client()

# Basic text-to-image
response = client.models.generate_content(
    model="gemini-2.5-flash-image",  # or gemini-3-pro-image-preview
    contents=prompt_text,
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        # Optional configurations:
        # image_config=types.ImageConfig(
        #     aspect_ratio="1:1",  # 1:1, 3:4, 4:3, 9:16, 16:9, 21:9
        #     image_size="1K",     # 1K, 2K, 4K (Pro only)
        # )
    )
)

# Extract and save image
for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        image.save("output.png")

# For image editing (pass existing image):
from PIL import Image

image = Image.open("input.png")
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[image, "Make the background a sunset scene"],
    config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
)

# For multi-turn refinement (use chat):
chat = client.chats.create(
    model="gemini-2.5-flash-image",
    config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
)
response1 = chat.send_message("A futuristic city skyline")
response2 = chat.send_message("Add more neon lights and flying cars")
```

#### For Google Imagen 4 Models:

```python
from google import genai
from google.genai import types

# Initialize client (uses GEMINI_API_KEY or GOOGLE_API_KEY env var automatically)
client = genai.Client()

# Imagen 4 text-to-image (no editing support)
# Also available: imagen-4.0-fast-generate-001, imagen-4.0-ultra-generate-001
response = client.models.generate_images(
    model="imagen-4.0-generate-001",
    prompt=prompt_text,
    config=types.GenerateImagesConfig(
        number_of_images=4,  # 1-4 for standard, 1 for Ultra
        aspect_ratio="1:1",  # 1:1, 3:4, 4:3, 9:16, 16:9
        person_generation="allow_adult",  # "dont_allow", "allow_adult", "allow_all"
    )
)

# Save images
for i, generated_image in enumerate(response.generated_images):
    generated_image.image.save(f"output_{i}.png")
```

#### For OpenAI Models (gpt-image-1.5 recommended):

```python
from openai import OpenAI
from pathlib import Path
import base64

client = OpenAI()  # reads OPENAI_API_KEY env var automatically

# gpt-image-1.5 generation (recommended)
response = client.images.generate(
    model="gpt-image-1.5",
    prompt=prompt_text,
    size="1024x1024",  # or "1536x1024", "1024x1536", "auto"
    quality="high",    # "low", "medium", "high"
    n=1,               # 1-10 images
    output_format="png",  # "png", "jpeg", "webp"
    background="auto",    # "transparent", "opaque", "auto"
    moderation="auto",    # "auto" or "low" for less restrictive
)

# Response returns base64 data
image_data = base64.b64decode(response.data[0].b64_json)
Path("output.png").write_bytes(image_data)

# gpt-image-1 generation (for max 4K resolution)
response = client.images.generate(
    model="gpt-image-1",
    prompt=prompt_text,
    size="1024x1024",
    quality="high",
    n=1,
)

# Image editing with gpt-image-1.5
response = client.images.edit(
    model="gpt-image-1.5",
    image=open("input.png", "rb"),
    prompt="Change the background to a beach sunset",
    size="1024x1024",
)

# Legacy DALL-E 3 generation
response = client.images.generate(
    model="dall-e-3",
    prompt=prompt_text,
    size="1024x1024",  # or "1024x1792", "1792x1024"
    quality="standard",  # or "hd"
    n=1,
)
image_url = response.data[0].url

# Download URL-based response
import requests
image_data = requests.get(image_url).content
Path("output.png").write_bytes(image_data)
```

**Implementation approach:**
- Use `Bash` tool to execute Python scripts with API calls
- Check for API keys in environment variables
- Handle errors gracefully (API limits, invalid prompts, etc.)
- Save images with descriptive filenames
- Report image location to user

### Step 5: Handle Output

1. **Save the generated image** to an appropriate location
2. **Verify the output** meets the request
3. **Show the user** the saved file path
4. **Offer refinement** if the result isn't quite right
5. **Explain the prompt used** so the user understands the generation

### Step 6: Iterate if Needed

If the user wants changes:
- For Gemini: Use chat interface to maintain context
- For gpt-image-1.5: Use editing API for precise face/logo preservation
- For Imagen/DALL-E: Generate new image with updated prompt
- Keep previous versions for comparison
- Suggest specific adjustments based on the current result

## Requirements

**API Keys:**
- Google (Gemini/Imagen): Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- OpenAI: Set `OPENAI_API_KEY` environment variable

**Python Packages:**
```bash
pip install google-genai openai pillow requests
```

> **Note**: The `google-generativeai` package has been deprecated and will no longer receive updates.
> Use `google-genai` instead. Migration guide: https://ai.google.dev/gemini-api/docs/migrate

**System:**
- Python 3.8+
- Internet connection for API access
- Write permissions for saving images

**Approximate Costs (per image):**
| Model | Low Quality | High Quality |
|-------|-------------|--------------|
| imagen-4.0-fast | $0.02 | $0.02 |
| imagen-4.0 | - | ~$0.04 |
| imagen-4.0-ultra | - | ~$0.08 |
| gemini-2.5-flash-image | ~$0.039 | ~$0.039 |
| gpt-image-1.5 | ~$0.016 | ~$0.15 |
| gpt-image-1 | ~$0.02 | ~$0.19 |
| dall-e-3 | ~$0.04 | ~$0.08 |
| dall-e-2 | ~$0.02 | ~$0.02 |

## Best Practices

### Prompt Engineering

1. **Be Specific**: Vague prompts produce inconsistent results
   - Bad: "a nice landscape"
   - Good: "mountain valley at sunrise, mist over lake, pine trees, warm golden light, peaceful atmosphere"

2. **Include Technical Details** for photorealism:
   - Camera: "shot on 85mm lens", "wide angle 24mm", "macro photography"
   - Lighting: "golden hour", "studio lighting", "rim light", "soft diffused"
   - Quality: "high resolution", "detailed", "sharp focus", "professional photography"

3. **Specify Style Clearly**:
   - "photorealistic", "oil painting", "watercolor", "digital art", "3D render"
   - "minimalist", "detailed", "abstract", "realistic", "stylized"
   - "anime style", "pixel art", "vector art", "charcoal sketch"

4. **Use Examples and References**:
   - "in the style of [artist/art movement]"
   - "similar to [known visual reference]"
   - For Gemini Pro: Provide actual reference images

5. **Negative Prompts** (what to avoid):
   - DALL-E doesn't support negative prompts directly
   - For Gemini, phrase as positive instructions: "clear sky" vs "no clouds"

### Model-Specific Tips

**gpt-image-1.5 (Recommended):**
- Best for iterative editing workflows - preserves faces/logos during edits
- Built-in reasoning understands context (e.g., "Bethel, NY, August 1969" → Woodstock)
- Excellent text rendering, especially dense/small text
- Great for infographics, diagrams, multi-panel compositions
- 4x faster than gpt-image-1, use streaming for real-time feedback
- Use `background="transparent"` for assets

**gpt-image-1:**
- Maximum resolution (4096x4096) when needed
- Good for one-shot high-res generation
- No editing/inpainting support

**Imagen 4 Family:**
- Best text rendering among Google models
- Use Fast ($0.02) for high-volume prototyping
- Use Ultra for highest quality single images
- Text-to-image only (no editing) - use Gemini for edits
- All images include SynthID watermark

**Gemini Flash (2.5) - Nano Banana:**
- Best for iterative multi-turn editing via chat
- Good for generating multiple variations quickly
- Use for draft/concept phase with refinement

**Gemini Pro (3) - Nano Banana Pro:**
- Use for final deliverables and 4K output
- Best for complex compositions with reference images (up to 14)
- "Thinking" mode generates interim drafts for composition planning
- Leverage Google Search grounding for current events/real places

**DALL-E 3 (Legacy):**
- Excellent at understanding natural language
- Strong at creative interpretations
- Automatic prompt expansion (may deviate from exact request)

**DALL-E 2 (Legacy):**
- More literal interpretation of prompts
- Can generate variations of existing images
- Budget-friendly for simple tasks

### Quality Guidelines

1. **Start with clear requirements**: Ask clarifying questions before generating
2. **Choose appropriate model**: Match model capabilities to requirements
3. **Iterate thoughtfully**: Make specific changes rather than complete regeneration
4. **Save intermediate versions**: Keep promising iterations
5. **Respect usage policies**: Follow content policies for each platform
6. **Credit the tool**: Disclose AI-generated images when sharing

### Error Handling

- **API key missing**: Prompt user to set environment variable
- **Invalid prompt**: Suggest refinements, check content policy
- **Rate limits**: Inform user and suggest retry timing
- **Generation failure**: Try simpler prompt or different model
- **Unsatisfactory result**: Offer to regenerate with adjusted prompt

## Examples

### Example 1: Logo Design

**User request:** "Create a logo for a coffee shop called 'Morning Brew'"

**Expected behavior:**
1. Ask user about style preference (modern, vintage, minimalist, etc.)
2. Ask about color preferences
3. Select model (gpt-image-1.5 for text rendering, or gemini-3-pro-image-preview for 4K)
4. Generate with prompt: "Coffee shop logo for 'Morning Brew', minimalist modern design,
   coffee cup with steam forming sunrise rays, warm brown and orange colors,
   clean professional aesthetic, vector style, white background"
5. Use `background="transparent"` for gpt-image-1.5 for easy placement
6. Save image and show path
7. Offer to generate variations with different styles

### Example 2: Product Photography

**User request:** "Generate product photos of wireless earbuds"

**Expected behavior:**
1. Select model (imagen-4.0-generate-001 for photorealism, or gpt-image-1.5 for editing)
2. Generate with prompt: "Wireless earbuds product photography, white background,
   professional studio lighting, 3/4 angle view showing charging case and earbuds,
   clean minimal composition, high resolution, sharp focus, e-commerce quality"
3. Generate additional angles if requested
4. Save all versions

### Example 3: Illustration

**User request:** "Create a cute sticker of a robot"

**Expected behavior:**
1. Select model (gpt-image-1.5 with `background="transparent"` for stickers)
2. Generate with prompt: "Cute robot sticker, kawaii style, bold black outlines,
   cel-shading, pastel blue and silver colors, big friendly eyes, rounded shapes,
   chibi proportions, white border, transparent background suitable for sticker"
3. Save and offer variations

### Example 4: Image Editing

**User request:** "Change the background of this photo to a beach sunset"

**Expected behavior:**
1. Use `Read` tool to load the existing image
2. Select model (gpt-image-1.5 for best editing with face preservation, or Gemini for chat-based iteration)
3. Generate with image + prompt: "Change the background to a beautiful beach at sunset,
   golden hour lighting, warm colors, ocean and palm trees visible, maintain the subject
   in foreground, seamless composition"
4. Save edited image

### Example 5: Iterative Refinement

**User request:** "Generate a futuristic city" → "Add more neon lights" → "Make it rain"

**Expected behavior:**
1. First generation: "Futuristic city skyline, towering skyscrapers, advanced architecture,
   night scene, detailed, cinematic lighting"
2. Use gpt-image-1.5 edit API or Gemini chat interface to maintain context
3. Second refinement: "Add vibrant neon lights throughout the city, cyberpunk aesthetic,
   glowing signs and billboards"
4. Third refinement: "Add rain effect, wet streets reflecting neon lights, atmospheric,
   moody"
5. Save each version with descriptive names

## Limitations

1. **Content Policies**: All models have content restrictions (no violence,
   explicit content, copyrighted characters, real people without consent)
2. **Text Rendering**: Much improved in gpt-image-1.5 and Imagen 4, but very long/complex text may still have issues
3. **Photorealism of People**: May not perfectly capture specific facial features; gpt-image-1.5 preserves faces best during edits
4. **Complex Compositions**: Very complex scenes may need multiple iterations
5. **Consistency**: Hard to maintain exact consistency across multiple generations; use gpt-image-1.5 or Gemini Pro with reference images for character consistency
6. **Real-time Events**: Results may not reflect very recent events (use Gemini Pro Search grounding for current topics)
7. **API Costs**: Be mindful of usage; see pricing table above
8. **Rate Limits**: APIs have rate limits; may need to wait between requests
9. **Imagen Limitations**: Text-to-image only (no editing), single image for Ultra model
10. **Watermarks**: Google Imagen images include SynthID watermark

## Related Skills

- `python-plotting` - For data visualization and charts
- `brainstorming` - For ideating visual concepts
- `scientific-writing` - For figure captions and documentation
- `python-best-practices` - For writing clean API integration code

## Additional Resources

- **Google GenAI SDK Migration Guide**: https://ai.google.dev/gemini-api/docs/migrate
- **Gemini Image Generation**: https://ai.google.dev/gemini-api/docs/image-generation
- **Imagen API Documentation**: https://ai.google.dev/gemini-api/docs/imagen
- **OpenAI Images API**: https://platform.openai.com/docs/api-reference/images
- **gpt-image-1.5 Prompting Guide**: https://cookbook.openai.com/examples/multimodal/image-gen-1.5-prompting_guide
- **Deprecated SDK Info**: https://github.com/google-gemini/deprecated-generative-ai-python
- **Prompt Engineering Guide**: See `references/prompt-engineering.md`
