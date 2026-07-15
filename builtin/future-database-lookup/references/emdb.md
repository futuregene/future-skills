# EMDB (Electron Microscopy Data Bank) API Reference

## Base URL
```
https://www.ebi.ac.uk/emdb/api/entry/
```

## Auth
No auth required. Fully public.

## Key Endpoints

### Entry Lookup
```
GET https://www.ebi.ac.uk/emdb/api/entry/{emdb_id}
```
Example:
```
https://www.ebi.ac.uk/emdb/api/entry/EMD-2984
```

## Response Structure

The API returns a nested JSON document. Key fields (verified 2026-07):

### Top-level fields:
| Field | Type | Description |
|-------|------|-------------|
| `emdb_id` | string | EMDB accession (e.g. "EMD-2984") |
| `admin.title` | string | Entry title |
| `admin.authors_list.author[]` | array | Authors, each with `valueOf_` (name) and `instance_type` |
| `admin.keywords` | object | Keywords |
| `admin.current_status` | string | Processing status |
| `structure_determination_list` | object | Contains `structure_determination` (array or object) |
| `sample` | object | Sample/macromolecule details |
| `map` | object | Map metadata (cell, axis, symmetry) |
| `crossreferences` | object | Cross-references to other databases |
| `interpretation` | object | Interpretation/fitting results |
| `validation` | object | Validation metrics |

### Resolution and method access:
Resolution is nested deep — access via:
```
structure_determination_list.structure_determination[0].image_processing[0].final_reconstruction.resolution
```
Where `resolution` is an object:
```json
{
  "res_type": "BY AUTHOR",
  "units": "Å",
  "valueOf_": "2.2"
}
```

Method is in:
```
structure_determination_list.structure_determination[0].method
```
Values: `singleParticle`, `tomography`, `electron_crystallography`, etc.

### Sample details:
```
sample.macromolecule_list.macromolecule[] — array of macromolecules
sample.macromolecule_list.macromolecule[0].name.synonym[] — protein names
sample.macromolecule_list.macromolecule[0].molecular_weight.theoretical — MW info
```

### Quick field access (Python example):
```python
import json

data = json.loads(response)
entry_id = data['emdb_id']
title = data['admin']['title']
authors = [a['valueOf_'] for a in data['admin']['authors_list']['author']]

# Resolution
sd = data['structure_determination_list']['structure_determination']
if isinstance(sd, list):
    sd = sd[0]
for ip in sd.get('image_processing', []):
    fr = ip.get('final_reconstruction', {})
    if fr:
        resolution = fr['resolution']['valueOf_']
        units = fr['resolution']['units']
```

## File Downloads
```
https://ftp.ebi.ac.uk/pub/databases/emdb/structures/EMD-{id}/map/emd_{id}.map.gz
https://ftp.ebi.ac.uk/pub/databases/emdb/structures/EMD-{id}/header/emd-{id}-v30.xml
```

## Search
EMDB doesn't have a dedicated REST search API. Use:
- PDBe search API (which indexes EMDB): `https://www.ebi.ac.uk/pdbe/search/pdb/select?q=...`
- EMDB website for interactive search

## Rate Limits
No published limits. Moderate usage expected.

## Notes
- All numeric/string values in the API may use `valueOf_` wrapper — check before accessing
- `structure_determination_list.structure_determination` may be a single object or array — handle both cases
- Resolution may not always be present (e.g., for tomograms)
- Cross-reference with PDB via `crossreferences`
