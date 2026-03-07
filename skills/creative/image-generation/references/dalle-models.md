# OpenAI Image Generation Models

## Overview

OpenAI provides a family of image generation models ranging from the latest gpt-image-1.5 to the legacy DALL-E series. The newer models offer superior quality, flexible output formats, transparent background support, and excellent text rendering, while the legacy DALL-E models remain available for specific use cases.

## Available Models

### gpt-image-1.5 (Recommended, December 2025)

**Specifications:**
- Resolution: 1024x1024, 1536x1024, 1024x1536, or auto
- Output Formats: png, jpeg, webp
- Quality Levels: low, medium, high
- Supports transparent backgrounds
- Can generate 1-10 images per request
- Supports image editing via edit endpoint
- Cost: ~$0.016 (low) to ~$0.15 (high) per image

**Strengths:**
- 4x faster than gpt-image-1, 20% lower cost
- Built-in reasoning and world knowledge
- Excellent text rendering in images
- Superior face and logo preservation during edits
- Multiple images per request
- Transparent background support
- Flexible output formats (png, jpeg, webp)

**Limitations:**
- Maximum resolution of 1536px on longest side
- Newer model, smaller community prompt library

**Ideal For:**
- Production quality image generation
- Iterative editing workflows
- Text-heavy images and infographics
- Logo and branding work
- Any use case requiring fast, high-quality output

### gpt-image-1 (April 2025)

**Specifications:**
- Resolution: up to 4096x4096
- Output Formats: png, jpeg, webp
- Quality Levels: low, medium, high
- Single image per request, no inpainting
- Cost: ~$0.02 (low), ~$0.07 (medium), ~$0.19 (high)

**Strengths:**
- Maximum resolution up to 4096x4096
- High-quality output with detailed rendering
- Flexible output formats (png, jpeg, webp)

**Limitations:**
- Single image per request only
- No inpainting support
- Slower and more expensive than gpt-image-1.5

**Ideal For:**
- Maximum resolution needs (large prints, detailed posters)
- Use cases requiring ultra-high-resolution output

### DALL-E 3 (Legacy)

**Specifications:**
- Resolution Options: 1024x1024 (square), 1024x1792 (portrait), 1792x1024 (landscape)
- Quality Levels: Standard, HD
- Speed: Moderate (higher quality takes longer)
- Cost: Higher than DALL-E 2
- Best Use Cases: High-quality illustrations, detailed scenes, creative interpretations

**Strengths:**
- Exceptional image quality and detail
- Superior understanding of natural language prompts
- Automatic prompt expansion/enhancement
- Excellent at creative interpretations
- Strong at rendering artistic styles
- Better coherence in complex scenes
- Improved safety and reduced bias

**Limitations:**
- Cannot edit existing images (text-to-image only)
- Cannot create variations of images
- More expensive than DALL-E 2
- No control over prompt expansion
- Limited to 3 resolution options

**Ideal For:**
- Artistic illustrations and concept art
- Marketing and advertising visuals
- Creative storytelling and narrative images
- Detailed character designs
- Fantasy and sci-fi scenes
- Natural language creative requests

### DALL-E 2 (Legacy)

**Specifications:**
- Resolution Options: 1024x1024, 512x512, 256x256
- Speed: Fast
- Cost: Lower than DALL-E 3
- Best Use Cases: Quick iterations, variations, image editing, cost-sensitive projects

**Strengths:**
- Image editing capabilities (inpainting)
- Can generate variations of existing images
- More literal interpretation of prompts (predictable)
- Lower cost per image
- Faster generation
- Good for prototyping
- Outpainting support

**Limitations:**
- Lower quality than DALL-E 3
- Less sophisticated prompt understanding
- More literal (less creative interpretation)
- May produce less coherent complex scenes

**Ideal For:**
- Budget-conscious projects
- Rapid prototyping and iteration
- Image editing and modifications
- Creating variations of a concept
- Outpainting (extending images)
- Quick mockups

## API Usage

### Basic Setup

```python
from openai import OpenAI
from pathlib import Path
import requests

# Initialize client (reads OPENAI_API_KEY from environment automatically)
client = OpenAI()
```

