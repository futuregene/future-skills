---
version: 3.0.0
name: future-slides
description: >
  Turn a report or outline into a coherent deck of PNG slide images and an optional
  PDF. Supports minimal, dark-tech, sketched, corporate, vibrant, research-poster,
  molecular-aesthetic, data-driven and custom styles. Use for presentation/slide
  creation; clarify when the user needs editable PPTX rather than image-based slides.
allowed-tools: Bash(future:*)
category: tools
---

# Image-Based Slide Decks

Use Future CLI tools for image generation/editing/analysis. Authentication is
handled by the CLI; never read or embed API keys. Consult `future tools describe
<tool>` and `future-image` for the current backend contract rather than assuming
historical quality, latency or size observations are permanent limitations.

## 1. Agree on the deck contract

Reuse the user's supplied language, audience, style, slide count, source material,
format and existing approvals. Ask only about unresolved decisions. Explicitly
state that this workflow delivers PNGs/PDF, not editable slide objects. If editable
PPTX is required, agree an editable-authoring workflow instead of mislabeling a PDF
or image-only deck as editable PowerPoint.

Offer these style choices only when useful and not already specified:

| Style | Visual direction |
|---|---|
| Minimal | White, clean typography, restrained palette |
| Dark tech | Dark background, geometric layout, accent highlights |
| Sketched | Hand-drawn lines, paper texture, soft colors |
| Corporate | Professional typography and muted business palette |
| Vibrant | Bold colors, high contrast, large type |
| Research poster | Academic structure, clear figures/captions |
| Molecular aesthetic | Molecular/structural imagery without fabricated data |
| Data-driven | Charts, metric cards and explicit units |
| Custom | The user's own visual description |

Present one concise outline with page count, visible text, visual purpose and
resource implications before billed generation unless already approved. Adapt to
the requested duration/count: cover, contents, section dividers and end pages are
optional, not mandatory extra pages. Do not impose Chinese on an English deck.

Use a unique output directory (date plus unique revision/run suffix). Keep source
materials unchanged. All manifest paths are relative to this deck directory.

## 2. Write the manifest and prompts

Create `deck.json` with the file tool. The slides array is the authoritative page
order; `idx` values are unique labels, not an invitation to sort by filename.

```json
{
  "language": "English",
  "slides": [
    {
      "idx": "01",
      "title": "Example title",
      "image": "slide_01.png",
      "prompt": "Cover slide. Exact title: 'Example title'. Minimal white style. English text. Keep content within a safe widescreen area. No watermark.",
      "size": "1792x1024",
      "quality": "medium",
      "reviewed": false
    }
  ]
}
```

Quote the exact visible text in each prompt. Use one consistent style description,
colors, language and typography across pages. Respect the backend's actual size
support: 1792x1024 is not exactly 16:9. Verify/crop to the requested final geometry
without cutting content, or choose an actually supported matching size.

Use actual data for quantitative charts and verify values/axes after rendering.
A generative diagram is not experimental evidence. Preserve references and source
attribution. If a user requests their real photo, edit/composite the supplied asset
with authorization rather than substituting a generated lookalike.

## 3. Generate with the tested runner

Read `scripts/run_deck.py` when running or modifying the workflow. Dependencies are
in `requirements.txt`; reuse installed packages or an authorized task-local environment.
Resolve the script path against this skill directory, not the process cwd.

```bash
# Explicitly billed action; generate one bounded selection at a time by default.
python /absolute/skill/path/scripts/run_deck.py generate /absolute/deck/deck.json --only 01 --timeout 600

# Optional approved concurrency, at most 3. This is not a monetary budget enforcer.
python /absolute/skill/path/scripts/run_deck.py generate /absolute/deck/deck.json --only 02,03,04 --jobs 3 --timeout 600

# Technical file validation, no model calls.
python /absolute/skill/path/scripts/run_deck.py check /absolute/deck/deck.json
```

The runner calls `future tools call image_gen --stdin --output ...`, requests one
image per page, validates a new PNG before publishing it, writes a unique generation
receipt, and returns nonzero on failure. It settles the current batch and does not
dispatch later batches after failure. It never silently retries or mistakes an old
file for new success. Use a new revision filename when regenerating an existing page.

The process allowance is HTTP timeout + 30 seconds **per batch**. The enclosing shell
allowance must cover all selected batches plus startup/validation. Prefer one bounded
batch per tool call. If the harness cannot wait that long, use an explicitly owned
persistent runner/monitor; do not assume a background shell survives cancellation.

A timeout can leave remote generation/billing unresolved. Read the receipt and actual
error first; inspect upstream status if supported. Do not automatically resubmit an
uncertain request. Report the ambiguity and obtain any needed retry authorization.
For a definite auth error ask the user to log in; do not launch login unprompted.

## 4. Review and fix

Load `future-image` and inspect every final slide when a complete deck review is
required. If a limited visual review is explicitly agreed, disclose the unchecked
pages and do not mark them reviewed merely to pass assembly.

```bash
future tools call read_image --input /absolute/deck/slide_01.png --question "Check exact text, numbers, missing/extra content, readability, layout and consistency with the agreed source and style."
future tools call image_edit --input /absolute/deck/slide_01.png --prompt "Correct only the identified issue, preserving approved content and style" --output /absolute/deck/slide_01_fixed.png --timeout 600
```

After fixing, update only that page's `image` path in the manifest. Reinspect it,
run `check`, and record its current `sha256`, `reviewed: true` and a nonempty
`review_note` identifying evidence/issues resolved. These fields record a review;
their presence alone does not prove visual or scientific correctness. Never copy
review status/hash onto a modified image without rechecking it.

## 5. Assemble and deliver

```bash
python /absolute/skill/path/scripts/run_deck.py assemble /absolute/deck/deck.json --output slides.pdf
```

Assembly validates every manifest image and its hash-bound review record, then uses
exactly one chosen image per slide in manifest order. It never globs `slide_*.png`,
so original/fixed copies and unrelated files cannot add duplicate pages. Open the
result and verify final page count, ordering, geometry and readability. Deliver the
PDF, selected PNGs and manifest with real validation/review limits and pending costs.
Do not report a partially generated deck as complete.

## Regression checks

From this skill directory run `python -m unittest discover -s tests -v`. Tests mock
the Future generation process (no paid calls), exercise failure/timeout/partial-deck
handling, stale files, manifest order, revision selection and actual local PDF assembly.
