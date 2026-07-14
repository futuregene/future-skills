#!/bin/bash
# Cross-database identifier resolution helper
# Usage: bash id_resolver.sh <type> <query>
#   types: gene-symbol, compound-name, variant-rsid, disease-name
# Examples:
#   bash id_resolver.sh gene-symbol TP53
#   bash id_resolver.sh compound-name aspirin
#   bash id_resolver.sh variant-rsid rs334
#   bash id_resolver.sh disease-name "cystic fibrosis"

set -euo pipefail

TYPE="${1:-}"
QUERY="${2:-}"

if [ -z "$TYPE" ] || [ -z "$QUERY" ]; then
    echo "Usage: id_resolver.sh <type> <query>"
    echo "  types: gene-symbol, compound-name, variant-rsid, disease-name"
    exit 1
fi

resolve_gene() {
    local SYMBOL="$1"
    echo "=== Resolving gene: $SYMBOL ===" >&2

    # Step 1: NCBI Gene ID
    local NCBI_ID
    NCBI_ID=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=${SYMBOL}%5BGene+Name%5D+AND+human%5BOrganism%5D&retmax=1&retmode=json" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['esearchresult']['idlist'][0])" 2>/dev/null || echo "")
    if [ -z "$NCBI_ID" ]; then
        echo "ERROR: Could not resolve gene symbol '$SYMBOL' via NCBI Gene" >&2
        exit 1
    fi

    # Step 2: Ensembl ID
    local ENSG
    ENSG=$(curl -s "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/${SYMBOL}?content-type=application/json" \
        | python3 -c "import sys,json; items=json.load(sys.stdin); print(next(i['id'] for i in items if i['type']=='gene'))" 2>/dev/null || echo "")
    if [ -z "$ENSG" ]; then
        ENSG="(not found)"
    fi

    # Step 3: UniProt accession (prefer Swiss-Prot reviewed entry)
    local UNIPROT
    UNIPROT=$(curl -s "https://rest.uniprot.org/uniprotkb/search?query=(gene_exact:${SYMBOL})+AND+(organism_id:9606)+AND+(reviewed:true)&fields=accession&size=1" \
        | python3 -c "import sys,json; results=json.load(sys.stdin)['results']; print(results[0]['primaryAccession'] if results else '')" 2>/dev/null || echo "")
    if [ -z "$UNIPROT" ]; then
        UNIPROT="(not found)"
    fi

    echo "---" >&2
    echo "NCBI Gene:  $NCBI_ID"
    echo "Ensembl:    $ENSG"
    echo "UniProt:    $UNIPROT"
}

resolve_compound() {
    local NAME="$1"
    echo "=== Resolving compound: $NAME ===" >&2

    # Step 1: PubChem CID
    local CID
    CID=$(curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/${NAME}/cids/JSON" \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['IdentifierList']['CID'][0])" 2>/dev/null || echo "")
    if [ -z "$CID" ]; then
        echo "ERROR: Could not resolve compound '$NAME' via PubChem" >&2
        exit 1
    fi

    # Step 2: SMILES, InChIKey, MW
    local PROPS
    PROPS=$(curl -s "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/${CID}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,InChIKey,IUPACName/JSON")
    local FORMULA=$(echo "$PROPS" | python3 -c "import sys,json; print(json.load(sys.stdin)['PropertyTable']['Properties'][0].get('MolecularFormula','N/A'))" 2>/dev/null || echo "N/A")
    local MW=$(echo "$PROPS" | python3 -c "import sys,json; print(json.load(sys.stdin)['PropertyTable']['Properties'][0].get('MolecularWeight','N/A'))" 2>/dev/null || echo "N/A")
    local SMILES=$(echo "$PROPS" | python3 -c "import sys,json; print(json.load(sys.stdin)['PropertyTable']['Properties'][0].get('CanonicalSMILES', json.load(sys.stdin)['PropertyTable']['Properties'][0].get('ConnectivitySMILES','N/A')))" 2>/dev/null || echo "N/A")
    local INCHIKEY=$(echo "$PROPS" | python3 -c "import sys,json; print(json.load(sys.stdin)['PropertyTable']['Properties'][0].get('InChIKey','N/A'))" 2>/dev/null || echo "N/A")

    # Step 3: ChEMBL ID via molecule search
    local CHEMBL
    CHEMBL=$(curl -s "https://www.ebi.ac.uk/chembl/api/data/molecule.json?pref_name__iregex=${NAME}&limit=1" \
        | python3 -c "import sys,json; data=json.load(sys.stdin); mols=data.get('molecules',[]); print(mols[0]['molecule_chembl_id'] if mols else 'N/A')" 2>/dev/null || echo "N/A")

    echo "---" >&2
    echo "PubChem CID: $CID"
    echo "Formula:     $FORMULA"
    echo "Mol Weight:  $MW"
    echo "SMILES:      $SMILES"
    echo "InChIKey:    $INCHIKEY"
    echo "ChEMBL:      CHEMBL${CHEMBL}"
}

resolve_variant() {
    local RSID="$1"
    echo "=== Resolving variant: $RSID ===" >&2

    # ClinVar
    local CLINVAR
    CLINVAR=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=clinvar&id=${RSID}&retmode=json" \
        | python3 -c "
import sys,json
data=json.load(sys.stdin)
result=data['result'][next(k for k in data['result'].keys() if k!='uids')]
print(f\"ClinVar title: {result.get('title','N/A')}\")
print(f\"Clinical significance: {result.get('clinical_significance','N/A')}\")
" 2>/dev/null || echo "ClinVar: N/A")

    # dbSNP
    local DBSNP
    DBSNP=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&id=${RSID}&retmode=json" \
        | python3 -c "
import sys,json
data=json.load(sys.stdin)
result=data['result'][next(k for k in data['result'].keys() if k!='uids')]
print(f\"dbSNP: chr{result.get('chr','?')}:{result.get('chrpos','?')}, alleles: {result.get('snp_class','?')}\")
" 2>/dev/null || echo "dbSNP: N/A")

    echo "---" >&2
    echo "$CLINVAR"
    echo "$DBSNP"
}

resolve_disease() {
    local NAME="$1"
    echo "=== Resolving disease: $NAME ===" >&2

    # Open Targets
    local OT_RESULT
    OT_RESULT=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        --data-raw "{\"query\":\"{ search(queryString: \\\"${NAME}\\\", entityNames:[\\\"disease\\\"], page:{size:3}) { hits { id name } } }\"}" \
        https://api.platform.opentargets.org/api/v4/graphql \
        | python3 -c "
import sys,json
data=json.load(sys.stdin)
hits=data['data']['search']['hits']
for h in hits:
    print(f\"Open Targets: {h['id']} — {h['name']}\")
" 2>/dev/null || echo "Open Targets: N/A")

    echo "---" >&2
    echo "$OT_RESULT"
}

case "$TYPE" in
    gene-symbol)     resolve_gene "$QUERY" ;;
    compound-name)   resolve_compound "$QUERY" ;;
    variant-rsid)    resolve_variant "$QUERY" ;;
    disease-name)    resolve_disease "$QUERY" ;;
    *)
        echo "Unknown type: $TYPE"
        echo "Valid types: gene-symbol, compound-name, variant-rsid, disease-name"
        exit 1
        ;;
esac