### gpt-image-1.5: Text-to-Image (Recommended)

```python
# Basic generation
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="A serene mountain lake at sunset with pine trees and mist",
    size="1024x1024",      # or "1536x1024", "1024x1536", "auto"
    quality="high",        # or "low", "medium"
    n=1,                   # 1-10 images per request
    output_format="png",   # or "jpeg", "webp"
)

# Get image URL
image_url = response.data[0].url

# Download and save
image_data = requests.get(image_url).content
Path("output.png").write_bytes(image_data)
```

### gpt-image-1.5: Multiple Images

```python
# Generate multiple images in a single request
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Minimalist tech company logo, abstract geometric design, blue and silver",
    size="1024x1024",
    quality="medium",
    n=4,  # Generate 4 variations at once
    output_format="png",
)

for idx, image_data in enumerate(response.data):
    img_bytes = requests.get(image_data.url).content
    Path(f"logo_option_{idx}.png").write_bytes(img_bytes)
```

### gpt-image-1.5: Image Editing

```python
# Edit an existing image via the edit endpoint
with open("original.png", "rb") as image_file:
    response = client.images.edit(
        model="gpt-image-1.5",
        image=image_file,
        prompt="Change the background to a tropical beach at sunset",
        size="1024x1024",
        quality="high",
    )

edited_url = response.data[0].url
```

### gpt-image-1: High Resolution

```python
# Generate ultra-high-resolution image
response = client.images.generate(
    model="gpt-image-1",
    prompt="Detailed botanical illustration of a rare orchid species, scientific accuracy",
    quality="high",
    output_format="png",
)

image_url = response.data[0].url
```

### DALL-E 3 (Legacy): Text-to-Image

```python
# Basic generation
response = client.images.generate(
    model="dall-e-3",
    prompt="A serene mountain lake at sunset with pine trees and mist",
    size="1024x1024",      # or "1024x1792", "1792x1024"
    quality="standard",    # or "hd"
    n=1,                   # DALL-E 3 only supports n=1
)

# Get image URL
image_url = response.data[0].url

# Download and save
image_data = requests.get(image_url).content
Path("output.png").write_bytes(image_data)

# Access revised prompt (DALL-E 3 expands prompts automatically)
revised_prompt = response.data[0].revised_prompt
print(f"DALL-E used this prompt: {revised_prompt}")
```

### DALL-E 3 (Legacy): High Quality (HD)

```python
# HD quality (more detail, higher cost)
response = client.images.generate(
    model="dall-e-3",
    prompt="Detailed portrait of a fantasy warrior, intricate armor, dramatic lighting",
    size="1024x1024",
    quality="hd",  # Enhanced detail and resolution
    n=1,
)

image_url = response.data[0].url
```

### DALL-E 3 (Legacy): Different Aspect Ratios

```python
# Square
response_square = client.images.generate(
    model="dall-e-3",
    prompt="Logo design for a tech startup",
    size="1024x1024",
)

# Portrait (vertical)
response_portrait = client.images.generate(
    model="dall-e-3",
    prompt="Full-body character design, fantasy knight",
    size="1024x1792",  # Tall format
)

# Landscape (horizontal)
response_landscape = client.images.generate(
    model="dall-e-3",
    prompt="Panoramic cityscape at night",
    size="1792x1024",  # Wide format
)
```

### DALL-E 2 (Legacy): Text-to-Image

```python
# Basic generation (can request multiple images)
response = client.images.generate(
    model="dall-e-2",
    prompt="A cute robot character in kawaii style",
    size="1024x1024",  # or "512x512", "256x256"
    n=2,               # Generate multiple variations
)

# Save all generated images
for idx, image_data in enumerate(response.data):
    image_url = image_data.url
    img_bytes = requests.get(image_url).content
    Path(f"output_{idx}.png").write_bytes(img_bytes)
```

### DALL-E 2 (Legacy): Create Variations

```python
# Generate variations of an existing image
with open("source_image.png", "rb") as image_file:
    response = client.images.create_variation(
        model="dall-e-2",
        image=image_file,
        n=3,  # Number of variations
        size="1024x1024",
    )

# Save variations
for idx, image_data in enumerate(response.data):
    img_bytes = requests.get(image_data.url).content
    Path(f"variation_{idx}.png").write_bytes(img_bytes)
```

