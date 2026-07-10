---
version: 2.0.0
name: future-slides
description: Generate presentation slides as images from a Markdown report using Future OS image tools. Supports multiple visual styles (clean, dark, sketched, corporate, vibrant, or user-defined). The user picks or describes a style before generation. Triggered when the user asks to create PPT/slides/presentation from content.
allowed-tools: Bash(future:*)
category: creative
---

# Future Slides Generator

Convert a Markdown report into PNG slides with a consistent visual aesthetic, then optionally package them as a lossless PDF.

> **Future OS platform rule:** use the `future` CLI for all image generation, image editing, and image analysis. Do not call legacy local image scripts or non-Future image analyzers.

> **Authentication is automatic.** The `future` CLI reads credentials from `~/.future/agent/auth.json`. Do not find, configure, or pass API keys manually. If a `future tools call` command returns an auth error, report the actual error and tell the user to run `future auth login`.

## Future CLI Tools

All image tools are called through `future tools call`.

```bash
# Generate a slide image from a prompt.
future tools call image_gen --stdin --output "$WORK_DIR/slide_NN.png" <<'JSON'
{
  "prompt": "<SLIDE_PROMPT>",
  "size": "1792x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON

# Edit an existing slide. Use image_path; the CLI handles base64 encoding.
future tools call image_edit --stdin --output "$WORK_DIR/slide_NN_fixed.png" <<JSON
{
  "prompt": "<EDIT_PROMPT>",
  "image_path": "$WORK_DIR/slide_NN.png",
  "size": "1792x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON

# Analyze a generated slide. Use image_path; the CLI handles base64 encoding.
future tools call read_image --stdin <<JSON
{
  "image_path": "$WORK_DIR/slide_NN.png",
  "question": "Check all visible Chinese text. Report Traditional Chinese, typos, hallucinated text, layout problems, and whether the style matches the deck.",
  "mime_type": "image/png",
  "max_tokens": 2000
}
JSON
```

Use `--stdin` for slide tools by default because prompts often contain quotes, newlines, and Chinese punctuation.

## Output Directory Convention

**Never save directly as bare files in the working directory.** Always create a timestamped subdirectory:

```bash
WORK_DIR="./slides_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$WORK_DIR"
```

All prompts, scripts, logs, PNG files, and final PDFs live under this directory.

## Step 0: Choose a Visual Style (Required)

**Before generating any slides, let the user choose a visual style.** Present a few curated presets and always offer a custom option:

```
请选择幻灯片的视觉风格：

1. 极简干净 — 白色背景，无衬线字体风格，细线条图标，克制的配色
2. 深色科技 — 深灰/黑色背景，霓虹高亮，科技感线条和几何图形
3. 手绘素描 — 白色纸张背景，墨水飞溅，随性手绘线条，漫画素描质感，粉彩配色
4. 现代商务 — 浅灰/米白背景，圆角卡片，扁平图标，专业蓝灰配色
5. 活力多彩 — 鲜艳渐变背景，粗体大字，趣味图标，高对比度

您也可以输入自定义风格描述（如："日式浮世绘风格"、"杂志排版风格"、"复古胶片风格"等）
```

Wait for the user's explicit choice. Record it as the **Style Description** for the deck.

**After the user picks a style, compose a Style Suffix** that will be appended to every slide prompt:

```text
<Style Description>, widescreen 16:9 composition. High quality anti-aliased rendering. Simplified Chinese only. No watermark.
```

- For **极简干净**: suffix should include "Clean minimalist vector illustration, white background, thin sans-serif typography, restrained color palette".
- For **深色科技**: suffix should include "Dark gradient background, neon accent highlights, tech-inspired geometric lines, high contrast".
- For **手绘素描**: suffix should include "Japanese illustration style sketchnote, white paper background, ink splatters, free-flowing hand-drawn lines, comic sketch texture, pastel watercolor, photorealistic scan of hand-drawn art on paper".
- For **现代商务**: suffix should include "Modern corporate presentation, light grey background, rounded card layout, flat vector icons, professional blue-grey palette".
- For **活力多彩**: suffix should include "Vibrant gradient background, bold oversized typography, playful icons, high contrast".
- For **custom** (user-provided description): use the user's description verbatim plus the common suffix.

