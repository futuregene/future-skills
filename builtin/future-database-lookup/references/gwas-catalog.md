# GWAS Catalog (EBI)

## Base URL
```
https://www.ebi.ac.uk/gwas/rest/api
```

## Auth
No API key required.

## Note: Responses use HAL+JSON format with `_links` and `_embedded` keys.

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/studies/{accession}` | Single study (e.g. GCST001633) |
| `/studies/search/findByPubmedId?pubmedId={id}` | Studies by PubMed ID |
| `/singleNucleotidePolymorphisms/{rsId}` | SNP details |
| `/singleNucleotidePolymorphisms/{rsId}/associations` | Associations for a SNP |
| `/singleNucleotidePolymorphisms/search/findByRsId?rsId={rsId}` | Search by rsID |
| `/associations` | List associations |
| `/associations/{id}` | Single association |
| `/efoTraits` | List EFO traits |
| `/efoTraits/search/findByEfoTrait?trait={name}` | Search traits |

## Pagination
`?page=0&size=20` (zero-indexed, max ~500)

## Example Calls
```
# Get a study
https://www.ebi.ac.uk/gwas/rest/api/studies/GCST001633

# Associations for a SNP
https://www.ebi.ac.uk/gwas/rest/api/singleNucleotidePolymorphisms/rs7329174/associations

# Search traits
https://www.ebi.ac.uk/gwas/rest/api/efoTraits/search/findByEfoTrait?trait=diabetes&page=0&size=5
```

## Response Format
HAL+JSON. Results in `_embedded.studies[]` or `_embedded.associations[]`. 
Key fields (association): `pvalue`, `pvalueDescription`, `orPerCopyNum`, `betaNum`, `riskFrequency`, `riskAllele`.
The `efoTrait` and `diseaseTrait` fields are NOT embedded in the association response — you must follow the HAL `_links`:
- `_links.efoTraits.href` → GET this URL to get the EFO trait name(s)
- `_links.study.href` → GET this URL to get the study info and `diseaseTrait.trait`
- `_links.snps.href` → GET this URL to get rsID, chromosome, position

Example workflow:
```
# Step 1: Get associations for a SNP
GET /singleNucleotidePolymorphisms/rs9272346/associations
# Returns association IDs and _links

# Step 2: Follow efoTraits link
GET /associations/11931/efoTraits
# → {"_embedded":{"efoTraits":[{"trait":"type 1 diabetes mellitus","uri":"MONDO:0005147"}]}}

# Step 3: Follow study link
GET /associations/11931/study
# → {"diseaseTrait":{"trait":"Type 1 diabetes"},"pubmedId":"...","title":"..."}
```

## Rate Limits
No published limit. Bulk data via FTP at ftp.ebi.ac.uk/pub/databases/gwas/
