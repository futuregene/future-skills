# GTEx (Genotype-Tissue Expression) API Reference

## Overview
GTEx catalogs gene expression levels across human tissues from postmortem donors,
enabling study of tissue-specific gene regulation and eQTLs.

## Base URL
`https://gtexportal.org/api/v2`

## Auth
None required (public, unauthenticated).

## Response Format
JSON. Most endpoints return paginated results with structure:
```json
{
  "data": [ ... ],
  "paging_info": {
    "numberOfPages": 10,
    "page": 0,
    "maxItemsPerPage": 250
  }
}
```

## Pagination Parameters (common to most endpoints)
- `page` -- 0-indexed page number (default: 0)
- `itemsPerPage` -- results per page (default: 250, max: 250)

## Key Endpoints

### Gene search (resolve symbol to GENCODE ID)
⚠️ **Important**: Always resolve gene symbols first — GTEx requires versioned GENCODE IDs for expression queries.
```
GET /reference/gene?geneId={symbol}&gencodeVersion=v26&genomeBuild=GRCh38/hg38
```

Parameters:
- `geneId` -- gene symbol (e.g. TP53) or Ensembl ID
- `gencodeVersion` -- `v26` for GTEx v8 (required)
- `genomeBuild` -- `GRCh38/hg38`

Example:
```
https://gtexportal.org/api/v2/reference/gene?geneId=TP53&gencodeVersion=v26&genomeBuild=GRCh38/hg38
```

Response (verified 2026-07):
```json
{
  "data": [
    {
      "chromosome": "chr17",
      "dataSource": "HAVANA",
      "description": "tumor protein p53 [Source:HGNC Symbol;Acc:HGNC:11998]",
      "end": 7687550,
      "entrezGeneId": 7157,
      "gencodeId": "ENSG00000141510.16",
      "gencodeVersion": "v26",
      "geneSymbol": "TP53",
      "geneType": "protein coding",
      "genomeBuild": "GRCh38/hg38",
      "start": 7661779,
      "strand": "-",
      "tss": 7687550
    }
  ],
  "paging_info": {"numberOfPages": 1, "page": 0, "maxItemsPerPage": 250, "totalNumberOfItems": 1}
}
```

⚠️ **Note**: `data` is an **array**, not an object. Access as `data[0].gencodeId`.

### Gene expression (median TPM by tissue)
```
GET /expression/medianGeneExpression?gencodeId={versioned_gencode_id}&datasetId=gtex_v8
```

Parameters:
- `gencodeId` -- Versioned Ensembl gene ID (required, e.g. `ENSG00000141510.16`)
- `datasetId` -- `gtex_v8` (required)
- `tissueSiteDetailId` -- filter to specific tissue (optional)

Example:
```
https://gtexportal.org/api/v2/expression/medianGeneExpression?gencodeId=ENSG00000141510.16&datasetId=gtex_v8
```

Returns median TPM per tissue for the gene.

### Gene expression (all genes, for a tissue)
```
GET /expression/medianGeneExpression?tissueSiteDetailId=Liver&datasetId=gtex_v8&page=0&itemsPerPage=250
```

### Single-tissue eQTLs
```
GET /association/singleTissueEqtl?gencodeId=ENSG00000139618.17&tissueSiteDetailId=Whole_Blood&datasetId=gtex_v8
```
Parameters:
- `gencodeId` -- Versioned Ensembl gene ID (required)
- `tissueSiteDetailId` -- tissue ID (required)
- `datasetId` -- `gtex_v8` (required)

### Multi-tissue eQTLs
```
GET /association/multiTissueEqtl?gencodeId=ENSG00000139618.17&datasetId=gtex_v8
```

### List tissues
```
GET /dataset/tissueSiteDetail?datasetId=gtex_v8
```
Returns all tissue site detail IDs, names, colors, sample counts.

### Exon expression
```
GET /expression/medianExonExpression?gencodeId=ENSG00000139618.17&datasetId=gtex_v8
```

### Transcript expression
```
GET /expression/medianTranscriptExpression?gencodeId=ENSG00000139618.17&datasetId=gtex_v8
```

### Top expressed genes in a tissue
```
GET /expression/topExpressedGene?tissueSiteDetailId=Brain_Cortex&datasetId=gtex_v8&filterMtGene=true
```

### Variant by location (dyadic)
```
GET /association/dyneqtl?variantId=chr1_1000000_A_G_b38&gencodeId=ENSG00000139618.17&tissueSiteDetailId=Whole_Blood&datasetId=gtex_v8
```

## Tissue ID examples
Use the underscore-separated names exactly:
- `Whole_Blood`, `Liver`, `Brain_Cortex`, `Heart_Left_Ventricle`
- `Muscle_Skeletal`, `Adipose_Subcutaneous`, `Lung`, `Skin_Sun_Exposed_Lower_leg`

## Example response (median gene expression)
```json
{
  "data": [
    {
      "datasetId": "gtex_v8",
      "gencodeId": "ENSG00000139618.17",
      "geneSymbol": "BRCA2",
      "median": 4.523,
      "tissueSiteDetailId": "Whole_Blood",
      "unit": "TPM"
    },
    {
      "datasetId": "gtex_v8",
      "gencodeId": "ENSG00000139618.17",
      "geneSymbol": "BRCA2",
      "median": 12.87,
      "tissueSiteDetailId": "Testis",
      "unit": "TPM"
    }
  ],
  "paging_info": { "numberOfPages": 1, "page": 0, "maxItemsPerPage": 250, "totalNumberOfItems": 54 }
}
```

## Rate Limits
- No published rate limits
- Reasonable request pacing recommended (~1-2 req/sec)
- For bulk analysis, download full datasets from the GTEx Portal downloads page

## Notes
- GTEx v8 is the primary dataset; always specify `datasetId=gtex_v8`
- Gene IDs must be versioned GENCODE IDs (e.g., ENSG00000139618.17)
- **Always use the gene search endpoint first** to resolve symbols to versioned GENCODE IDs:
  ```
  GET /reference/gene?geneId=TP53&gencodeVersion=v26&genomeBuild=GRCh38/hg38
  ```
- ⚠️ Not all genes have expression data in GTEx v8. If a gene returns an empty `data` array, it may not be in the dataset or the GENCODE version suffix may be wrong.
- Some GENCODE IDs without the version suffix (e.g. `ENSG00000141510`) may timeout — always use the versioned form with `.##` suffix.
- `gencodeVersion=v26` corresponds to GTEx v8
