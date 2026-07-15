# BindingDB REST API

## Base URLs
```
https://bindingdb.org/rest/
https://bindingdb.org/axis2/services/BDBService/
```

## Auth
No API key required. Fully open and free.

## Response Format
Default is XML. Append `&response=application/json` to any endpoint for JSON.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/rest/getLigandsByUniprot` | Ligands for a single protein target |
| `/rest/getLigandsByUniprots` | Ligands for multiple protein targets |
| `/rest/getLigandsByPDBs` | Ligands by PDB structure IDs |
| `/rest/getTargetByCompound` | Targets for a compound (SMILES similarity) |

## Endpoint Details

### 1. Get ligands for a single target
```
GET https://bindingdb.org/rest/getLigandsByUniprot?uniprot={UNIPROT_ID};{IC50_cutoff_nM}&response=application/json
```
- `uniprot` — UniProt ID followed by `;` and affinity cutoff in nM (semicon separated in same param)
- Returns JSON wrapped in `getLindsByUniprotResponse`
- Each affinity item has keys: `bdb.monomerid`, `bdb.smile`, `bdb.affinity_type` (IC50/Ki/Kd), `bdb.affinity` (value in nM), `bdb.target_name`, `bdb.primary`
- Returns empty string if UniProt ID not found
- Top-level fields: `bdb.hit` (count), `bdb.length`, `bdb.uniprot_length`, `bdb.primary`, `bdb.alternative`

Example — verified working (2026-07):
```bash
curl -s "https://bindingdb.org/rest/getLigandsByUniprot?uniprot=P35355;10&response=application/json"
# Returns 8 ligands with IC50 values from <1nM to 9nM
```

### 2. Get ligands for multiple targets
```
GET https://bindingdb.org/rest/getLigandsByUniprots?uniprot={IDs}&cutoff={nM}&response=application/json
```
- `uniprot` — Comma-separated UniProt IDs (separate param, NO semicolon!)
- `cutoff` — Affinity cutoff in nM (separate parameter)
- Returns `getLindsByUniprotsResponse.affinities[]` with different field names than single-target:
  - `query` — target name (e.g. "Prostaglandin G/H synthase 1")
  - `monomerid` — compound monomer ID
  - `smile` — SMILES string (note: `smile` not `bdb.smile`)
  - `affinity_type` — IC50/Ki/Kd
  - `affinity` — value in nM
  - `pmid` — PubMed ID
  - `doi` — DOI
- ⚠️ Field names differ from single-target endpoint!
- Returns empty array for `affinities` if no matching IDs

Example:
```
https://bindingdb.org/rest/getLigandsByUniprots?uniprot=P35355,P23219&cutoff=1000&response=application/json
```

### 3. Get ligands by PDB structure
```
GET https://bindingdb.org/rest/getLigandsByPDBs?pdb={PDBs}&cutoff={nM}&identity={percent}&response=application/json
```
- `pdb` — Comma-separated PDB IDs
- `cutoff` — Affinity cutoff in nM
- `identity` — Sequence identity cutoff (percent, e.g. 92)

Example:
```
https://bindingdb.org/rest/getLigandsByPDBs?pdb=1Q0L,3ANM&cutoff=100&identity=92&response=application/json
```

### 4. Find targets for a compound (similarity search)
```
GET https://bindingdb.org/rest/getTargetByCompound?smiles={SMILES}&cutoff={similarity}&response=application/json
```
- `smiles` — Compound SMILES (must be URL-encoded)
- `cutoff` — Tanimoto similarity cutoff (decimal, e.g. 0.85)
- Returns similar compounds with their protein targets and affinities
- Response wrapped in `getLindsByUniprotResponse` structure (confusing naming — this is the actual response wrapper):
  - `bdb.smile` — query SMILES
  - `bdb.hit` — number of results
  - `bdb.affinities[]` — each with: `bdb.monomerid`, `bdb.smiles` (note 's'), `bdb.inhibitor`, `bdb.target`, `bdb.species`, `bdb.affinity_type`, `bdb.affinity`

Example:
```
https://bindingdb.org/rest/getTargetByCompound?smiles=CC%28%3DO%29OC1%3DCC%3DCC%3DC1C%28%3DO%29O&cutoff=0.85&response=application/json
```

## Rate Limits
No documented limit. Keep requests to ~1 per second as a courtesy.
- ⚠️ **Known issue (2026)**: The `/rest/getLigandsByUniprot` endpoint sometimes returns **HTTP 504 Gateway Timeout** for common targets. If you get a 504, try narrowing the affinity cutoff (e.g., `;100` instead of `;1000`), using `/rest/getLigandsByPDBs`, or falling back to **ChEMBL**.

## Field Name Variations Between Endpoints

⚠️ Different endpoints use slightly different field names:

| Field | Single target | Multi target | TargetByCompound |
|-------|--------------|--------------|------------------|
| SMILES | `bdb.smile` | `smile` | `bdb.smiles` |
| Monomer ID | `bdb.monomerid` | `monomerid` | `bdb.monomerid` |
| Target name | `bdb.target_name` | `query` | `bdb.target` |
| PubMed | — | `pmid` | — |
| DOI | — | `doi` | — |

## Error Handling
- Returns empty string (not JSON) for invalid/bad UniProt IDs
- Returns HTTP 504 for timeouts
- Returns empty affinities array when no results match

## Notes
- The API surface is small (4 endpoints) but focused on binding affinity data
- For compound-name search, resolve to SMILES first via PubChem, then use `getTargetByCompound`
- For bulk data access, use downloadable TSV/SDF files from https://www.bindingdb.org/bind/chemsearch/marvin/Download.jsp
- Contains ~3.2M binding measurements for ~1.4M compounds and ~11.4K targets
