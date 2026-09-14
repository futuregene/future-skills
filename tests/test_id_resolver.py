"""No-network regression coverage for the bundled database helper."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("id_resolver", ROOT / "builtin/future-database-lookup/scripts/id_resolver.py")
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)


class FakeClient:
    def __init__(self, *responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, params=None, payload=None):
        self.calls.append((url, params, payload))
        return next(self.responses)


class IdResolverTests(unittest.TestCase):
    def test_smiles_is_read_once_and_chembl_id_is_not_prefixed_twice(self):
        for smiles_key in ["CanonicalSMILES", "ConnectivitySMILES", "SMILES"]:
            client = FakeClient({"IdentifierList": {"CID": [2244]}},
                                {"PropertyTable": {"Properties": [{smiles_key: "CC(=O)O", "InChIKey": "KEY"}]}},
                                {"molecules": [{"molecule_chembl_id": "CHEMBL25"}], "page_meta": {"total_count": 1}})
            result = resolver.resolve_compound(client, "acetyl salicylic/acid")
            self.assertEqual(result["smiles"], "CC(=O)O")
            self.assertEqual(result["chembl_ids"], ["CHEMBL25"])
            self.assertIn("acetyl%20salicylic%2Facid", client.calls[0][0])
            self.assertEqual(client.calls[2][1]["molecule_structures__standard_inchi_key"], "KEY")

    def test_ambiguous_compound_does_not_select_first_hit(self):
        client = FakeClient({"IdentifierList": {"CID": [1, 2]}})
        result = resolver.resolve_compound(client, "ambiguous")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(len(client.calls), 1)

    def test_variant_uses_elink_and_numeric_ids_not_rsid_as_clinvar_id(self):
        client = FakeClient({"result": {"uids": ["334"]}}, {"linksets": [{"linksetdbs": [
            {"dbto": "clinvar", "links": ["15333", "15175", "15175"]}]}]},
            {"result": {"uids": ["15175", "15333"]}})
        result = resolver.resolve_variant(client, "rs334")
        self.assertEqual(client.calls[0][1]["id"], "334")
        self.assertTrue(client.calls[1][0].endswith("elink.fcgi"))
        self.assertEqual(client.calls[2][1]["id"], "15175,15333")
        self.assertEqual(result["clinvar_ids"], ["15175", "15333"])
        self.assertTrue(result["clinvar_summaries_complete"])

    def test_no_clinvar_link_and_summary_limit_are_explicit(self):
        client = FakeClient({"result": {}}, {"linksets": []})
        self.assertEqual(resolver.resolve_variant(client, "rs1")["clinvar_ids"], [])
        ids = [str(i) for i in range(1, 25)]
        client = FakeClient({"result": {}}, {"linksets": [{"linksetdbs": [
            {"dbto": "clinvar", "links": ids}]}]}, {"result": {}})
        result = resolver.resolve_variant(client, "rs1")
        self.assertFalse(result["clinvar_summaries_complete"])
        self.assertEqual(len(client.calls[2][1]["id"].split(",")), 20)

    def test_missing_summary_is_not_reported_complete(self):
        client = FakeClient({"result": {}}, {"linksets": [{"linksetdbs": [
            {"dbto": "clinvar", "links": ["1", "2"]}]}]}, {"result": {"uids": ["1"]}})
        self.assertFalse(resolver.resolve_variant(client, "rs1")["clinvar_summaries_complete"])

    def test_gene_requires_taxon_and_does_not_hide_truncation(self):
        client = FakeClient()
        with self.assertRaises(ValueError):
            resolver.resolve_gene(client, "TP53", None)
        self.assertFalse(client.calls)
        client = FakeClient({"esearchresult": {"count": "30", "idlist": ["7157"]}}, {"results": []})
        result = resolver.resolve_gene(client, "TP53", 9606)
        self.assertFalse(result["ncbi_gene"]["complete"])
        self.assertIn("txid9606", client.calls[0][1]["term"])

    def test_disease_text_is_a_graphql_variable(self):
        client = FakeClient({"data": {"search": {"hits": []}}})
        name = 'a "quoted" condition\\test'
        resolver.resolve_disease(client, name)
        payload = client.calls[0][2]
        self.assertNotIn(name, payload["query"])
        self.assertIn("page: {index: 0, size: 3}", payload["query"])
        self.assertEqual(payload["variables"]["term"], name)
        self.assertEqual(json.loads(json.dumps(payload)), payload)

    def test_http_request_encodes_parameters_and_has_timeout(self):
        with patch.object(resolver, "urlopen", return_value=io.BytesIO(b'{"ok":true}')) as opened:
            client = resolver.Client()
            client.get("https://example.org/api", {"q": "a & b+?"})
            args, kwargs = opened.call_args
            self.assertEqual(parse_qs(urlsplit(args[0].full_url).query)["q"], ["a & b+?"])
            self.assertEqual(kwargs["timeout"], 30)
            self.assertEqual(len(client.requests), 1)

    def test_http_and_api_errors_are_not_successful_na_or_retried(self):
        with patch.object(resolver, "urlopen", side_effect=HTTPError("https://example.org", 429, "limited", {}, None)) as opened:
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(resolver.main(["compound-name", "aspirin"]), 1)
            self.assertIn("HTTP 429", stderr.getvalue())
            self.assertEqual(opened.call_count, 1)
        for body in [b'{"errors":[{"message":"failed"}]}', b'{"result":{"1":{"error":"invalid uid"}}}']:
            with patch.object(resolver, "urlopen", return_value=io.BytesIO(body)):
                with self.assertRaises(ValueError):
                    resolver.Client().get("https://example.org")


if __name__ == "__main__":
    unittest.main()
