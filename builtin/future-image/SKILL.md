---
version: 1.1.2
name: future-image
description: Generate images from text prompts, edit existing images using natural-language instructions, and analyze images (OCR, visual Q&A, object recognition).
allowed-tools: Bash(future:*)
category: tools
---

> **Authentication is automatic.** The `future` CLI reads your credentials from `~/.future/agent/auth.json`. You do NOT need to find, configure, or pass API keys — just call the tools below.

# Image

## When to use this skill

Load this skill when the user asks to:
- Generate, create, or draw an image from a description
- Edit, modify, or transform an existing image
- Read text from an image (OCR) or describe what's in an image
- Analyze a photo, screenshot, or diagram
- 生成图片 / 画图 / 编辑图片 / 识别图片文字 / OCR / 描述图片内容

**If the user mentions any of the above, stop what you're doing and use this skill.** Do not try to find image tools elsewhere — use the tools below.

## How to use

All tools are called via the `future` CLI using the `bash` tool. Use `--output` to save images to files.

### Quick examples

```bash
# Generate an image from a text prompt (takes 1–5 minutes typically)
future tools call image_gen --prompt "A red fox in an autumn forest" --size "1024x1024" --output ./output.png --timeout 600

# Edit an existing image. Use --input <path> — the CLI handles base64 encoding internally.
future tools call image_edit --input /path/to/photo.png --prompt "Convert to watercolor painting" --output ./edited.png --timeout 600

# Edit with optional mask
future tools call image_edit --input /path/to/photo.png --mask /path/to/mask.png --prompt "Replace background with sky" --output ./edited.png --timeout 600

# Analyze an image. Use --input <path> — the CLI handles base64 encoding internally.
future tools call read_image --input /path/to/photo.png --question "Describe this image"
```

### When to use --stdin (large prompts)

For tools with very long prompts, `--stdin` can be cleaner than an inline argument. File inputs always use `--input <path>` so ARG_MAX is never an issue.

```bash
# Generate using --stdin (good for long/complex prompts)
future tools call image_gen --stdin --output ./output.png --timeout 600 <<'JSON'
{
  "prompt": "A complex scene with detailed description...",
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON
```

### Timeout and bash tool settings

**For `image_gen` and `image_edit`, always add `--timeout 600` to the `future tools call` command.** The CLI defaults to 600s for image tools, but larger images or higher quality may need more time. Actual generation times (for 1024×1024 images; larger sizes take longer):

| Quality | Typical time | Notes |
|---------|-------------|-------|
| `low` | 60–120s | Fastest; acceptable quality for drafts and simple images |
| `medium` | 120–300s | Recommended default; Chinese text adds ~30–60s |
| `high` | Unreliable | Frequently triggers `azure_image_transport_failed`; avoid |

**Two independent timeout layers must both be generous enough — they do NOT share a setting:**

1. **CLI HTTP timeout** — set via `--timeout 600` on the `future tools call` command.
2. **Bash tool process timeout** — set via `"timeout": 600` in the bash tool call parameters.

If either layer is too low, the generation will be killed.  When in doubt, use 600 for both:

```json
{"command": "future tools call image_gen --prompt \"...\" --output ./out.png --timeout 600", "timeout": 600}
```

`read_image` is much faster (typically 10–30 seconds) and does not need --timeout.

### File input

**Always use `--input <path>` for file inputs.** The CLI reads the file and encodes it automatically. Never put `image_b64` or `image_path` in the argument list. For `image_edit`, use `--mask <path>` for optional mask images.

## Error handling

**Authentication is automatic.** The `future` CLI reads credentials from `~/.future/agent/auth.json`. You do NOT need to run `future auth login` — if you see an error, read the actual error message first.

When `future tools call` fails, it prints a JSON error object. Parse it to understand the cause:

| Error pattern | Meaning | Action |
|---|---|---|
| `unauthorized` / `401` | Auth token missing or expired | Tell user: "Auth token may be expired, run `future auth login`" |
| `403` / `model_access_denied` | Model access denied (API key issue on server side) | Tell user the model returned 403, don't try to re-login |
| `upstream_request_failed` | RareMCP or upstream service unreachable | Retry once, then report to user |
| `insufficient_credit` | Account balance too low | Tell user to top up |
| `azure_image_transport_failed` | Image transport error (often from `quality: "high"`) | Retry with `quality: "medium"`; high quality is unreliable |
| `Invalid size` / `below minimum pixel budget` | Requested size is below 1024×1024 | Use `size: "1024x1024"` or larger; 1024 is the hard minimum |
| `Argument list too long` (bash error) | Very long --prompt string exceeds shell ARG_MAX | Use `--stdin` method (see examples above) |
| `This operation was aborted` (no JSON error) | CLI HTTP timeout (default 60s) exceeded | Regenerate with `--timeout 600` and bash tool `"timeout": 600` |

**Never run `future auth login` unprompted** — the error is almost always something else.

## Available tools

### image_gen
Generate one or more images from a natural-language text prompt. Returns base64-encoded image data. Use `--output` to save to a file. Generation typically takes 1–5 minutes.

Arguments: `--prompt "..." [--size "..."] [--quality "..."] [--n N] [--output_format "..."] [--output <path>] [--timeout <secs>]`

**Size notes:** `1024x1024` is the hard minimum — smaller sizes return a 400 error. `3840x2160` (4K) works but produces large files (~5 MB+ for PNG).

**Quality notes:** `"low"` is fastest (~60–120s) and cheapest — good for drafts, simple images, or when iterating rapidly. `"medium"` (default, ~120–300s) is recommended for most final use cases; Chinese/Japanese/Korean text generation adds ~30–60s due to character rendering complexity. `"high"` is **unreliable** and often triggers `azure_image_transport_failed` — prefer `"medium"` and only try `"high"` as a last resort.

**n parameter:** `n > 1` may not produce multiple output files — the CLI's `--output` flag only saves one file. If you need multiple images, make multiple separate calls.

### image_edit
Modify an existing image according to a text instruction. Use `--input <path>` for the source image and `--mask <path>` for an optional mask — the CLI handles base64 encoding internally. 

Arguments: `--input <path> [--mask <path>] --prompt "..." [--size "..."] [--quality "..."] [--output_format "..."]`

**Quality:** Same as image_gen — prefer `"medium"`. `"high"` is unreliable.

**Size:** The `size` parameter here controls the *output* size, not the input. The source image is automatically resized to fit.

### read_image
Analyze an image and answer questions about its content. Use `--input <path>` for the image — the CLI handles base64 encoding internally. 

Arguments: `--input <path> --question "..." [--mime_type "..."] [--max_tokens N]`

**Performance:** `read_image` is fast (10–30 seconds). It does not need `--timeout`.

**Chinese/OCR:** Chinese text recognition is highly accurate. The model can read horizontal and vertical text, stamps, seals, and decorative calligraphy. For OCR tasks, phrase the question explicitly: "What Chinese text is visible in this image? Read all visible characters."
