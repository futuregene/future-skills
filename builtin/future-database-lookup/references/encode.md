# ENCODE (Encyclopedia of DNA Elements)

## Base URL
```
https://www.encodeproject.org
```

## Auth
No auth required. Append `?format=json` or set `Accept: application/json`.

## Every portal URL returns JSON when requested with the right header.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/search/?type=Experiment&format=json` | Search experiments |
| `/experiments/{accession}/?format=json` | Specific experiment |
| `/files/{accession}/?format=json` | File metadata |
| `/biosamples/{accession}/?format=json` | Biosample info |
| `/annotations/?format=json` | Search annotations |

## Search Parameters
- `type` — Experiment, File, Biosample, Annotation, etc.
- `assay_term_name` — ChIP-seq, RNA-seq, ATAC-seq, etc. (⚠️ Use `assay_term_name`, NOT `assay_title`. As of 2026, `assay_title` returns 0 results while `assay_term_name` works.)

Example:
```
# CORRECT (returns results):
https://www.encodeproject.org/search/?type=Experiment&assay_term_name=ChIP-seq&format=json&limit=5

# INCORRECT (returns 0):
https://www.encodeproject.org/search/?type=Experiment&assay_title=ChIP-seq&format=json&limit=5
```

- `target.label` — target protein (e.g. CTCF, H3K27ac), may be empty for some experiments
- `biosample_ontology.term_name` — cell type
- `limit` — results per page
- `field` — specific fields to return

## Example Calls
```
# ChIP-seq experiments for CTCF
https://www.encodeproject.org/search/?type=Experiment&assay_term_name=ChIP-seq&target.label=CTCF&format=json&limit=5

# RNA-seq experiments
https://www.encodeproject.org/search/?type=Experiment&assay_term_name=RNA-seq&format=json&limit=5

# ChIP-seq experiments for a gene (use target.label, NOT gene symbol directly)
https://www.encodeproject.org/search/?type=Experiment&assay_term_name=ChIP-seq&target.label=TP53&format=json&limit=5

# Specific experiment
https://www.encodeproject.org/experiments/ENCSR000AAA/?format=json

# Files for an experiment
https://www.encodeproject.org/search/?type=File&dataset=/experiments/ENCSR000AAA/&format=json
```

## Response Format
JSON-LD. Search: `@graph` array + `total` + `facets`. Use `frame=object` or `frame=embedded` to control depth.

## Rate Limits
No published limits. Use `limit=` and `field=` to reduce payload.
