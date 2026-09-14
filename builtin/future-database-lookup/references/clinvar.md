# ClinVar API Reference

## Identifier semantics

ClinVar Variation IDs are numeric; VCV accessions (optionally versioned) identify
variant-centric aggregated records. RCV records aggregate variant–condition
interpretations; SCV accessions identify submitted assertions. Neither a VCV nor
an rsID is a single clinical verdict. An rsID can link to multiple ClinVar records.
Do not substitute an rsID, Allele ID, RCV or VCV string for a numeric E-utilities UID.

## Resolve an rsID before retrieving summaries

Use the numeric dbSNP ID (strip the validated `rs` prefix) with ELink:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=snp&db=clinvar&id=334&retmode=json
```

Collect `linksets[].linksetdbs[]` with `dbto == "clinvar"`, preserving every returned
`links[]` UID. Then batch those numeric ClinVar IDs through ESummary:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=15175,15333&retmode=json
```

Do not call ClinVar ESummary with `id=rs334`, or search `rs334[AlleleID]`.
Do not assume a seemingly valid ESearch field constrained the query: inspect
`querytranslation`, warnings and result counts. A live check on 2026-09-14 found
`rs334[RS]` translated to `rs334[All Fields]`, whereas ELink explicitly linked dbSNP
to ten ClinVar UIDs. That count is an observation, not a permanent assertion.

## Other lookups

ESearch supports structured queries and returns numeric UIDs:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=clinvar&term=TP53%5BGene%5D&retmode=json&retmax=10
```

URL-encode query parameters and inspect translations. Paginate when completeness
is required; `retmax=10` is only a first-page example. Variation pages use numeric
Variation IDs: `https://www.ncbi.nlm.nih.gov/clinvar/variation/15175/`.
Use documented E-utilities/NCBI downloads rather than assuming a page URL has an
undocumented `/api/` JSON endpoint.

## Interpret responses

Inspect the actual schema; old flat `clinical_significance` examples are not a
stable contract. Keep germline classification, somatic clinical impact and
oncogenicity distinct. Report condition, review status, accession/version and
last evaluation date when supplied, including conflicts among submitters. Missing
classification is not benign evidence. Do not label `snp_class` as alleles or add
a chromosome prefix to an already formatted `chrpos` field.

## Limits and provenance

NCBI E-utilities permits 3 requests/sec without an API key and 10 with one; rate
limits apply across callers. Use existing authorized credentials only, never log
them, and respect service guidance. Preserve source IDs, mapping multiplicity,
retrieval date, genome build/coordinate convention when relevant, and all result
limits. No ClinVar link means no linked record was found, not a benign variant.

Official references:
- https://www.ncbi.nlm.nih.gov/clinvar/docs/identifiers/
- https://www.ncbi.nlm.nih.gov/books/NBK25499/ (E-utilities reference)