The Style Suffix must stay **identical** for every slide in the deck to maintain visual consistency.

## Global Style Rules

Every slide must follow these rules:

- Use widescreen output. Prefer Future image tool size `1792x1024`; it is the closest supported wide format to 16:9. Keep all content inside a safe 16:9 composition with generous margins.
- Use `quality: "medium"` only. Chinese text with high quality can time out.
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
Cover slide. Large Chinese headline: '[TITLE]'.
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
Below, numbered items in cards or bubbles, each with Chinese text.
Items: '01 [SECTION1]', '02 [SECTION2]', ...
Decorative: style-appropriate corner elements.
{Style Suffix}
```

### D. Quote Slide

```text
Quote slide. Centered large text: '[FULL_QUOTE_WITH_INSPIRING_TONE]'.
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
| `## 一、xxx` chapter heading | Section Divider (B) | After TOC |
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
    "title": "封面标题",
    "prompt": "..."
  }
]
```

Rules:

- Slide 01 is always the cover.
- Slide 02 is always the TOC and lists all final chapter titles.
- Each chapter has one Section Divider plus 2-5 content slides.
- Every visible Chinese string must appear exactly in `prompt`.
- Every prompt includes the Style Suffix (from Step 0) and the exact Simplified Chinese warning.

### Step 2: Present Outline to User for Confirmation

Before generating any images, show the user a concise outline of all planned slides:

```text
幻灯片大纲（共 N 张）
─────────────────────────────────
01 封面: [标题]
02 目录: [章节列表]
03 章节: [章节名]
04 内容: [内容标题]
...
NN 结束页: [结束语]
─────────────────────────────────
请确认是否按此大纲生成？（是/否或有修改意见）
```

Wait for explicit user confirmation. If the user requests changes, update `slide_prompts.json` and present the outline again. Only proceed after confirmation.

### Step 3: Create Work Directory and Per-Slide Scripts

The generated scripts must match the confirmed outline exactly: same slide count, same order, same slide numbers, same prompt intent.

Create one standalone script per slide. Each script generates exactly one image and writes status markers (`STARTED`, `SUCCESS`, `FAILED`) to its own log.

```bash
#!/bin/bash
set -u

SLIDE="01"
WORK_DIR="./slides_YYYYMMDD_HHMMSS"
LOG="$WORK_DIR/gen_${SLIDE}.log"

echo "[$(date '+%H:%M:%S')] STARTED" > "$LOG"

future tools call image_gen --stdin --output "$WORK_DIR/slide_${SLIDE}.png" >> "$LOG" 2>&1 <<'JSON'
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

Create a master runner script that launches per-slide scripts in batches of 3 to reduce rate limiting:

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

Run the master script in the background:

```bash
bash "$WORK_DIR/run_all.sh" > "$WORK_DIR/master.log" 2>&1 &
```

Check progress:

```bash
for f in "$WORK_DIR"/gen_*.log; do
  echo "$(basename "$f" .log): $(tail -1 "$f")"
done
```

### Step 5: Verify Slides with `read_image`

After generation, inspect all slides when practical. For large decks, inspect at least the cover, TOC, every Section Divider, every slide with dense text, and at least 5 content slides.

```bash
future tools call read_image --stdin <<JSON
{
  "image_path": "$WORK_DIR/slide_NN.png",
  "question": "Review this Chinese presentation slide. Check every visible Chinese character for Simplified Chinese, typos, hallucinated words, missing text, extra text, and Traditional Chinese. Also check layout, visual consistency with the deck style, and text readability. Return a concise list of issues or say PASS.",
  "mime_type": "image/png",
  "max_tokens": 2000
}
JSON
```

Verification checklist:

- Chinese text is Simplified Chinese only.
- No typos, hallucinated words, malformed glyphs, or missing strokes.
- Watch common mistakes: `多媒体`, `我们` becoming `我們`, `从` becoming `從`, `选` becoming `選`.
- Required exact strings from the prompt are present.
- No extra title, logo, watermark, or unrelated text.
- Style is consistent across all pages.

### Step 6: Fix Individual Slides

Identify failed slides:

```bash
grep -l "FAILED" "$WORK_DIR"/gen_*.log
```

For visual or text issues, tighten the prompt and rerun only the affected slide script:

```bash
bash "$WORK_DIR/gen_XX.sh"
```

Common prompt repairs:

- For Traditional Chinese: repeat `Simplified Chinese only. Use 我们, 从, 选 exactly; do not use 我們, 從, 選.`
- For typos: list the exact problematic string and say `Use the exact text '[TEXT]' with no substitutions.`
- For missing quote text: include the full quote verbatim and say `The quote must be visible and centered.`

### Step 7: Photo / Avatar Integration (Optional)

If the user provides a reference photo, first describe the visible features with `read_image`, then use that textual description in the slide edit prompt.

```bash
future tools call read_image --stdin <<JSON
{
  "image_path": "/path/to/reference_photo.png",
  "question": "Describe the person's visible features for creating a respectful illustration. Mention hair, glasses, expression, clothing, and face shape. Do not identify the person.",
  "mime_type": "image/png",
  "max_tokens": 800
}
JSON

future tools call image_edit --stdin --output "$WORK_DIR/slide_NN_fixed.png" <<JSON
{
  "image_path": "$WORK_DIR/slide_NN.png",
  "prompt": "Replace the person with an illustration using these visible features: [FEATURE_DESCRIPTION]. Blend naturally into the background. Keep all Chinese text and icons unchanged. {Style Suffix}",
  "size": "1792x1024",
  "quality": "medium",
  "output_format": "png"
}
JSON
```

Only use a real photo when the user explicitly asks for one.

### Step 8: Assemble PDF

After all PNG slides pass verification, combine them into a PDF.

```bash
# Best when available: embeds PNGs directly.
img2pdf "$WORK_DIR"/slide_*.png -o "$WORK_DIR/slides.pdf"
```

Fallback with Pillow:

```bash
WORK_DIR="$WORK_DIR" python3 -c "
from PIL import Image
import glob, os
work_dir = os.environ['WORK_DIR']
files = sorted(glob.glob(f'{work_dir}/slide_*.png'))
images = [Image.open(f).convert('RGB') for f in files]
images[0].save(f'{work_dir}/slides.pdf', save_all=True, append_images=images[1:])
"
```

Upload or share the PDF only through user-approved platform tools. Do not hard-code a Feishu/Lark folder token in this skill.

## Error Handling

When `future tools call` fails, read the JSON error first.

| Error pattern | Meaning | Action |
|---|---|---|
| `unauthorized` / `401` | Auth token missing or expired | Tell the user to run `future auth login` |
| `403` / `model_access_denied` | Model access denied on the server side | Report the access issue; do not retry login |
| `upstream_request_failed` | Remote image service or MCP service unreachable | Retry once, then report the failure |
| `insufficient_credit` | Account balance too low | Tell the user to top up |
| `429` / rate limit | Too much concurrency | Wait 60 seconds and rerun failed slides one by one |

Never run `future auth login` unprompted.

## Known Pitfalls

| # | Pitfall | Frequency | Solution |
|---|---|---|---|
| 1 | Traditional Chinese appears | High | Append `Simplified Chinese only.` and verify with `read_image` |
| 2 | Chinese typos in generated images | High | Put exact Chinese strings in prompts and inspect every visible character |
| 3 | Hallucinated words | High | Never describe text meaning; quote the exact visible text |
| 4 | Image generation timeout | Medium | Keep `quality` at `medium`; retry once; reduce dense text |
| 5 | 429 rate limiting | Medium | Run at most 3 slides concurrently; retry failed slides individually |
| 6 | Quote slide misses text | Low | Include the full quote verbatim and state it must be visible |
| 7 | PDF assembly fails because `img2pdf` is missing | Low | Use the Pillow fallback |
