# Research and Serious-Presentation Quality

Apply these rules across disciplines. Do not assume the user works in biology,
conducts experiments, writes in English, or wants a journal-paper structure.

## Evidence and claims

- Separate observations, analyses, interpretations, hypotheses, simulations and
  proposed work. Label synthetic examples as synthetic on the slide itself.
- Preserve denominators, sample sizes, populations, comparators, units, measurement
  conditions and uncertainty when they change interpretation. Distinguish technical
  replicates from independent samples; association from causation; exploratory
  findings from confirmatory tests. Do not invent missing information.
- Report relevant effect sizes/intervals rather than substituting significance stars
  for results. Preserve error-bar definitions (SD/SE/CI) and statistical assumptions.
- Do not promote literature claims to the user's results. Keep preliminary,
  unpublished or non-peer-reviewed status where material to interpretation.
- For a proposal, keep expected outcomes and milestones distinct from achievements.
  For a technical review, separate measured performance from design intent.
- A heading can summarize a supported result, but must not overclaim. Avoid both
  exaggerated headlines and unexplained collections of numbers.

## Citation and provenance

Maintain a source registry with stable IDs, citation text and a precise locator
(e.g. DOI plus figure/page, dataset version plus sheet/range, local file plus page).
Registry URLs are references, not permission to fetch or upload. Verify citations
against material actually inspected; mark inaccessible or secondary-only evidence.
Use compact visible citations on the relevant slide, with full references in an
appendix if useful. Speaker notes alone are insufficient when slides circulate as PDF.
The bundled manifest links element `source_ids` to the registry but does not invent
or automatically render a bibliography: author the visible citation text explicitly.

Trace quantitative charts back to data and calculation code, including filtering,
normalization, excluded observations, uncertainty and transformations. Avoid
independent retyping of the same statistic on multiple slides. Native chart caches
and workbooks are not evidence that the calculation is correct.

## Figures, formulas and data graphics

- Prefer source plots, vectors or high-resolution images; preserve licensing,
  attribution, panel labels, legends, color scales, axis labels and scale bars.
- Keep the original unchanged. Record authorized crops/transforms and source hashes.
  Use contain/letterboxing unless a crop is intentional and checked. Cropping that
  changes interpretation (e.g. omitted control, y-axis or contradictory panel) is not
  merely a layout choice.
- Do not use generative image editing to repair scientific text, plot values,
  microscopy, gels, spectra, molecule identity or other evidentiary content.
  Illustrative schematics must be distinguishable from measured structures/results.
- Use native charts when data and chart semantics can be represented faithfully.
  Nonuniform numerical x values require a numeric axis, not equally spaced labels.
  Do not silently drop error bars, log scales, censored observations or missingness.
  Native tables should retain units and precision. Avoid 3D and decorative effects
  that distort quantitative comparisons; disclose nonzero/truncated axes when used.
- Keep math notation exact, including Greek, subscripts, superscripts, minus signs,
  vector notation and units. The starter schema provides plain text, not an equation
  engine. Use a suitable native equation/custom authoring path, or a clearly disclosed
  vector/raster formula asset plus editable LaTeX source; do not claim the latter is
  a native editable equation.
- Use colorblind-considerate contrast plus labels/line styles, not color alone.
  Thin lines and small legends need inspection at the actual presentation size.

## Privacy and publication

Confidential source material stays local unless the user authorizes the specific
remote processing. This includes figures sent to image analysis, not just PDFs sent
for parsing. Check participant identifiers, unpublished measurements and embedded
workbooks before sharing. Keep internal reviewer/preparation notes out of public
speaker notes, metadata and hidden slides. Do not automatically strip limitations or
attribution merely because a slide is crowded.
