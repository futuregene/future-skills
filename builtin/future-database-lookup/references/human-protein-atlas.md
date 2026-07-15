# Human Protein Atlas (HPA)

## Base URL
```
https://www.proteinatlas.org
```

## Auth
No API key required.

## Key Endpoints

| Purpose | URL Pattern |
|---|---|
| Gene data by Ensembl ID | `/{ENSEMBL_ID}.json` |
| Gene data by symbol | `/{GENE_NAME}.json` |
| Search (JSON) | `/search/{QUERY}?format=json` |
| Search (XML) | `/search/{QUERY}?format=xml` |

## Example Calls

```
# Gene data by Ensembl ID (✅ recommended — returns full JSON)
https://www.proteinatlas.org/ENSG00000141510.json

# Gene data by symbol (⚠️ may return HTML instead of JSON)
https://www.proteinatlas.org/TP53.json

# Search
https://www.proteinatlas.org/search/TP53?format=json
```

## Response Format (JSON, gene endpoint)
```json
{
  "Gene": "TP53",
  "Gene synonym": ["p53", "LFS1"],
  "Ensembl": "ENSG00000141510",
  "Gene description": "tumor protein p53",
  "Uniprot": ["P04637"],
  "Chromosome": "17",
  "Position": "7661779-7687538",
  "Protein class": ["Transcription factors", "Cancer-related genes", ...],
  "RNA tissue specificity": "Low tissue specificity",
  "Subcellular location": ["Nucleoplasm", "Vesicles", "Cytosol"],
  "Molecular function": ["Activator", "DNA-binding", "Repressor"],
  "Disease involvement": ["Cancer-related genes", "Disease variant", ...],
  "Pathology prognostics": [...]
}
```

⚠️ **Use the Ensembl ID-based endpoint** (`/ENSG00000141510.json`). The symbol-based endpoint (`/TP53.json`) may return HTML due to server content negotiation. Both return the same JSON structure when they work. The tissue-level expression data is NOT included in the JSON response — use the bulk TSV downloads for tissue data.

## Bulk Downloads
For large-scale work, use TSV files from https://www.proteinatlas.org/about/download:
- `normal_tissue.tsv` — IHC tissue expression
- `rna_tissue_consensus.tsv` — RNA consensus
- `subcellular_location.tsv`
- `pathology.tsv` — cancer prognostics

## Rate Limits
No published limits. Be reasonable. Prefer bulk downloads for large queries.
