---
version: 1.1.0
name: future-image
description: Generate images from text prompts, edit existing images using natural-language instructions, and analyze images (OCR, visual Q&A, object recognition). Image generation supports configurable size and quality. Editing accepts both source image and optional mask. Analysis returns structured text descriptions.
allowed-tools: Bash(future:*)
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
future tools call image_gen --args '{"prompt": "A red fox in an autumn forest", "size": "1024x1024"}' --output ./output.png --timeout 600

# Edit an existing image. Use image_b64 (base64-encoded image data).
IMG_B64=$(base64 -i /path/to/photo.png | tr -d '\n')
future tools call image_edit --args '{"prompt": "Convert to watercolor painting", "image_b64": "'"$IMG_B64"'"}' --output ./edited.png --timeout 600

# Analyze an image. Use image_b64 (base64-encoded image data).
IMG_B64=$(base64 -i /path/to/photo.png | tr -d '\n')
future tools call read_image --args '{"image_b64": "'"$IMG_B64"'", "question": "Describe this image"}'
```

### When to use --stdin (large images)

When the base64-encoded image is large (> ~200 KB, or the image file > ~150 KB), the shell's `ARG_MAX` limit may be exceeded when embedding the base64 string directly in `--args`. In this case **all three tools** support `--stdin`:

```bash
# Generate using --stdin (good for long/complex prompts too)
future tools call image_gen --stdin --output ./output.png --timeout 600 <<'JSON'
{
  "prompt": "A complex scene with detailed description...",
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON

# Edit large image via --stdin
future tools call image_edit --stdin --output ./edited.png --timeout 600 <<JSON
{
  "prompt": "Apply watercolor style",
  "image_b64": "$(base64 -i /path/to/large_photo.png | tr -d '\n')",
  "size": "1024x1024",
  "quality": "medium"
}
JSON

# Analyze large image via --stdin (recommended for images >1 MB)
future tools call read_image --stdin <<JSON
{
  "image_b64": "$(base64 -i /path/to/large_scan.png | tr -d '\n')",
  "question": "Describe all text visible in this image",
  "max_tokens": 1000
}
JSON
```

### Timeout and bash tool settings

**For `image_gen` and `image_edit`, always add `--timeout 600` to the `future tools call` command.** Most generations complete in 1–5 minutes, but the CLI defaults to a 60-second HTTP timeout. The bash tool's own `timeout` parameter (default 120s) must also match:

```json
{"command": "future tools call image_gen --args '...' --output ./out.png --timeout 600", "timeout": 600}
```

`read_image` is much faster (typically 10–30 seconds) and does not need --timeout.

### Encoding images

**Use `image_b64` for image data.** The API expects base64-encoded image strings. Encode files with: `base64 -i <file> | tr -d '\n'`.

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
| `Argument list too long` (bash error) | Base64 string exceeds shell ARG_MAX | Use `--stdin` method (see examples above) |

**Never run `future auth login` unprompted** — the error is almost always something else.

## Available tools

### image_gen
Generate one or more images from a natural-language text prompt. Returns base64-encoded image data. Use `--output` to save to a file. Generation typically takes 1–5 minutes.

Arguments: `{"prompt": "string (required)", "size": "string (default: \"1024x1024\", options: 1024x1024, 1792x1024, 1024x1792, 2560x1440, 3840x2160)", "quality": "string (default: \"medium\", options: low, medium, high)", "n": "int (1–10, default: 1)", "output_format": "string (default: \"png\", options: png, jpeg)"}`

**Size notes:** `1024x1024` is the hard minimum — smaller sizes return a 400 error. `3840x2160` (4K) works but produces large files (~5 MB+ for PNG).

**Quality notes:** `"low"` is fastest and cheapest. `"medium"` (default) is recommended for most use cases. `"high"` is **unreliable** and often triggers `azure_image_transport_failed` — prefer "medium" and only try "high" as a fallback if "medium" quality is insufficient.

**n parameter:** `n > 1` may not produce multiple output files — the CLI's `--output` flag only saves one file. If you need multiple images, make multiple separate calls.

### image_edit
Modify an existing image according to a text instruction. Use `image_b64` with base64-encoded image data. Encode with `base64 -i <file> | tr -d '\n'`. For large source images, use `--stdin` to avoid shell argument size limits.

Arguments: `{"prompt": "string (required)", "image_b64": "string (required, base64-encoded image)", "mask_b64": "string (optional, base64-encoded mask image)", "size": "string (default: \"1024x1024\")", "quality": "string (default: \"medium\", options: low, medium, high)", "output_format": "string (default: \"png\", options: png, jpeg)"}`

**Quality:** Same as image_gen — prefer `"medium"`. `"high"` is unreliable.

**Size:** The `size` parameter here controls the *output* size, not the input. The source image is automatically resized to fit.

### read_image
Analyze an image and answer questions about its content. Use `image_b64` with base64-encoded image data. Encode with `base64 -i <file> | tr -d '\n'`. For large images, use `--stdin` to avoid shell argument size limits.

Arguments: `{"image_b64": "string (required, base64-encoded image)", "question": "string (required)", "mime_type": "string (default: \"image/png\")", "max_tokens": "integer (default: 2000)"}`

**Performance:** `read_image` is fast (10–30 seconds). It does not need `--timeout`.

**Chinese/OCR:** Chinese text recognition is highly accurate. The model can read horizontal and vertical text, stamps, seals, and decorative calligraphy. For OCR tasks, phrase the question explicitly: "What Chinese text is visible in this image? Read all visible characters."
