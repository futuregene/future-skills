#!/usr/bin/env python3
"""Bounded public ID lookups. Candidate lists are not unique identity assertions.

Uses Python's standard library on Windows/macOS/Linux. No keys, implicit human
organism, automatic retries, or files. Outputs JSON with request provenance.
"""
import argparse
from datetime import datetime, timezone
import json
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


class Client:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.requests = []
        self.last_ncbi = None

    def get(self, url, params=None, payload=None):
        if url.startswith(EUTILS):
            if self.last_ncbi is not None:
                time.sleep(max(0, 0.35 - (time.monotonic() - self.last_ncbi)))
            self.last_ncbi = time.monotonic()
        params = params or {}
        body = json.dumps(payload).encode() if payload is not None else None
        request = Request(url + ("?" + urlencode(params) if params else ""), data=body,
                          headers={"Accept": "application/json", "Content-Type": "application/json"})
        self.requests.append({"endpoint": url, "parameters": params, "payload": payload,
                              "accessed_at": datetime.now(timezone.utc).isoformat()})
        with urlopen(request, timeout=self.timeout) as response:
            data = json.load(response)
        if not isinstance(data, dict) or data.get("error") or data.get("errors"):
            raise ValueError("API returned an error or an unexpected JSON shape")
        if isinstance(data.get("result"), dict) and any(
                isinstance(item, dict) and item.get("error") for item in data["result"].values()):
            raise ValueError("Summary contains a record-level API error")
        return data


def search_ids(client, db, term):
    result = client.get(EUTILS + "esearch.fcgi", {
        "db": db, "term": term, "retmax": 20, "retmode": "json"})["esearchresult"]
    if any(result.get("errorlist", {}).values()) or any(result.get("warninglist", {}).values()):
        raise ValueError("Search reported a warning/error; inspect query semantics manually")
    ids = result["idlist"]
    return {"ids": ids, "total": int(result["count"]),
            "complete": len(ids) == int(result["count"]),
            "query_translation": result.get("querytranslation")}


def resolve_gene(client, symbol, taxon):
    if taxon is None or taxon <= 0:
        raise ValueError("gene-symbol requires an explicit positive --taxon (e.g. 9606 for human)")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", symbol):
        raise ValueError("Use a single gene symbol, not an Entrez query expression")
    genes = search_ids(client, "gene", f'"{symbol}"[Gene Name] AND txid{taxon}[Organism]')
    proteins = client.get("https://rest.uniprot.org/uniprotkb/search", {
        "query": f"(gene_exact:{symbol}) AND (organism_id:{taxon}) AND (reviewed:true)",
        "fields": "accession,gene_names,organism_id", "size": 20, "format": "json"})
    return {"taxon": taxon, "ncbi_gene": genes,
            "uniprot_candidates": proteins["results"],
            "note": "UniProt is a first-page reviewed-protein candidate list, not an exhaustive or one-to-one gene mapping."}


def resolve_compound(client, name):
    result = client.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
                        + quote(name, safe="") + "/cids/JSON")
    cids = result["IdentifierList"]["CID"]
    if len(cids) != 1:
        return {"pubchem_candidates": cids, "status": "ambiguous" if cids else "not_found"}
    props = client.get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
                       + str(cids[0]) + "/property/MolecularFormula,MolecularWeight,CanonicalSMILES,InChIKey/JSON")
    prop = props["PropertyTable"]["Properties"][0]
    smiles = prop.get("CanonicalSMILES") or prop.get("ConnectivitySMILES") or prop.get("SMILES")
    result = {"pubchem_cid": cids[0], "properties": prop, "smiles": smiles,
              "smiles_note": "Connectivity/canonical SMILES is not a guarantee of stereochemical identity."}
    if prop.get("InChIKey"):
        chembl = client.get("https://www.ebi.ac.uk/chembl/api/data/molecule.json", {
            "molecule_structures__standard_inchi_key": prop["InChIKey"], "limit": 20})
        result["chembl_ids"] = [m["molecule_chembl_id"] for m in chembl["molecules"]]
        result["chembl_total"] = chembl["page_meta"]["total_count"]
        result["chembl_complete"] = len(result["chembl_ids"]) == result["chembl_total"]
    return result


def resolve_variant(client, rsid):
    if not re.fullmatch(r"rs[1-9][0-9]*", rsid):
        raise ValueError("variant-rsid requires an rsID such as rs334")
    numeric = rsid[2:]
    snp = client.get(EUTILS + "esummary.fcgi", {"db": "snp", "id": numeric, "retmode": "json"})
    links = client.get(EUTILS + "elink.fcgi", {
        "dbfrom": "snp", "db": "clinvar", "id": numeric, "retmode": "json"})
    ids = sorted({str(i) for group in links.get("linksets", [])
                  for link in group.get("linksetdbs", []) if link.get("dbto") == "clinvar"
                  for i in link.get("links", [])}, key=int)
    result = {"rsid": rsid, "dbsnp": snp["result"], "clinvar_ids": ids,
              "clinvar_total_linked": len(ids), "clinvar_summaries_complete": len(ids) <= 20}
    if ids:
        result["clinvar"] = client.get(EUTILS + "esummary.fcgi", {
            "db": "clinvar", "id": ",".join(ids[:20]), "retmode": "json"})["result"]
        result["clinvar_summaries_complete"] = set(result["clinvar"].get("uids", [])) == set(ids)
    return result


def resolve_disease(client, name):
    query = """query ResolveDisease($term: String!) {
      search(queryString: $term, entityNames: [\"disease\"], page: {index: 0, size: 3}) {
        hits { id name }
      }
    }"""
    data = client.get("https://api.platform.opentargets.org/api/v4/graphql",
                      payload={"query": query, "variables": {"term": name}})
    return {"candidates": data["data"]["search"]["hits"],
            "note": "At most three search candidates; not an exact identity or exhaustive list."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("type", choices=["gene-symbol", "compound-name", "variant-rsid", "disease-name"])
    parser.add_argument("query")
    parser.add_argument("--taxon", type=int, help="Required for gene-symbol; no implicit human default")
    args = parser.parse_args(argv)
    if not args.query.strip():
        parser.error("query must not be empty")
    client = Client()
    try:
        if args.type == "gene-symbol":
            result = resolve_gene(client, args.query, args.taxon)
        else:
            resolver = {"compound-name": resolve_compound, "variant-rsid": resolve_variant,
                        "disease-name": resolve_disease}[args.type]
            result = resolver(client, args.query)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as error:
        # Do not turn transport, schema or API failures into a successful "N/A".
        detail = f"HTTP {error.code}" if isinstance(error, HTTPError) else type(error).__name__
        if isinstance(error, HTTPError):
            error.close()
        if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError):
            detail += f": {error}"
        endpoint = client.requests[-1]["endpoint"] if client.requests else "before any request"
        print(f"Lookup failed ({detail}) at {endpoint}; no verified result. No automatic retry was made.", file=sys.stderr)
        return 1
    print(json.dumps({"query": args.query, "result": result, "requests": client.requests}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