### DALL-E 2 (Legacy): Edit Images (Inpainting)

```python
# Edit specific parts of an image using a mask
# Mask: transparent PNG where transparent areas will be regenerated

with open("original.png", "rb") as image_file, \
     open("mask.png", "rb") as mask_file:

    response = client.images.edit(
        model="dall-e-2",
        image=image_file,
        mask=mask_file,
        prompt="A sunflower field in the background",
        n=1,
        size="1024x1024",
    )

edited_url = response.data[0].url
```

## Prompt Engineering Best Practices

### gpt-image-1.5 and gpt-image-1 Prompting

The newer models have built-in reasoning and world knowledge, making them highly capable with both simple and detailed prompts:

**Text Rendering:**
```
"A professional infographic showing '5 Steps to Better Sleep' with numbered
sections, clean modern typography, blue and white color scheme"
```

**Precise Control:**
```
"Product photo of a ceramic coffee mug with the text 'Good Morning' in
elegant serif font, on a wooden table, soft natural lighting, transparent
background"
```

**Best Practices for gpt-image-1.5 / gpt-image-1:**
- Leverage built-in world knowledge for accurate depictions
- Use for text-heavy images (the models excel at text rendering)
- Specify output format based on needs (webp for web, png for transparency)
- Use quality levels strategically (low for drafts, high for finals)

### DALL-E 3 Prompting

DALL-E 3 automatically expands and enhances prompts, so you can be more conversational:

**Natural Language Works Well:**
```
"A cozy coffee shop interior with warm lighting, people reading books,
rain visible through large windows, artistic and inviting atmosphere"
```

**DALL-E 3 will expand this to something like:**
```
"A warm and inviting coffee shop interior scene with soft amber lighting
from pendant lamps, several patrons engaged in reading books at wooden tables,
large storefront windows revealing a gentle rain outside, potted plants on
windowsills, vintage decor elements, creating an artistic and comfortable
atmosphere, digital art style"
```

**Best Practices for DALL-E 3:**
- Use natural, descriptive language
- Focus on the essence of what you want
- Include style, mood, and atmosphere
- Don't over-engineer - let DALL-E expand
- Specify important details explicitly
- Trust the automatic enhancement

### DALL-E 2 Prompting

DALL-E 2 is more literal and requires more explicit direction:

**Be Very Specific:**
```
"Studio portrait photograph of a golden retriever wearing a red bandana,
professional lighting, neutral gray background, high detail, sharp focus,
looking at camera"
```

**Include All Important Details:**
- Subject positioning: "centered", "left side", "in foreground"
- Camera angle: "from above", "eye level", "low angle"
- Style markers: "digital art", "oil painting", "photography"
- Lighting: "soft lighting", "dramatic shadows", "bright and even"
- Mood/atmosphere explicitly stated

### Effective Prompt Structure

**Formula:** `[Subject] + [Action/Pose] + [Setting/Context] + [Style] + [Details] + [Mood/Lighting]`

**Examples:**

**Character Design:**
```
A mystical forest guardian character, standing pose with staff, ancient grove
setting, fantasy digital art style, glowing runes on armor, ethereal mist around
feet, dramatic lighting with dappled forest sunlight
```

**Product Visualization:**
```
Sleek wireless headphones, floating in air, minimal white background, studio
product photography, metallic silver finish with black accents, soft shadows,
professional commercial quality, high resolution
```

**Scene/Environment:**
```
Cyberpunk alleyway at night, neon signs in Japanese and English, rain-slicked
streets reflecting colorful lights, lone figure walking away, atmospheric fog,
cinematic composition, moody and atmospheric
```

**Abstract/Artistic:**
```
Abstract representation of music and emotion, flowing shapes and colors,
vibrant blues and oranges, watercolor and digital art fusion, dynamic movement,
dreamlike and expressive
```

## Model Comparison

