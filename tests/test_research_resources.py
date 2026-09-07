from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ResearchResourceTests(unittest.TestCase):
    def test_entry_resources_exist_and_retired_dependencies_are_absent(self):
        for name in ["future-scientific-writing", "future-peer-review", "future-database-lookup"]:
            folder = ROOT / "builtin" / name
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            self.assertLess(len(text.splitlines()), 180, name)
            self.assertNotIn("research-lookup", text)
            self.assertNotIn("skills/scientific-slides/scripts/pdf_to_images.py", text)
            for resource in re.findall(r"`((?:references|assets)/[^`]+)`", text):
                self.assertTrue((folder / resource).is_file(), resource)

    def test_database_index_covers_each_database_reference_once(self):
        folder = ROOT / "builtin/future-database-lookup/references"
        text = (folder / "database-index.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+\.md)\)", text)
        self.assertEqual(len(links), len(set(links)))
        self.assertEqual(set(links), {p.name for p in folder.glob("*.md")} - {"database-index.md"})
        self.assertEqual(len(links) - 1, 78)  # the additional link is the retrieval contract


if __name__ == "__main__":
    unittest.main()
