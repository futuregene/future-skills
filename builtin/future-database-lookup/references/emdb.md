# EMDB (Electron Microscopy Data Bank)

## Base URL
```
https://www.ebi.ac.uk/emdb/api/
```

## Auth
No auth required.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/entry/{emdb_id}` | Full entry metadata (e.g. EMD-1234) |
| `/entry/map/{emdb_id}` | Map/volume metadata |
| `/entry/experiment/{emdb_id}` | Experimental details |
| `/entry/fitted/{emdb_id}` | Fitted PDB models |
| `/search/{query}?rows={n}` | Search entries by keyword |

## Example Calls
```
# Entry metadata
https://www.ebi.ac.uk/emdb/api/entry/EMD-1234

# Search for ribosome entries
https://www.ebi.ac.uk/emdb/api/search/ribosome?rows=5

# Experimental details
https://www.ebi.ac.uk/emdb/api/entry/experiment/EMD-1234
```

## Response Format
JSON. Search includes pagination and matching entry array.

### Entry Response Structure (actual)
```json
{
  "_id": "5f3a8cfa043d5cc5a75c8742",
  "admin": {
    "title": "West Nile virus in complex with the Fab fragment...",
    "deposition_date": "2020-08-17",
    "last_update": "2024-01-15"
  },
  "emdb_id": "EMD-1234",
  "sample": {
    "name": "Sample description..."
  },
  "structure_determination_list": {
    "resolution": 3.5,
    "method": "SINGLE PARTICLE"
  },
  "map": { ... },
  "crossreferences": { ... },
  "version": { ... }
}
```
Key fields are nested: title → `admin.title`, resolution → `structure_determination_list.resolution`, method → `structure_determination_list.method`.

## Rate Limits
EBI fair-use policy. Map files (MRC/CCP4) available via FTP for bulk access.