| Feature | gpt-image-1.5 | gpt-image-1 | DALL-E 3 (Legacy) | DALL-E 2 (Legacy) |
|---------|----------------|-------------|-------------------|-------------------|
| **Image Quality** | Excellent | Excellent | Exceptional | Good |
| **Max Resolution** | 1536px | 4096px | 1792px | 1024px |
| **Output Formats** | png, jpeg, webp | png, jpeg, webp | png | png |
| **Quality Levels** | low, medium, high | low, medium, high | Standard, HD | Standard only |
| **Multiple Images/Request** | Yes (1-10) | No (n=1 only) | No (n=1 only) | Yes (n up to 10) |
| **Transparent Backgrounds** | Yes | No | No | No |
| **Text Rendering** | Excellent | Good | Limited | Poor |
| **Image Editing** | Yes (edit endpoint) | No | No | Yes (inpainting) |
| **Image Variations** | No | No | No | Yes |
| **Prompt Enhancement** | Built-in reasoning | Built-in reasoning | Auto-expansion | No |
| **Speed** | Fast | Moderate | Moderate | Fast |
| **Cost** | ~$0.016-$0.15 | ~$0.02-$0.19 | Higher | Lower |
| **Best For** | Production, editing, text | Max resolution | Creative art | Iterations, editing |

## Model Selection Guide

### Choose gpt-image-1.5 When (Recommended):
- You want the best balance of quality, speed, and cost
- Creating production-quality images
- Working with text-heavy images or infographics
- Need transparent backgrounds
- Iterative editing workflows
- Need multiple images per request
- Logo and branding work requiring face/logo preservation

### Choose gpt-image-1 When:
- Maximum resolution is required (up to 4096x4096)
- Creating large prints or posters
- Ultra-high-resolution output is the priority

### Choose DALL-E 3 (Legacy) When:
- Quality is paramount
- Creating final deliverables
- Need creative interpretation
- Working with natural language descriptions
- Want automatic prompt enhancement
- Creating artistic/illustrative content

### Choose DALL-E 2 (Legacy) When:
- Need to generate multiple variations
- Editing existing images (inpainting)
- Budget is constrained
- Need faster generation
- Want more literal interpretation
- Prototyping and iteration phase
- Need outpainting capabilities
- Generating many options to choose from

## Cost Optimization

**gpt-image-1.5 (Recommended):**
- Use "low" quality (~$0.016) for rapid prototyping
- Use "medium" for most production needs
- Reserve "high" (~$0.15) for final deliverables
- Generate multiple images per request to explore concepts efficiently

**gpt-image-1:**
- Use "low" quality (~$0.02) for drafts
- Use "medium" (~$0.07) for standard output
- Reserve "high" (~$0.19) for maximum resolution needs

**DALL-E 3 (Legacy):**
- Use "standard" quality for most needs
- Reserve "hd" for critical final deliverables
- Can only generate 1 image per request

**DALL-E 2 (Legacy):**
- Generate multiple variations in single request (cheaper per image)
- Use 512x512 for rapid prototyping
- Scale up to 1024x1024 only for selected concepts
- Leverage variations feature to explore concepts efficiently

**Recommended Approach:**
- Use gpt-image-1.5 with "low" quality for exploration and iteration
- Use gpt-image-1.5 with "high" quality for final production images
- Use gpt-image-1 only when you need resolution above 1536px

## Common Use Cases

### Marketing Visuals

**gpt-image-1.5** (recommended):
```python
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Dynamic marketing image showing diverse team collaborating on "
           "creative project, modern office environment, energetic and "
           "professional atmosphere, vibrant colors, lifestyle photography style",
    size="1536x1024",  # Landscape for web banners
    quality="high",
    output_format="jpeg",
)
```

### Logo Concepts

**gpt-image-1.5** (multiple options with transparency):
```python
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Minimalist tech company logo, abstract geometric network symbol, "
           "blue and silver colors, clean modern design, professional",
    size="1024x1024",
    quality="high",
    n=5,  # Generate 5 different concepts
    output_format="png",  # Supports transparency
)
```

### Text-Heavy Infographics

**gpt-image-1.5** (excellent text rendering):
```python
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Clean infographic titled 'The Water Cycle' with labeled diagrams "
           "showing evaporation, condensation, precipitation, and collection, "
           "educational style, blue color palette, clear readable text",
    size="1024x1536",  # Portrait for infographic
    quality="high",
    output_format="png",
)
```

