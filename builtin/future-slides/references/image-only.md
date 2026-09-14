# Opt-In Image-Only Decks

Use this route only when the user requests image-based slides or accepts the loss
of native editing. State that outputs are PNG/PDF, not editable PowerPoint objects.
Native/hybrid PPTX remains the default. Do not label a wrapper PPTX as editable.

Load `future-image` and consult `future tools describe image_gen` / `image_edit` /
`read_image` for current contracts. CLI authentication is handled by Future; do not
read keys. Generation and remote image review may incur costs and transmit data.
Do not send private figures or documents without authorization.

## Plan and manifest

Reuse audience, language, slide count, style and sources. Show a concise outline,
exact visible text and resource implications before billed generation unless already
approved. Style can be minimal, dark, sketched, corporate, vibrant, research-poster,
data-driven or custom; never impose a scientific motif on unrelated content.
Use a new output/revision directory, leaving original files unchanged.

Write a separate image manifest with the file tool (not the native schema):

```json
{
  "language": "English",
  "slides": [
    {
      "idx": "01",
      "title": "Example",
      "image": "slide_01.png",
      "prompt": "Exact title: 'Example'. High-contrast minimal composition; no invented data or references.",
      "size": "1792x1024",
      "quality": "medium",
      "reviewed": false
    }
  ]
}
```

The slides array defines page order. Paths are relative to the manifest directory.
Use the same visual language across pages. Respect actual supported image dimensions:
1792×1024 is not 16:9. Verify final geometry; do not crop content merely to force a
ratio. Quantitative charts require real data and verification. Generated schematics
are illustrations, not experimental evidence. Preserve sources and authorized photos.

## Bounded generation

Read `scripts/run_deck.py`; resolve its path from the skill directory.

```bash
python /absolute/skill/scripts/run_deck.py generate /absolute/output/image-deck.json --only 01 --timeout 600
python /absolute/skill/scripts/run_deck.py check /absolute/output/image-deck.json
```

Only `generate` invokes billed generation. Default to one bounded selection at a
time. Approved concurrency may use `--only 02,03,04 --jobs 3`; this is not a monetary
budget enforcer. The runner validates newly produced PNGs, records a unique receipt,
settles the current batch and stops after failure/uncertainty. It never silently
retries or mistakes an old image for success. Use new filenames for replacements.

CLI HTTP timeout plus 30 seconds is the per-process allowance; the enclosing tool
must allow for every batch. Do not assume a background job survives cancellation.
A local timeout does not establish remote cancellation or zero billing. Inspect the
receipt/status before retrying uncertain work and obtain needed retry authorization.
For auth failure ask the user to log in; never initiate login without permission.

## Review and assembly

Inspect every final page for exact text/numbers, readability, crops and source fidelity.
When remote review is allowed, `future-image` provides `read_image`; for a limited or
local-only review disclose the actual unchecked pages. Fix authorized illustrative
assets only; do not use generative edits to reconstruct scientific evidence.

For each reviewed image record its current `sha256`, `reviewed: true` and a meaningful
`review_note`. Updating the image invalidates old review evidence. Fields alone are
not proof that visual or scientific review occurred.

```bash
python /absolute/skill/scripts/run_deck.py assemble /absolute/output/image-deck.json --output slides.pdf
```

Assembly requires hash-bound review records and uses exactly the selected image per
slide in manifest order, never a filename glob. Check final PDF page count, ordering,
geometry and readability. Deliver PDF, chosen PNGs and manifest with costs/limitations.
Never call partial generation complete. Image-runner regressions remain in `tests/`.
