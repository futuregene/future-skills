# GWAS Catalog REST API

## Base URL
```
https://www.ebi.ac.uk/gwas/rest/api
```

## Auth
No API key required. Fully public.

## Key Endpoints

### Search studies by disease/trait
```
GET /studies/search/findByDiseaseTrait?trait={trait_name}&size={n}
```

Parameters:
- `trait` — Disease or trait name (e.g. `breast carcinoma`)
- `size` — Results per page (default 20)
- `page` — Page number (0-indexed)

Example:
```
https://www.ebi.ac.uk/gwas/rest/api/studies/search/findByDiseaseTrait?trait=breast%20carcinoma&size=5
```

### Search by PubMed ID
```
GET /studies/search/findByPubMedId?pubmedId={pmid}
```

### Search by accession
```
GET /studies/search/findByAccession?accessionId={gcs_id}
```

Example:
```
https://www.ebi.ac.uk/gwas/rest/api/studies/search/findByAccession?accessionId=GCST000854
```

### Get single study
```
GET /studies/{study_accession}
```

### Get study associations
```
GET /studies/{study_accession}/associations?size={n}
```

### Browse all studies (paginated)
```
GET /studies?size={n}&page={p}
```

### Search associations
```
GET /associations/search/findByDiseaseTrait?trait={trait_name}&size={n}
```

### Search by variant rsID
```
GET /associations/search/findByRiskAllele?riskAllele={rsid}&size={n}
```

### Search EFOTraits
```
GET /efoTraits/search/findByTrait?trait={trait_name}&size={n}
```

## Response Format
All responses are HAL+JSON. Key response elements:

```json
{
  "_embedded": {
    "studies": [
      {
        "accessionId": "GCST000854",
        "diseaseTrait": {
          "trait": "Suicide risk"
        },
        "publicationInfo": {
          "pubmedId": "21234567",
          "title": "...",
          "author": "..."
        },
        "initialSampleSize": "...",
        "replicationSampleSize": "...",
        "_links": {
          "associations": { "href": "..." }
        }
      }
    ]
  },
  "page": {
    "size": 20,
    "totalElements": 5000,
    "totalPages": 250,
    "number": 0
  }
}
```

## Pagination
Uses Spring Data REST pagination:
- `size` — results per page
- `page` — page number (0-indexed)
- Response includes `page.totalElements` and `page.totalPages`

## Rate Limits
No strict limits published. Be reasonable — ~1-2 req/sec.

## Notes
- Trait names must match EFO ontology terms where possible
- Use URL encoding for special characters in trait names
- The `_links` in each study provide direct URLs to related resources
- For bulk data, use the GWAS Catalog FTP downloads