### Character Design

**gpt-image-1.5** (recommended):
```python
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Fantasy character design: Elven archer with intricate leaf-pattern "
           "armor, holding ornate longbow, confident stance, forest background, "
           "detailed digital art style, vibrant fantasy colors",
    size="1024x1536",  # Portrait orientation
    quality="high",
    output_format="png",
)
```

### Ultra-High-Resolution Art

**gpt-image-1** (maximum resolution):
```python
response = client.images.generate(
    model="gpt-image-1",
    prompt="Highly detailed botanical illustration of a rare orchid, "
           "scientific accuracy, fine line work, watercolor style",
    quality="high",
    output_format="png",
)
```

### Product Mockups

**Start with gpt-image-1.5 low quality, refine with high quality**:
```python
# Iteration phase (low cost)
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Smartphone mockup showing weather app interface, hand holding phone, "
           "clean white background, professional product photography",
    size="1024x1024",
    quality="low",
    n=3,
)

# Final version (high quality)
response = client.images.generate(
    model="gpt-image-1.5",
    prompt="Professional product photo: hand holding modern smartphone displaying "
           "elegant weather app interface with gradient blue sky background, "
           "clean white studio background, soft professional lighting, "
           "commercial photography quality",
    size="1024x1024",
    quality="high",
    output_format="png",
)
```

## Error Handling

```python
from openai import OpenAI, OpenAIError

client = OpenAI()

try:
    response = client.images.generate(
        model="gpt-image-1.5",
        prompt=user_prompt,
        size="1024x1024",
        quality="high",
    )
    image_url = response.data[0].url

except OpenAIError as e:
    if "content_policy_violation" in str(e):
        print("Prompt violates content policy. Please rephrase.")
    elif "billing" in str(e).lower():
        print("Billing issue. Check your OpenAI account.")
    elif "rate_limit" in str(e).lower():
        print("Rate limit exceeded. Please wait and retry.")
    else:
        print(f"Error: {e}")
```

## Content Policy

OpenAI has strict content policies. Images cannot:
- Contain violence, gore, or disturbing content
- Include hate symbols or discriminatory content
- Feature sexual or adult content
- Depict illegal activities
- Show identifiable real people without consent
- Include copyrighted characters or IP

**Best Practices:**
- Keep prompts appropriate and respectful
- Avoid requesting specific real people
- Don't use copyrighted character names
- Focus on original creative concepts

## Rate Limits

- Free tier: Limited requests per minute
- Paid tier: Higher limits based on usage tier
- gpt-image-1.5: Optimized for throughput
- gpt-image-1: Moderate rate limits
- DALL-E 3: Generally lower rate limits
- DALL-E 2: Higher rate limits (cheaper)

Implement exponential backoff for production use:

```python
import time
from openai import OpenAI, RateLimitError

def generate_with_retry(client, **kwargs):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return client.images.generate(**kwargs)
        except RateLimitError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

## Best Practices Summary

1. **Use gpt-image-1.5 as the default** - best balance of quality, speed, and cost
2. **Use gpt-image-1 for max resolution** - when you need output above 1536px
3. **Leverage quality levels** - low for drafts, medium for production, high for finals
4. **Use transparent backgrounds** (gpt-image-1.5) for logos and compositing
5. **Generate multiple images** per request with gpt-image-1.5 for exploration
6. **Choose the right output format** - png for transparency, jpeg for photos, webp for web
7. **Handle errors gracefully** - content policy and rate limits are real
8. **Save all outputs** - generation isn't deterministic
9. **Respect content policy** - keep prompts appropriate
10. **Optimize costs** - use appropriate quality level for each stage

## API Resources

- **Official Documentation**: https://platform.openai.com/docs/guides/images
- **API Reference**: https://platform.openai.com/docs/api-reference/images
- **Python SDK**: https://github.com/openai/openai-python
- **Pricing**: https://openai.com/pricing
- **Content Policy**: https://openai.com/policies/usage-policies
- **Rate Limits**: https://platform.openai.com/docs/guides/rate-limits
