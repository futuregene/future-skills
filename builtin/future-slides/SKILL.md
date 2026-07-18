---
version: 2.0.2
name: future-slides
description: Generate presentation slides as images from a Markdown report. Supports 8 curated visual styles (minimal, dark-tech, sketched, corporate, vibrant, research-poster, molecular-aesthetic, data-driven) plus custom style input. Triggered when the user asks to create slides, PPT, or presentation from content.
allowed-tools: Bash(future:*)
category: tools
---

# Future Slides Generator

Convert a Markdown report into a coherent deck of PNG slides, then optionally package them as a lossless PDF.

> **Future OS platform rule:** use the `future` CLI for all image generation, image editing, and image analysis. Do not call legacy local image scripts or non-Future image analyzers.

> **Authentication is automatic.** The `future` CLI reads credentials from `~/.future/agent/auth.json`. Do not find, configure, or pass API keys manually. If a `future tools call` command returns an auth error, report the actual error and tell the user to run `future auth login`.

> **Tip:** use `future tools describe <tool>` to see all available arguments for any tool.
## Future CLI Tools

All image tools are called through `future tools call`.

```bash
# Generate a slide image from a prompt.
# --timeout 600 is REQUIRED: medium quality + Chinese text takes 120–300s, default 60s HTTP timeout will abort.
future tools call image_gen --stdin --output "$WORK_DIR/slide_NN.png" --timeout 600 <<'JSON'
{
  "prompt": "<SLIDE_PROMPT>",
  "size": "1792x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON

# Edit an existing slide. The API expects base64-encoded image data.
IMG_B64=$(base64 -i "$WORK_DIR/slide_NN.png" | tr -d '\n')
future tools call image_edit --stdin --output "$WORK_DIR/slide_NN_fixed.png" --timeout 600 <<JSON
{
  "prompt": "<EDIT_PROMPT>",
  "image_b64": "$IMG_B64",
  "size": "1792x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON

# Analyze a generated slide. The API expects base64-encoded image data.
# read_image is fast (10–30s), no --timeout needed.
IMG_B64=$(base64 -i "$WORK_DIR/slide_NN.png" | tr -d '\n')
future tools call read_image --stdin <<JSON
{
  "image_b64": "$IMG_B64",
  "question": "Check all visible text. Report typos, hallucinated text, layout problems, and whether the style matches the deck.",
  "mime_type": "image/png",
  "max_tokens": 2000
}
JSON
```

**Timeout note for bash tool:** When calling `image_gen` or `image_edit` via the bash tool, set the bash tool's own `timeout` parameter to at least `600` as well. The CLI's `--timeout` controls the HTTP layer; the bash tool timeout controls the process itself. Both must be generous enough.

Use `--stdin` for slide tools because prompts often contain quotes, newlines, and special characters.

## Output Directory Convention

**Never save directly as bare files in the working directory.** Always create a timestamped subdirectory:

```bash
WORK_DIR="./slides_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$WORK_DIR"
```

All prompts, scripts, logs, PNG files, and final PDFs live under this directory.

## Step 0: Choose a Visual Style (Required)

**Before generating any slides, present the user with a style menu.** Always include these 8 presets plus a custom option:

```
Choose a visual style for the slide deck:

1. Minimal Clean — white background, sans-serif typography, thin line icons, restrained color palette
2. Dark Tech — dark grey/black background, neon accent highlights, geometric tech lines, high contrast
3. Sketched — white paper background, ink splatters, free-flowing hand-drawn lines, comic sketch texture, pastel watercolor
4. Modern Corporate — light grey/warm beige background, rounded card layout, flat vector icons, professional blue-grey palette
5. Vibrant Impact — bold gradient backgrounds, oversized typography, playful icons, high contrast
6. Research Poster — clean academic conference poster aesthetic, clear section hierarchy, professional typography, subtle institutional color accents
7. Molecular Aesthetic — dark or gradient background with abstract molecular structures, protein-surface textures, crystallography-inspired geometry, glowing ligand-like highlights
8. Data-Driven — dashboard-inspired layouts, clean data visualization aesthetics, subtle grid patterns, metric cards with accent colors

Or describe your own custom style (e.g. "Japanese ukiyo-e woodblock print", "magazine editorial layout", "retro film photography", "futuristic holographic UI").
```

