# ClinVar API Reference

## Base URLs
- **E-utilities**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **ClinVar VCV pages**: `https://www.ncbi.nlm.nih.gov/clinvar/variation/{vcv_id}/`

## Authentication
- **E-utilities**: API key recommended (`&api_key=KEY`). 3 req/sec without, 10 req/sec with key.
- **ClinVar VCV API**: No auth required.

## Important: ClinVar IDs vs dbSNP rsIDs

⚠️ **ClinVar uses its own accession system (VCV)**, NOT dbSNP rsIDs for primary lookups. An rsID maps to a genomic location, while a VCV accession represents a specific variant-interpretation pair.

To look up ClinVar data for a known rsID:
1. First get the VCV accession via eSearch with the allele ID or by searching
2. Then use eSummary with the VCV accession

## Key Endpoints

### 1. eSearch — Find ClinVar records
```
GET esearch.fcgi?db=clinvar&term={query}&retmode=json
```

**Examples:**
```
# Search by gene symbol
esearch.fcgi?db=clinvar&term=TP53%5BGene%5D&retmode=json&retmax=10

# Search by clinical significance
esearch.fcgi?db=clinvar&term=pathogenic%5Bclinsig%5D&retmode=json&retmax=5

# Search by condition
esearch.fcgi?db=clinvar&term=%22Li-Fraumeni+syndrome%22%5Bdis%5D&retmode=json&retmax=5
```

### 2. eSummary — Get record summaries
```
GET esummary.fcgi?db=clinvar&id={clinvar_ids}&retmode=json
```

Where `{clinvar_ids}` are ClinVar variation IDs (VCV accessions), NOT rsIDs.

Response fields include:
- `title` — Variant description (HGVS + gene info)
- `clinical_significance` — Clinical significance assertion
- `review_status` — Review status (e.g. "criteria provided, multiple submitters, no conflicts")
- `last_evaluated` — Last evaluation date
- `accession` — VCV accession
- `allele_id` — Allele ID
- `gene_sort` — Gene symbol

### 3. ClinVar Variation API (VCF-compatible)
```
GET https://www.ncbi.nlm.nih.gov/clinvar/variation/{vcv_id}/api/
```

Returns structured JSON with full variant details including:
- Variant coordinates, HGVS expressions
- Clinical assertions with review status
- Molecular consequence
- Conditions/diseases
- Submitter information

### 4. Convert rsID → Allele ID
```
GET esearch.fcgi?db=clinvar&term={rsid}%5BAlleleID%5D&retmode=json
```

Note: Not all rsIDs have ClinVar entries. Only rsIDs with clinical assertions are in ClinVar.

## Common E-utilities Search Terms

```
# By gene
TP53[Gene]

# By clinical significance
pathogenic[clinsig]
likely pathogenic[clinsig]
uncertain significance[clinsig]

# By review status
criteria provided[review]
reviewed by expert panel[review]
practice guideline[review]

# By molecular consequence  
missense[molc]
frameshift[molc]
nonsense[molc]

# By disease/condition
"Li-Fraumeni syndrome"[dis]
"Breast-ovarian cancer"[dis]

# Combined
TP53[Gene] AND pathogenic[clinsig] AND missense[molc]
```

## Rate Limits
- E-utilities: 3 req/sec (no key), 10 req/sec (with key)
- ClinVar API: No published limits, be respectful

## Notes
- ClinVar records are accessioned as VCV###### (e.g. VCV000000001)
- Clinical significance may have multiple values for a single variant (different submitters)
- Always check `review_status` — "no assertion criteria provided" is less reliable than "reviewed by expert panel"
- For population frequency data, prefer gnomAD (ClinVar only has clinical assertions)
- The ClinVar Variation API provides more structured data than E-utilities summaries
