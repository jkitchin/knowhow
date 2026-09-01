# Atlas Cloud Image Provider

Atlas Cloud is an optional image provider for the video-storytelling workflow. The default image-generation skill and ElevenLabs narration remain unchanged.

## Setup

```bash
export ATLASCLOUD_API_KEY="your-api-key"
# Optional media API override; do not use the OpenAI-compatible /v1 LLM base here.
export ATLAS_MEDIA_API_BASE="https://api.atlascloud.ai/api/v1"
```

The helper uses the current `google/nano-banana-2/text-to-image` schema:

```bash
python scripts/atlas_image.py \
  "A square story frame, consistent character design, warm studio lighting" \
  --aspect-ratio 1:1 \
  --resolution 1k \
  --format jpeg \
  --output scene-00.jpg
```

For each later scene, keep the same style and character locks in the prompt. This text-to-image route does not accept a previous image; do not claim reference-image continuity. Use descriptive locks consistently and review each frame before continuing.

## Request Safety

The generation `POST /api/v1/model/generateImage` is sent exactly once. The helper never retries that billable request. It only retries transient prediction `GET` failures up to three times and stops after a bounded number of polls.

Successful predictions return an `outputs` array. Passing `--output` downloads the first URL to the requested file. Keep API keys in environment variables and never place them in prompts, command output, or committed files.