Wait for the user's explicit choice. Record it as the **Style Description** for the deck.

**After the user picks a style, compose a Style Suffix** appended to every slide prompt:

```text
<Style Description>, widescreen 16:9 composition. High quality anti-aliased rendering. Simplified Chinese only. No watermark.
```

- **Presets 1-5**: expand into a detailed one-sentence style description.
- **Presets 6-8**: research-specific presets. Include "scientific presentation" context, appropriate medium descriptors (e.g. "vector illustration" for poster, "3D render with subsurface scattering" for molecular), and "publication-quality rendering".
- **Custom**: use the user's description verbatim plus the common suffix.

The Style Suffix must stay **identical** for every slide in the deck to maintain visual consistency.

## Global Style Rules

Every slide must follow these rules:

- Use widescreen output. Prefer Future image tool size `1792x1024`; it is the closest supported wide format to 16:9. Keep all content inside a safe 16:9 composition with generous margins.
- Use `quality: "medium"` for best results. Chinese text with `quality: "high"` is unreliable and often triggers `azure_image_transport_failed`. With `quality: "medium"`, always pass `--timeout 600` to the CLI and set bash tool timeout to ≥600s — generation typically takes 120–300 seconds for 1792×1024 slides with Chinese text. If you experience persistent timeouts, fall back to `quality: "low"` which completes in ~60–120s and still produces acceptable results.
- Append the **Style Suffix** (from Step 0) to every slide prompt.
- Append this exact text at the end of every prompt:

  ```text
  Simplified Chinese only. Must use exact Simplified Chinese characters with NO typos. Double-check every character.
  ```

- Put every required Chinese string verbatim in the prompt. Do not describe the meaning and expect the model to infer the text.
- Keep the deck visually consistent. Reuse the same style suffix, color palette, and typography on every slide.
- Include a table of contents slide as slide 02 immediately after the cover.
- Keep each slide concise. Use at most 5 bullet points per content slide.

## Slide Types and Prompt Templates

All prompts below MUST include the `{Style Suffix}` placeholder. Replace it with the actual suffix composed in Step 0.

### A. Cover Slide

```text
Cover slide. Large headline: '[TITLE]'.
Below, smaller subtitle: '[SUBTITLE]'.
Bottom text: '[AUTHOR_INFO]'.
Surrounding decorative elements: [topic-related visuals — icons, geometric shapes, abstract patterns].
{Style Suffix}
```

### B. Section Divider

```text
Section divider. Large bold number '[NN]' centered.
Below, title: '[SECTION_NAME]'.
Minimal decorative elements.
{Style Suffix}
```

### C. Table of Contents

```text
Table of contents. Large title '目录' centered.
Below, numbered items in cards or bubbles, each with text.
Items: '01 [SECTION1]', '02 [SECTION2]', ...
Decorative: style-appropriate corner elements.
{Style Suffix}
```

### D. Quote Slide

```text
Quote slide. Centered large text: '[FULL_QUOTE]'.
Below: '—— [ATTRIBUTION]'.
{Style Suffix}
```

### E. Content / Bullet Points

```text
Bullet points slide. Headline: '[PAGE_TITLE]'.
Points: '[POINT1]'; '[POINT2]'; '[POINT3]'.
Simple icons matching the topic.
{Style Suffix}
```

### F. Two-Column Comparison

```text
Comparison slide. Headline: '[TITLE]'.
Left column: '[LEFT_LABEL]'. Text: '[LEFT_POINTS]'.
Right column: '[RIGHT_LABEL]'. Text: '[RIGHT_POINTS]'.
Bottom quote: '[QUOTE]'.
{Style Suffix}
```

