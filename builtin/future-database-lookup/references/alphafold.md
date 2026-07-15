# AlphaFold DB (Predicted Protein Structures)

## Base URL
```
https://alphafold.ebi.ac.uk/api/
```

## Auth
No auth required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/prediction/{uniprot_accession}` | Prediction metadata by UniProt ID |

## Structure File URLs (direct download)

⚠️ **IMPORTANT**: The version number in file URLs changes. Always get the `latestVersion` from the API response first, or use the direct URLs provided in the API response (`pdbUrl`, `cifUrl`, `bcifUrl`, `paeDocUrl`, `plddtDocUrl`).

Pattern (use `{VERSION}` from `latestVersion` field):
```
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v{VERSION}.pdb
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v{VERSION}.cif
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-model_v{VERSION}.bcif
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-predicted_aligned_error_v{VERSION}.json
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-confidence_v{VERSION}.json
https://alphafold.ebi.ac.uk/files/AF-{UNIPROT}-F1-predicted_aligned_error_v{VERSION}.png
```

## Example Calls
```
# Get prediction metadata for EGFR
https://alphafold.ebi.ac.uk/api/prediction/P00533

# Download PDB structure (use version from API response)
# For P00533: latestVersion=6, so:
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v6.pdb

# Download PAE (predicted aligned error)
https://alphafold.ebi.ac.uk/files/AF-P00533-F1-predicted_aligned_error_v6.json

# Best practice: extract URLs from API response
curl -s https://alphafold.ebi.ac.uk/api/prediction/P00533 | python3 -c "import json,sys;d=json.load(sys.stdin)[0];print(d['pdbUrl'])"
```

## Response Format (API Metadata)

JSON array with one entry per prediction. Key fields:

| Field | Description |
|-------|-------------|
| `uniprotAccession` | UniProt accession (e.g. P00533) |
| `gene` | Gene symbol |
| `organismScientificName` | Organism name |
| `modelEntityId` | AlphaFold model ID (e.g. AF-P00533-F1) |
| `latestVersion` | Current model version number (use for file URLs) |
| `allVersions` | Array of all available versions |
| `globalMetricValue` | Mean pLDDT (confidence score, 0-100) |
| `fractionPlddtVeryHigh` | Fraction of residues with pLDDT > 90 |
| `fractionPlddtConfident` | Fraction with pLDDT 70-90 |
| `fractionPlddtLow` | Fraction with pLDDT 50-70 |
| `fractionPlddtVeryLow` | Fraction with pLDDT < 50 |
| `pdbUrl` | Direct URL to PDB structure file |
| `cifUrl` | Direct URL to mmCIF structure file |
| `bcifUrl` | Direct URL to BinaryCIF file |
| `paeImageUrl` | Direct URL to PAE plot image (PNG) |
| `paeDocUrl` | Direct URL to PAE JSON data |
| `plddtDocUrl` | Direct URL to per-residue pLDDT JSON |
| `sequence` | Full amino acid sequence |
| `sequenceChecksum` | MD5 checksum of sequence |
| `isUniProtReviewed` | Whether the UniProt entry is Swiss-Prot reviewed |
| `uniprotId` | UniProt entry name (e.g. EGFR_HUMAN) |

### Example Response (condensed)
```json
[{
  "uniprotAccession": "P00533",
  "gene": "EGFR",
  "organismScientificName": "Homo sapiens",
  "modelEntityId": "AF-P00533-F1",
  "latestVersion": 6,
  "globalMetricValue": 75.94,
  "fractionPlddtVeryHigh": 0.474,
  "fractionPlddtConfident": 0.233,
  "fractionPlddtLow": 0.065,
  "fractionPlddtVeryLow": 0.228,
  "pdbUrl": "https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v6.pdb",
  "cifUrl": "https://alphafold.ebi.ac.uk/files/AF-P00533-F1-model_v6.cif",
  "paeDocUrl": "https://alphafold.ebi.ac.uk/files/AF-P00533-F1-predicted_aligned_error_v6.json",
  "plddtDocUrl": "https://alphafold.ebi.ac.uk/files/AF-P00533-F1-confidence_v6.json",
  "sequence": "MRPSGTAGAALLALLAALCPASRALEEKKV...",
  "isUniProtReviewed": true
}]
```

## Error Handling
- Returns `{"error": "Invalid identifier format. ..."}` for bad UniProt accessions (HTTP 200).
- Returns empty array `[]` if the UniProt accession has no AlphaFold prediction.

## Rate Limits
No strict limits. Use FTP/Cloud for bulk downloads (~200M+ structures).
