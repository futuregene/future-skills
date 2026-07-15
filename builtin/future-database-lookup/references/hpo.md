# HPO (Human Phenotype Ontology) API Reference

## Base URL
```
https://ontology.jax.org/api
```

## Auth
No auth required. Fully public.

## Key Endpoints

### 1. Get Term by ID
```
GET /hp/terms/{hp_id}
```

Example:
```
https://ontology.jax.org/api/hp/terms/HP:0001250
```

Response (verified 2026-07):
```json
{
  "id": "HP:0001250",
  "name": "Seizure",
  "definition": "A seizure is an intermittent abnormality of nervous system physiology characterised by a transient occurrence of signs and/or symptoms due to abnormal excessive or synchronous neuronal activity in the brain.",
  "comment": "...",
  "descendantCount": 123,
  "synonyms": ["Epileptic seizure", "Convulsion", "..."],
  "xrefs": ["SNOMEDCT_US:91175000", "UMLS:C0036572"],
  "publicationReferences": [...],
  "translations": [...]
}
```

⚠️ Note: The field is `name` (not `label`).

### 2. Search Terms
```
GET /search?q={query}&limit={n}
```

Example:
```
https://ontology.jax.org/api/search?q=seizure&limit=5
```

Response:
```json
{
  "results": [
    {
      "id": "HP:0001250",
      "name": "Seizure",
      "ontology": "hp"
    }
  ],
  "total": 50
}
```

### 3. Term Ancestors
```
GET /hp/terms/{hp_id}/ancestors
```

### 4. Term Descendants
```
GET /hp/terms/{hp_id}/descendants
```

### 5. Disease-Phenotype Associations
```
GET /disease/{disease_id}/phenotypes
```

Query parameters:
- `disease_id` — OMIM, ORPHA, or DECIPHER ID

Example:
```
https://ontology.jax.org/api/disease/OMIM:154700/phenotypes
```

### 6. Network Search
```
GET /network/search/{hp_id}?ontology=hp
```

## Term ID Format
- HP terms: `HP:0001250` (no URL encoding needed in path)
- Disease IDs: `OMIM:154700`, `ORPHA:1234`, `DECIPHER:12`

## Rate Limits
No strict limits. Moderate usage expected.

## Notes
- The HPO is part of the Monarch Initiative ecosystem
- Cross-reference HPO terms with other ontologies via the `xrefs` field
- For phenotype-driven diagnostics, use the Exomiser or LIRICAL tools
- The `name` field (not `label`) contains the primary term name
