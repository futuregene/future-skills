# HPO (Human Phenotype Ontology)

## Base URL
```
https://hpo.jax.org/api/hpo
```

## Auth
No API key required.

## Important: URL-encode colons in HP IDs — `HP:0001250` becomes `HP%3A0001250`

## ⚠️ API Status (2026)
The HPO API is undergoing migration. As of 2026-07:
- The legacy endpoint `https://ontology.jax.org/api/hp` returns "Not Found" for most queries.
- The current endpoint `https://hpo.jax.org/api/hpo` returns an Angular SPA (HTML), not JSON API responses.
- For reliable programmatic access, use one of these alternatives:
  1. **Monarch Initiative** (`/entity/HP%3A0001250`) for term details and gene/disease associations
  2. **HPO API via BioPortal** (`https://data.bioontology.org/ontologies/HP`)
  3. Download the OWL/JSON files from `https://hpo.jax.org/data/`

## Key Endpoints (legacy — may or may not work)

| Endpoint | Description |
|----------|-------------|
| `/hpo/term/{id}` | Term details |
| `/hpo/term/{id}/genes` | Genes associated with a phenotype |
| `/hpo/term/{id}/diseases` | Diseases associated with a phenotype |
| `/hpo/gene/{gene_id}` | Phenotypes for a gene (Entrez ID) |

## Recommended alternative: Monarch Initiative for HPO data

```
# Term details for Seizure
GET https://api.monarchinitiative.org/v3/api/entity/HP%3A0001250

# Genes for seizure phenotype
GET https://api.monarchinitiative.org/v3/api/entity/HP%3A0001250/associations?category=biolink:GeneToPhenotypicFeatureAssociation&limit=20
```

## Response Format (legacy)
JSON. Terms: `id`, `name`, `definition`, `synonyms`. Gene associations: `genes[]` with `geneId`, `geneSymbol`. Diseases: `diseases[]` with `diseaseId`, `diseaseName`.

## Rate Limits
No published limits. Bulk annotation files at https://hpo.jax.org/data/annotations
