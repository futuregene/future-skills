# QuickGO (Gene Ontology Annotations) API Reference

## Base URL
```
https://www.ebi.ac.uk/QuickGO/services/
```

## Authentication
None required. All endpoints public.

## Rate Limits
No strict limits. Be courteous.

## Key Endpoints

### 1. Search Annotations (JSON)
```
GET /services/annotation/search?geneProductId={id}&limit={n}
```

Parameters:
- `geneProductId` — UniProt accession with prefix: `UniProtKB:P04637`
- `goId` — filter by GO term ID (e.g. `GO:0006915`)
- `aspect` — `biological_process`, `molecular_function`, `cellular_component`
- `taxonId` — NCBI taxon ID (e.g. `9606`)
- `evidenceCode` — ECO evidence code (e.g. `ECO:0000250`)
- `limit` — results per page (max 100)
- `page` — page number (1-indexed)

**Example — get GO annotations for TP53:**
```
GET https://www.ebi.ac.uk/QuickGO/services/annotation/search?geneProductId=UniProtKB:P04637&limit=5
```

**Response (JSON):**
```json
{
  "numberOfHits": 1032,
  "results": [
    {
      "goId": "GO:0008285",
      "goName": "negative regulation of cell population proliferation",
      "goAspect": "biological_process",
      "geneProductId": "UniProtKB:P04637",
      "symbol": "TP53",
      "qualifier": "acts_upstream_of",
      "evidenceCode": "ECO:0000250",
      "goEvidence": "ISS",
      "reference": "PMID:30514107",
      "withFrom": "UniProtKB:P10361",
      "taxonId": 9606,
      "assignedBy": "ARUK-UCL",
      "date": "20210810"
    }
  ]
}
```

### 2. Download Annotations (TSV/GAF/GPAD format)
```
GET /services/annotation/downloadSearch?geneProductId={id}&limit={n}
```

⚠️ **REQUIRES `Accept` header** — must include one of:
- `text/tsv` for tab-separated
- `text/gpad` for GPAD format
- `text/gaf` for GAF format

**Example:**
```bash
curl -s -H "Accept: text/tsv" \
  "https://www.ebi.ac.uk/QuickGO/services/annotation/downloadSearch?geneProductId=UniProtKB:P04637&limit=5"
```

### 3. GO Term Lookup
```
GET /services/ontology/go/terms/{go_id}
```

**Example — get info for GO:0006915 (apoptosis):**
```
GET https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO%3A0006915
```
Note: URL-encode `:` as `%3A`.

**Response:**
```json
{
  "results": [
    {
      "id": "GO:0006915",
      "name": "apoptotic process",
      "definition": {
        "text": "A programmed cell death process which begins when a cell receives an internal..."
      },
      "aspect": "biological_process",
      "isObsolete": false
    }
  ]
}
```

### 4. GO Term Ancestors
```
GET /services/ontology/go/terms/{go_id}/ancestors
```

### 5. GO Term Descendants
```
GET /services/ontology/go/terms/{go_id}/descendants
```

## Gene Product ID Format
Use the `UniProtKB:` prefix for UniProt accessions:
- Correct: `UniProtKB:P04637`
- Incorrect: `P04637`, `UniProt:P04637`

Other accepted prefixes: `ENSEMBL:`, `RefSeq:`, `MGI:`, `RGD:`, `SGD:`, `dictyBase:`

## Pagination
- The `search` endpoint returns `numberOfHits` for total count
- Use `page` parameter (1-indexed) with `limit` for pagination
- The `downloadSearch` endpoint streams all results (respects `limit` but may not paginate the same way)

## Notes
- For programmatic JSON access, prefer the `/annotation/search` endpoint
- For bulk data, use `/annotation/downloadSearch` with appropriate Accept header
- GO term IDs must be URL-encoded (`GO%3A0006915`)
- QuickGO annotations come from multiple sources including UniProt-GOA, Reactome, etc.
- Check `assignedBy` field to see the source of each annotation