### G. Case Study

```text
Case study slide. Headline: '[CASE_TITLE]'.
Illustration of [topic — e.g. automotive factory, campus, clinic, research lab].
Text: '[KEY_FACTS]'.
{Style Suffix}
```

### H. End Slide

```text
End slide. Centered large text: '[CLOSING_LINE]'.
Below: '[SUBLINE]'.
{Style Suffix}
```

## Chapter Rules

1. Every chapter must have a Section Divider slide.
2. Every chapter must have at least 2 content slides, excluding the Section Divider itself.
3. Every chapter must have at most 5 content slides, excluding the Section Divider itself.
4. If a chapter cannot meet the 2-slide minimum, merge it with the adjacent chapter and use one merged Section Divider.
5. Content slides per chapter are the slides between its Section Divider and the next Section Divider or End Slide.

## Report-to-Slide Mapping

Every deck starts with Cover + TOC. The TOC is always slide 02.

| Report Element | Slide Type | Position |
|---|---|---|
| Deck metadata | Cover (A) | Slide 01 |
| Chapter list | Table of Contents (C) | Slide 02 |
| `## Section heading` | Section Divider (B) | After TOC |
| Title + 3-5 bullet points | Content (E) | After section divider |
| `> quote` block | Quote (D) | As needed |
| Case study | Case Study (G) | As needed |
| Comparison section | Two-Column Comparison (F) | As needed |
| Table | Split into multiple Content (E) slides | As needed |
| End of report | End Slide (H) | Last slide |

Use the naming convention `slide_NN.png`, where `NN` is zero-padded.

## Execution Workflow

### Step 1: Generate Slide Prompts

Read the Markdown report. Build `slide_prompts.json` in the work directory with:

```json
[
  {
    "idx": "01",
    "type": "cover",
    "title": "Cover Title",
    "prompt": "..."
  }
]
```

Rules:

- Slide 01 is always the cover.
- Slide 02 is always the TOC and lists all final chapter titles.
- Each chapter has one Section Divider plus 2-5 content slides.
- Every visible text string must appear exactly in `prompt`.
- Every prompt includes the Style Suffix (from Step 0) and the exact language warning.

### Step 2: Present Outline for Confirmation

Before generating any images, show a concise outline:

```text
Slide Outline (N slides total)
─────────────────────────────────
01 Cover: [title]
02 TOC: [chapter list]
03 Section: [section name]
04 Content: [content title]
...
NN End: [closing message]
─────────────────────────────────
Proceed with this outline? (yes / no / modifications)
```

Wait for explicit user confirmation before generating.

### Step 3: Create Work Directory and Per-Slide Scripts

Create one standalone script per slide. Each script generates exactly one image and writes status markers (`STARTED`, `SUCCESS`, `FAILED`) to its own log.

```bash
#!/bin/bash
set -u

SLIDE="01"
WORK_DIR="./slides_YYYYMMDD_HHMMSS"
LOG="$WORK_DIR/gen_${SLIDE}.log"

echo "[$(date '+%H:%M:%S')] STARTED" > "$LOG"

future tools call image_gen --stdin --output "$WORK_DIR/slide_${SLIDE}.png" --timeout 600 >> "$LOG" 2>&1 <<'JSON'
{
  "prompt": "<SLIDE_PROMPT>",
  "size": "1792x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON

if [ $? -eq 0 ] && [ -f "$WORK_DIR/slide_${SLIDE}.png" ]; then
  echo "[$(date '+%H:%M:%S')] SUCCESS" >> "$LOG"
else
  echo "[$(date '+%H:%M:%S')] FAILED" >> "$LOG"
fi
```

Create a master runner script that launches per-slide scripts in batches of 3:

