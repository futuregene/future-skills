# Authoring Routes and Design

## Preferred route: semantic content → explicit scene → native PPTX

Keep content, evidence and layout separate enough to revise them safely. A small
manifest with stable slide/object IDs is sufficient; do not build a general layout
framework for a one-off deck. The agent designs each slide, then the deterministic
backend serializes it. Same-source HTML can be a useful optional reading view, but
it is not a substitute for rendering the PPTX.

The supplied `scripts/native_deck.py` accepts explicit dimensions in inches; it does
not choose layouts, measure font glyphs, solve routing or fit text automatically.
It provides native text, text-bearing shapes, tables, limited charts, contain-fit
images and bound connectors. Unsupported fields fail instead of disappearing.
Use `references/native-format.md` for the exact supported contract.

Use a task-local authoring script when required features are not supported; preserve
stable object names, provenance, editability tests and review evidence. Do not expand
the bundled schema for a single project without tests and a genuinely reusable need.

## Layout selection, not a single research template

Use only layouts that fit the content. Useful building blocks include:

- One question plus one large evidence panel and a short takeaway.
- Methods pipeline with text inside its native nodes and bound connectors.
- Two-column comparison with aligned quantities and explicit comparator conditions.
- Results plot plus a narrow interpretation/limitations column.
- A native table for a small number of exact values; move large tables to appendix.
- Equation or model schematic plus variable definitions and assumptions.
- Timeline, study design, uncertainty/risk map, or decision/next-step page.

For a default 13.33×7.5 inch deck, a starting grid is 0.5 inch outer margins, a
0.7–1 inch heading zone, and a separate citation/footer zone. Typical starting sizes
are 28–36pt headings, 20–24pt body and 14–16pt references; these are heuristics, not
universal bounds. Poster dimensions, room/projector conditions and complex scripts
need different choices. Use typography, spacing and a restrained accent consistently.
Allow whitespace. Never force every page into three cards or identical bullets.

Prefer a semantic block with wrapping to per-line/per-glyph boxes. For simple cards,
put the text inside the shape so moving the card also moves its text. The starter
backend does not create arbitrary groups. For compound visuals needing group-level
editing, use native group shapes in the task-local authoring code and test transforms.

Connectors must attach to real native shape connection sites, not merely end at the
same pixel. Use stable ports; verify a drag in a target client before claiming the
routing remains desirable after editing. Straight/elbow routing is intentionally
limited; loops, branching buses and obstacle avoidance need explicit routes and
rendered checks. Avoid font arrows, loose triangle arrowheads and detached line art.

## Fonts and compatibility

Select installed fonts appropriate to the language and target audience. Record Latin
and East Asian choices; never assume PingFang, Microsoft YaHei, Arial or Noto is
available everywhere. The sample requests fonts; it does not bundle them. Installing
or embedding fonts requires availability/licensing checks and user authorization.
Use portable substitutions deliberately, then rerender. Test Greek, mixed CJK/Latin,
math and RTL text where used. Merely setting a font name is not a font-availability test.

## Other routes and honest limits

**Original scientific graphics:** keep them as images when data are unavailable or a
faithful native chart cannot represent their semantics. Supply source data/code when
available. The surrounding title, caption and interpretation remain native text.
Original figure pixels are not made editable by attaching a workbook with guessed data.

**HTML/PDF reconstruction:** extracting selectable PDF text and vector paths can
recover editable objects without OCR. It loses paragraph, chart and diagram semantics;
font baselines, kerning, clipping, layering and unsupported paths need reconciliation.
Merge spans into meaningful text blocks rather than thousands of glyph boxes. This
is a separate best-effort conversion, not a universal converter in the starter tool.

**Existing PPTX/templates:** inspect masters, fonts, theme, notes, charts, links and
unsupported objects first. Work on a copy and compare before/after. Libraries may
lose unsupported features during save; native Office automation may be preferable
when available and authorized. Never promise arbitrary lossless round trips.

**Image-only:** read `references/image-only.md`. Only use it when requested; an image
inside a PPTX is still not editable slide content. Image generation can assist with
illustrative assets, not replace scientific measurement or native information.

## Local revision contract

A source rebuild replaces the generated deck, not just one manually edited slide.
Confirm which file is authoritative before rebuilding; reconcile user's edits first.
Preserve slide/element IDs, change only the intended scope and compare source and
saved objects. Cross-slide numeric values do not automatically recalculate in PPTX.
Publish a new revision; never silently overwrite older deliveries. Keep a manifest
and hashes with the source, and bind each review to the exact rendered revision.
