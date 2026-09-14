"""Static contracts plus executable no-network checks for audited resources."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AuditContractTests(unittest.TestCase):
    def test_retired_generators_fail_closed_without_outputs(self):
        for name in ["generate_schematic.py", "generate_schematic_ai.py"]:
            script = ROOT / "builtin/future-peer-review/scripts" / name
            with tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "figure.png"
                result = subprocess.run([sys.executable, str(script), "test", "-o", str(output)],
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 2)
                self.assertIn("No image was generated or reviewed", result.stderr)
                self.assertFalse(list(Path(temp).iterdir()))

    def test_guideline_versions_and_item_counts_are_consistent(self):
        text = (ROOT / "builtin/future-scientific-writing/references/reporting_guidelines.md").read_text(encoding="utf-8")
        for expected in ["CONSORT 2025", "SPIRIT 2025", "TRIPOD+AI", "30 items", "34 items", "27-item"]:
            self.assertIn(expected, text)
        for stale in ["**Latest version:** CONSORT 2010", "**Latest version:** SPIRIT 2013", "**Latest version:** TRIPOD 2015"]:
            self.assertNotIn(stale, text)

    def test_request_pacer_never_reduces_the_minimum_delay(self):
        text = (ROOT / "builtin/future-database-lookup/scripts/rate_limiter.sh").read_text(encoding="utf-8")
        self.assertIn("random.uniform(1.0, 1.2)", text)
        self.assertIn("--fail", text)
        self.assertIn("--max-time 30", text)
        self.assertIn("NOT a cross-process/global rate limiter", text)

    def test_private_urls_route_before_remote_fetch(self):
        text = (ROOT / "builtin/future-web/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("use remote services", text)
        self.assertIn("local, intranet, signed", text)
        self.assertIn("service-specific skill", text)


if __name__ == "__main__":
    unittest.main()
