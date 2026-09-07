# Evidence, Lineage and Claim Verification

## Source cards

Keep cards as structured notes or a table in the workspace. Minimum fields:

| Field | Meaning |
|---|---|
| source_id / identity | Stable ID, title, author/organization, DOI/PMID/URL or local document ID |
| version / access | Publication/update date where known, retrieval date, final URL, access limitations |
| content level | snippet, generated summary, abstract, selected original passages, or full body actually obtained |
| origin / lineage | Original study/data/announcement, secondary analysis, or repost; underlying evidence ID and derivation links where known |
| evidence location | Exact relevant section/page/paragraph/table and concise excerpt or faithful paraphrase |
| applicability | Population, setting, assumptions, method limitations, funding/interest and date constraints where relevant |

Do not imply full-text review when only an abstract was returned. `search_paper` may
return `ai_summary`; it is a lead, not original evidence. Inspect `get_paper`'s actual
`body_text` and its completeness before claiming to have checked methods or results.
Store only authorized material; use necessary excerpts rather than reproducing entire
copyrighted works without a valid basis.

## Source independence and quality

- Trace each important factual claim back to its study, dataset or originating document.
  Three articles repeating one press release are three pages, but one evidence lineage.
- Merge mirrors, reposts, identifier aliases and versions of the same work for reference
  counts. Distinct analyses may remain distinct bibliography entries, while still sharing
  the same underlying data; report those quantities separately.
- Unknown independence stays unknown. Do not label sources independent just because
  their domains, authors or wording differ. Conversely, different studies from one
  organization are not automatically the same evidence; inspect how evidence was generated.
- Authority is claim-specific. An official specification is strong evidence of what it
  specifies, not necessarily of real-world performance. A primary bug report may be
  better evidence of an observed failure than a prestigious secondary news article.
- Agreement, accessibility, recency and methodological quality are separate properties.
  Do not derive confidence by counting agreeing URLs or automatically preferring new
  material over a relevant foundational source.

## Claim-to-evidence record

For each decision-critical claim, record:

`claim_id | exact claim and scope | source_ids + locations | lineage groups | support/contradiction | verification state | limitations/action`

Classify evidence as direct observation/reported study result, analytical derivation,
quoted assertion, estimate or hypothesis. Separate what a source reports from what the
researcher concludes. Preserve units, denominators, dates, study conditions and uncertainty.

A claim is **supported within scope** only when inspected evidence supports its actual
wording and important qualifications. Use **contradicted**, **unresolved**, or **not yet
checked** as appropriate. An inaccessible URL is an access failure, not proof the claim
is false; a reachable page that lacks the asserted result is not support.

When sources disagree, check versions, populations, definitions, units and study design
before calling it a scientific controversy. Keep genuine disagreement and its implications;
a user's preference for one side is not additional evidence.

## Handling failed citations

Every key claim must be checked against actual relevant source content at all depths.
Drafting can add or strengthen claims, so repeat the check for changed final statements.

If one key citation fails:
1. Identify the claim and whether the failure is access, mismatch, missing qualifications,
   erroneous bibliographic identity or contrary evidence.
2. Within budget, find the authorized original version or independent support, and
   update the claim record. Do not keep retrying an unrelated or irrelevant page.
3. Otherwise remove/revise the claim or mark it unresolved; limit any dependent conclusion.
   Report precisely which part remains unverified. Four successful checks cannot cancel
   a failed fifth key citation.

Optional sampling of secondary citations is additional quality control, not a replacement
for checking key claims. Disclose sample selection and failures; do not use a universal
allowed failure percentage as a pass gate.

## Confidence and review

Use a reasoned checklist: directness, provenance, methods, scope fit, counterevidence,
and verification completeness. Describe uncertainty rather than assigning an uncalibrated
0–1 correctness score. If a user asks for numeric rubric scores, define them as subjective
rubric ratings, not probabilities or a substitute for unresolved evidence.

Self-review is not independent review. Record the reviewer, prior involvement and shared
materials when independent review was required. An AI-written summary or a second run
of the same extraction does not by itself provide independent scientific corroboration.
