from pathlib import Path
import tempfile
import unittest

import yaml

from check_builtin import check_fences, validate_entry, validate_resources


class BuiltinValidationTests(unittest.TestCase):
    def test_folded_description_is_valid(self):
        header = validate_entry("example", "---\nname: example\nversion: 1.2.3\ndescription: >\n  Tools: safe usage\n---\n```sh\necho ok\n```\n")
        self.assertIn("Tools: safe usage", header["description"])

    def test_bad_yaml_and_duplicate_keys_are_rejected(self):
        for description in ["description: Tools: broken", "description: one\ndescription: two"]:
            with self.assertRaises((ValueError, yaml.YAMLError)):
                validate_entry("example", f"---\nname: example\nversion: 1.2.3\n{description}\n---\n")

    def test_inline_closer_and_unclosed_fences_are_rejected(self):
        for text in ["```bash\necho ok ```\n", "```python\nprint(1)\n"]:
            with self.assertRaises(ValueError):
                check_fences(text)
        check_fences('```python\nprint("```")\n```\n~~~text\nhello\n~~~\n')

    def test_resource_paths_are_real_and_contained(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "references").mkdir()
            (root / "references/real.md").write_text("example")
            validate_resources(root, "Read `references/real.md`.")
            for text in ["Read `references/missing.md`.", "[bad](references/../../escape.md)"]:
                with self.assertRaises(ValueError):
                    validate_resources(root, text)
            validate_resources(root, "```text\nExample `references/placeholder.md`\n```\n")

    def test_missing_fields_and_mismatched_names_are_rejected(self):
        for header in ["name: wrong\nversion: 1.2.3\ndescription: x",
                       "name: example\ndescription: x",
                       "name: example\nversion: 1.2.3"]:
            with self.assertRaises(ValueError):
                validate_entry("example", f"---\n{header}\n---\n")


if __name__ == "__main__":
    unittest.main()
