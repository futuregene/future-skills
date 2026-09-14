# Validation and Release

## Independent checks

| Layer | Evidence | Does NOT prove |
|---|---|---|
| Manifest/structure | saved objects, dimensions, text, native tables/charts, image hashes, endpoint bindings | glyph fit, scientific validity, Office appearance |
| Content/science | source-to-slide comparison of claims, values, units, formulas and references | visual clarity or independent reproduction |
| Native render | PDF/images produced from the actual PPTX in a named client | identical appearance in other clients |
| Visual review | inspection of the final rendered pages, with issues/fixes recorded | correctness of the original study |

The bundled build/check receipt deliberately reports content review, native rendering
and visual review as `not_performed`. Do not edit it to claim those checks occurred.
Write separate actual review evidence with input/output hashes, renderer/version,
review method, pages checked, defects, unresolved warnings and limitations.

## Structural and editability checks

Run `native_deck.py check` against the exact manifest and release. It detects stale
source/PPTX/assets; checks page and object counts, geometry, text, image bytes/crops,
native tables, chart cache values and connector endpoint bindings. It does not check
every possible DrawingML style or recalculate scientific data.

On a disposable copy, actually edit representative text, a shape color, a table cell
and chart data if present; save/reopen and check persistence. For diagrams also check
native connection IDs. A target-client drag/edit test is needed for user interaction
and routing behavior. Do not mutate the release just to run tests.

The backend warns about intersecting content rectangles and small type. Review each
warning: intentional overlap and legitimate small labels exist. It cannot measure
actual glyph bounds or see text inside an image. Negative fixtures should include
out-of-bounds nodes, duplicate IDs, broken image hashes, chart dimension mismatches,
nonfinite data, stale releases and detached connectors—not just a successful build.

## Render the PPTX, not a sibling HTML

Use an installed, authorized local PowerPoint, LibreOffice, Keynote or other suitable
renderer. Detect availability; never assume macOS/Keynote or a fixed application path.
Use a fresh output directory and an isolated profile/document to avoid disturbing
other work. A LibreOffice invocation, when it is installed, has this structure:

```text
<soffice executable> -env:UserInstallation=<isolated-profile-file-URI> --headless --convert-to pdf --outdir <fresh-directory> <absolute-deck.pptx>
```

Pass an argv array via subprocess, use pathlib to construct the profile's file URI,
and set a bounded timeout. Do not run untrusted shell fragments or kill existing
Office processes. Conversion failures/timeouts are failures; keep the exact error
and do not accept an old PDF as new success. Only close documents/processes owned by
this task. If temporary rendering cleanup fails, disclose it rather than deleting
unrelated user profiles or documents. Do not silently install a renderer.

Verify output exists, PDF page count/order/dimensions, and that it belongs to this
PPTX hash. Render that PDF to review images with an available local tool. Inspect
every slide, especially mixed-script text, equation symbols, chart legends/axes,
image crops and connector routes. Wait for fonts/resources if a renderer needs it.

A LibreOffice pass is not a PowerPoint pass; record the actual application and fonts.
HTML-derived PDF may also be delivered as a sibling export, labeled as such. If no
renderer is available, deliver PPTX with structural checks and explicitly mark native
visual verification outstanding. Do not claim success based on the renderer exiting
zero or on object bounding boxes alone.

## Visual/content review questions

- Is the intended message understandable without reading paragraphs aloud?
- Are every title, legend, scale bar, footnote and panel label visible?
- Are formulas, minus signs, Greek/CJK glyphs and superscripts correct?
- Do measured/uncertain/proposed results remain distinguishable?
- Are axes, units, baseline choices, error bars and image crops faithful?
- Do arrows connect the intended objects without crossing content?
- Do captions and citations remain legible at the target presentation size?
- Are edits limited to the requested scope, with no stale duplicate pages?

For confidential work, use permitted local inspection/OCR or request human review.
Remote image analysis requires approval of that data transfer. OCR verifies some
text, not overall beauty or scientific validity. Record partial review honestly.

## Release checks

Scan notes, hidden slides, metadata, embedded chart workbooks and external links.
Check that source data inside the PPTX are authorized for the recipients. Internal
preparation notes do not belong in public speaker notes by default. Keep required
scientific caveats and attribution visible; do not confuse them with internal notes.

Deliver the chosen revision only, with editable source when requested and a concise
validation summary. New changes invalidate old render/review hashes. Rebuild and
review the changed slides plus affected numbering, references and shared content.
Budget exhausted or renderer unavailable means an explicitly limited draft, not a
fabricated final approval.
