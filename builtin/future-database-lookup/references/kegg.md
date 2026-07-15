# KEGG REST API

## Base URL
```
https://rest.kegg.jp
```

## Auth
No API key required. Free for academic use. Commercial use requires license.

## Important: KEGG returns tab-delimited text and flat-file format, NOT JSON.

## Key Operations (URL-path-based, no query parameters)

| URL Pattern | Description |
|-------------|-------------|
| `/list/{database}` | List all entries |
| `/list/{database}/{organism}` | List entries for organism |
| `/get/{dbentries}` | Get entry data (flat-file) |
| `/get/{dbentries}/image` | Pathway image (PNG) |
| `/get/{dbentries}/kgml` | Pathway as KGML XML |
| `/find/{database}/{query}` | Search by keyword |
| `/find/{database}/{query}/formula` | Search by molecular formula |
| `/find/{database}/{value}/exact_mass` | Search by exact mass |
| `/link/{target_db}/{dbentries}` | Find linked entries from source to target database |
| `/link/{target_db}/{source_db}` | List all links between two databases |
| `/conv/{target_db}/{dbentries}` | Cross-reference ID conversion |
| `/ddi/{dbentries}` | Drug-drug interactions |

## Database Codes

| Code | Database | Example ID |
|------|----------|------------|
| `pathway` | Pathways | `path:map00010` |
| `compound` | Compounds | `cpd:C00001` |
| `drug` | Drugs | `dr:D00001` |
| `enzyme` | Enzymes | `ec:1.1.1.1` |
| `genes`/`hsa` | Genes | `hsa:10458` |
| `disease` | Diseases | `H00001` |
| `reaction` | Reactions | `R00001` |
| `ko` | KO orthologs | `K00001` |

## Important ID Format Rules

### Link endpoint requires database prefix

When using `/link/{target_db}/{dbentries}`, the `{dbentries}` MUST include the database prefix:

| Correct | Wrong |
|---------|-------|
| `/link/pathway/cpd:C01405` | `/link/pathway/C01405` |
| `/link/pathway/hsa:672` | `/link/pathway/672` |
| `/link/pathway/dr:D00109` | `/link/pathway/D00109` |

### ID conversion returns Substance IDs not Compound IDs

⚠️ **IMPORTANT**: `/conv/pubchem/{kegg_id}` returns PubChem **Substance** IDs (SID), not Compound IDs (CID). To get the CID, resolve the SID through PubChem:
```
# KEGG conv returns SID
GET /conv/pubchem/C01405
# Returns: cpd:C01405  pubchem:4594

# Resolve SID→CID through PubChem
GET https://pubchem.ncbi.nlm.nih.gov/rest/pug/substance/sid/4594/cids/JSON
```

## Example Calls

```
# List human pathways
https://rest.kegg.jp/list/pathway/hsa

# Get pathway entry
https://rest.kegg.jp/get/hsa00010

# Search compounds by name
https://rest.kegg.jp/find/compound/aspirin

# Search by molecular formula
https://rest.kegg.jp/find/compound/C9H8O4/formula

# Find pathways for a gene
https://rest.kegg.jp/link/pathway/hsa:10458

# Find diseases for a gene
https://rest.kegg.jp/link/disease/hsa:672

# Convert KEGG to PubChem IDs (returns SID!)
https://rest.kegg.jp/conv/pubchem/C00001

# Get multiple entries (max 10, joined with +)
https://rest.kegg.jp/get/C00001+C00002+C00003

# Drug-drug interactions
https://rest.kegg.jp/ddi/D00564+D00110

# Get compound with full detail
https://rest.kegg.jp/get/C01405
```

## Response Format
Tab-delimited text for list/find/link/conv. Flat-file text for get. **No JSON support.**

### List/Find response format (TSV):
```
entry_id\tdescription
cpd:C01405\tAspirin; Acetylsalicylic acid; 2-Acetoxybenzenecarboxylic acid
```

### Get response format (flat-file):
```
ENTRY       C01405                      Compound
NAME        Aspirin;
            Acetylsalicylic acid;
FORMULA     C9H8O4
EXACT_MASS  180.0423
MOL_WEIGHT  180.16
```

## Rate Limits
No published limits. Keep to a few requests per second. Batch up to 10 IDs per `/get` with `+`. May return HTTP 403 if too many requests.

## Error Handling
- Returns empty response body (no error message) for invalid IDs
- HTTP 404 for malformed URLs
- Returns 200 with empty body when no results found for find/link