```bash
#!/bin/bash
set -u

WORK_DIR="./slides_YYYYMMDD_HHMMSS"

bash "$WORK_DIR/gen_01.sh" &
bash "$WORK_DIR/gen_02.sh" &
bash "$WORK_DIR/gen_03.sh" &
wait
sleep 5

bash "$WORK_DIR/gen_04.sh" &
bash "$WORK_DIR/gen_05.sh" &
bash "$WORK_DIR/gen_06.sh" &
wait
sleep 5

echo "ALL DONE"
```

### Step 4: Run and Track Generation

```bash
bash "$WORK_DIR/run_all.sh" > "$WORK_DIR/master.log" 2>&1 &
```

Check progress:

```bash
for f in "$WORK_DIR"/gen_*.log; do
  echo "$(basename "$f" .log): $(tail -1 "$f")"
done
```

### Step 5: Verify Slides

Inspect all slides when practical. For large decks, inspect at least the cover, TOC, every Section Divider, every slide with dense text, and at least 5 content slides.

```bash
IMG_B64=$(base64 -i "$WORK_DIR/slide_NN.png" | tr -d '\n')
future tools call read_image --stdin <<JSON
{
  "image_b64": "$IMG_B64",
  "question": "Review this presentation slide. Check every visible text character for typos, hallucinated words, missing text, and extra text. Also check layout, visual consistency with the deck style, and text readability. Return a concise list of issues or say PASS.",
  "mime_type": "image/png",
  "max_tokens": 2000
}
JSON
```

### Step 6: Fix Individual Slides

```bash
grep -l "FAILED" "$WORK_DIR"/gen_*.log
```

Rerun only the affected slide script after tightening the prompt.

### Step 7: Photo / Avatar Integration (Optional)

If the user provides a reference photo, first describe the visible features with `read_image`, then use that textual description in the slide edit prompt. Only use a real photo when the user explicitly asks for one.

### Step 8: Assemble PDF

```bash
# Preferred: embeds PNGs directly.
img2pdf "$WORK_DIR"/slide_*.png -o "$WORK_DIR/slides.pdf"
```

Fallback with Pillow when `img2pdf` is unavailable.

## Error Handling

| Error pattern | Meaning | Action |
|---|---|---|
| `unauthorized` / `401` | Auth token missing or expired | Tell the user to run `future auth login` |
| `403` / `model_access_denied` | Model access denied on the server | Report the access issue; do not retry login |
| `upstream_request_failed` | Remote image or MCP service unreachable | Retry once, then report |
| `This operation was aborted` | CLI HTTP timeout (default 60s) exceeded during generation | Regenerate with `--timeout 600` on the `future tools call` command |
| `azure_image_transport_failed` | Image transport error (often from `quality: "high"`) | Retry with `quality: "medium"` or `"low"`; high quality is unreliable |
| `insufficient_credit` | Account balance too low | Tell the user to top up |
| `429` / rate limit | Too much concurrency | Wait 60s and rerun failed slides one by one |

Never run `future auth login` unprompted.

## Known Pitfalls

| # | Pitfall | Frequency | Solution |
|---|---|---|---|
| 1 | Wrong language characters in images | High | Append explicit language instruction and verify with `read_image` |
| 2 | Typos in generated images | High | Put exact text strings in prompts and inspect every visible character |
| 3 | Hallucinated words | High | Never describe text meaning; quote the exact visible text |
| 4 | Image generation timeout | High | Always pass `--timeout 600` to CLI and set bash tool timeout ≥600s. If still timing out, fall back to `quality: "low"` (60–120s). Reduce dense text as last resort. |
| 5 | 429 rate limiting | Medium | Run at most 3 slides concurrently; retry failed slides individually |
| 6 | Quote slide misses text | Low | Include the full quote verbatim and state it must be visible |
| 7 | PDF assembly fails (missing `img2pdf`) | Low | Use the Pillow fallback |
| 8 | Bash tool timeout kills process before image completes | Medium | When calling scripts via bash tool, always set `"timeout": 600` in the tool call parameters. The CLI `--timeout` and bash tool timeout are independent layers — both must cover the generation window. |
