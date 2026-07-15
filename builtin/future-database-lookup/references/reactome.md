# Reactome Content Service REST API

## Base URL

```
https://reactome.org/ContentService
```

No authentication required. JSON by default.

## Key Endpoints

### Search (full-text across pathways, reactions, proteins)

```
GET /search/query?query={term}
```

Parameters:
- `query` (required) — search term (e.g. "apoptosis", "TP53", "R-HSA-109581")
- `species` — filter by species (e.g. "Homo sapiens")
- `types` — filter by type: `Pathway`, `Reaction`, `Protein`, `Complex`, `SmallMolecule`
- `cluster` — boolean, cluster results (default true)
- `rows` — page size
- `Start row` — offset for pagination

Example:
```
/search/query?query=apoptosis&species=Homo+sapiens&types=Pathway&rows=3
```

Response (verified 2026-07):
```json
{
  "results": [
    {
      "typeName": "Pathway",
      "entries": [
        {
          "dbId": 109581,
          "stId": "R-HSA-109581",
          "name": "<span class=\"highlighting\">Apoptosis</span>",
          "species": ["Homo sapiens"],
          "summation": "..."
        }
      ],
      "entriesCount": 288,
      "rowCount": 3
    }
  ],
  "rowCount": 25,
  "numberOfGroups": 9,
  "numberOfMatches": 1058
}
```

⚠️ Pay attention to pagination fields: top-level uses `rowCount` for returned results per page, `numberOfMatches` for total matches across all types. Use `Start row` parameter for pagination offset.

### Autocomplete
```
GET /search/suggest?query={partial_term}
```

### Top-level pathways for a species
```
GET /data/pathways/top/{species}
```
Example: `/data/pathways/top/Homo+sapiens`

### Pathway details
```
GET /data/query/{id}
```
Where `{id}` is a stable ID like `R-HSA-109581` or a numeric dbId.

### Events contained in a pathway
```
GET /data/pathway/{id}/containedEvents
```

### Participants of a reaction
```
GET /data/event/{id}/participants
```

### Ancestors of an event
```
GET /data/event/{id}/ancestors
```

### Map external ID to pathways (e.g. UniProt to Reactome pathways)
```
GET /data/mapping/{resource}/{id}/pathways
```
Example — find pathways for TP53 (UniProt P04637):
```
/data/mapping/UniProt/P04637/pathways
```

### Map external ID to reactions
```
GET /data/mapping/{resource}/{id}/reactions
```

### Generic entity lookup
```
GET /data/query/{id}
```

### Reference entities for an event
```
GET /data/participants/{id}/referenceEntities
```

### All species
```
GET /data/species/all
```

### Event hierarchy for a species (large response)
```
GET /data/eventsHierarchy/{species}
```

## Stable ID Format

`R-{species_code}-{number}`

| Code | Species |
|---|---|
| HSA | Homo sapiens |
| MMU | Mus musculus |
| RNO | Rattus norvegicus |
| DME | Drosophila melanogaster |
| CEL | C. elegans |
| SCE | S. cerevisiae |

## External Resource Names for Mapping

`UniProt`, `ChEBI`, `ENSEMBL`, `miRBase`, `GeneCards`, `NCBI`

Multiple values for same parameter: repeat the parameter (e.g. `types=Pathway&types=Reaction`).

## Response Notes

- Search responses may contain HTML `<span class="highlighting">` tags in `name` and `summation` fields — strip these before display.
- Use `entries` array (not `rows`) to access search result items.

## Rate Limits

No API key required. No formal rate limit published, but be reasonable — avoid hundreds of concurrent requests. For bulk data, use Reactome's downloadable dumps (MySQL, Neo4j, BioPAX, SBML).
