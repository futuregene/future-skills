# Native Manifest v1

Used by `scripts/native_deck.py`, NOT the opt-in image runner. Start with
`assets/example-native.json`. All sizes/positions are inches except font sizes
(points). Canvas, language, fonts, colors and slide count are configurable. No page
layout, study type or discipline is mandatory. Unknown fields fail explicitly.

## Top-level fields

| Field | Contract |
|---|---|
| `schema_version` | integer `1` |
| `title`, `language` | nonempty strings; use a language tag such as `en-US` or `zh-CN` |
| `width`, `height` | positive finite canvas dimensions, at most 56 inches |
| `theme` | `font`, `cjk_font`, and six-digit RGB `background`, `foreground`, `accent`; all required |
| `sources` | optional array of `{id, citation, locator}`; reference metadata only, no automatic fetching |
| `slides` | nonempty array; order is authoritative |

A slide has `id`, `title`, `elements` and optional `speaker_notes`. `title` is source
metadata; put a text element on the slide when a visible title is needed. Notes are
public output: never put confidential preparation notes there by accident.

Slide/element/source IDs are unique in their own scope, using letters, numbers,
underscore or hyphen. Each element has `id`, `kind`, optional `source_ids`, and the
fields below. Referenced sources must exist. Citation metadata is NOT automatically
visible: include explicit text elements for on-slide citations and figure captions.

## Elements

All elements except connectors need `x`, `y`, `w`, `h`; dimensions must be positive
and contained by the canvas. Content rectangle overlap produces warnings, not a claim
of actual rendered overlap. Z-order follows array order, except connectors are emitted
last after their targets exist. Put background shapes first.

### `text`

Required `text`; optional `size` (default 22pt), `color` (theme foreground), `bold`
(boolean), `align` (`left`, `center`, `right`). Newlines create paragraphs in one
native text box. Wrapping is enabled, automatic shrinking is not. Plain Unicode is
supported; rich runs, equations, vertical/RTL layout and automatic bullets require a
task-local authoring extension and target-client checks.

### `shape`

Optional `shape`: `rect` (default), `round_rect`, `ellipse`; `fill`, `line` RGB colors;
optional `text` with the same typography options as a text element. A text-bearing
shape is a movable/editable card without disconnected overlay text. Blank shapes
can act as panels. Fill defaults to background, line to accent. Text margins are
small fixed insets; visual fit is not measured.

### `image`

Required `path`, `sha256`, `alt`. Path is a local PNG/JPEG relative to the manifest,
with forward slashes, no drive/absolute paths or traversal outside the deck directory
(including symlinks). Hash the exact authorized asset. Images are contain-fit and
centered within the given box, preserving aspect ratio and original bytes with zero
PowerPoint crop. The hash establishes byte identity, not content correctness. An
intentional crop must be a separately reviewed asset with its own provenance/hash.
Original labels inside images are not native editable text.

### `table`

Required `rows`: nonempty rectangular array of strings. Optional `size` (default
18pt), `header` (default true). Emits a native PowerPoint table, equal-width columns
and equal-height rows; no spreadsheet formulas. Use explicit units/precision. Complex
merged cells, column widths or multi-page tables need task-local authoring code.

### `chart`

Required `chart_type`: `column`, `bar`, `line` or `scatter`; nonempty `series`.
Optional `x_title`, `y_title` label the physical horizontal/vertical axes.

Category charts (`column`, `bar`, `line`):

```json
{"chart_type":"column","categories":["Control","Treatment"],
 "series":[{"name":"Synthetic response (a.u.)","values":[1.0,1.2]}]}
```

`categories` are distinct nonempty strings. Each series has a distinct `name` and
finite numeric `values` of matching length. Do not encode missing values as zero.

Numeric scatter:

```json
{"chart_type":"scatter","series":[{"name":"Synthetic observations",
 "points":[[0,1.0],[2,1.2],[10,1.1]]}],"x_title":"Time (h)","y_title":"Response (a.u.)"}
```

Scatter uses true numeric x/y points (not evenly spaced categories), with no
`categories` field. Both routes generate native charts plus embedded workbooks, so
chart data can be edited in PowerPoint. The starter backend intentionally does NOT
support error bars, missing values, log scales, custom ranges or complex plots. Do
not discard those semantics. Use an appropriate task-local native extension or an
original/source-generated figure with data/code and disclose its editing limits.
Chart styling uses native defaults; inspect contrast and axis formatting, especially
on nonwhite backgrounds. `source_ids` links provenance; missing references warn.

### `connector`

```json
{"id":"flow","kind":"connector",
 "source":{"id":"step-a","port":"right"},
 "target":{"id":"step-b","port":"left"},
 "routing":"straight","arrow":true}
```

`source` and `target` must name different native `shape` elements on the same slide.
Ports: `top`, `left`, `bottom`, `right`. `routing`: `straight` (default) or `elbow`;
optional RGB `color` and boolean `arrow` (default true). Native endpoint bindings
are serialized, not just matching coordinates. Arbitrary groups, loops, obstacle
avoidance and branch buses are not implemented. Inspect routes and drag behavior
in the target client; source binding does not guarantee aesthetically good rerouting.

## Output and checks

```bash
python /absolute/skill/scripts/native_deck.py build /absolute/deck/deck.json --output talk-r1.pptx
python /absolute/skill/scripts/native_deck.py check /absolute/deck/deck.json --output talk-r1.pptx
```

Both paths resolve relative to the manifest. Build refuses existing PPTX or receipt;
use a new revision name. It generates and reopens the PPTX before publishing, checks
objects against the scene, then exclusively creates the PPTX and `.build.json` receipt.
No external model calls, scientific validation, rendering or font installation occurs.

Receipt includes manifest/PPTX/image hashes, per-slide counts, warnings and separate
`not_performed` states for content review, native render and visual review. Check
recomputes hashes and structural assertions; manual PPTX edits or changed sources
invalidate the build receipt. A hash is provenance evidence, not an approval signature.
Keep real visual/scientific review evidence separate and bound to the exact revision.
