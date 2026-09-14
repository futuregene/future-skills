import importlib.util
from pathlib import Path
import tempfile
import unittest

from check_builtin import validate_entry

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("custom_validator", ROOT / "builtin/future-skill-creator/scripts/validate_skill.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class CustomSkillValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name) / "example"
        self.folder.mkdir()

    def write(self, extra="", name="example"):
        (self.folder / "SKILL.md").write_text(
            f"---\nname: {name}\nversion: 1.0.0\ndescription: >\n  Tools: examples\n{extra}---\n# Example\n", encoding="utf-8")

    def test_valid_folded_description_and_false_flag(self):
        self.write("disable-model-invocation: false\n")
        data = validator.validate(self.folder)
        self.assertIs(data["disable-model-invocation"], False)

    def test_rejects_name_mismatch_duplicate_keys_and_non_boolean_flags(self):
        self.write(name="wrong")
        with self.assertRaises(ValueError):
            validator.validate(self.folder)
        for extra in ["name: example\n", "disableModelInvocation: 'false'\n",
                      "disableModelInvocation: true\ndisable_model_invocation: false\n"]:
            self.write(extra)
            with self.assertRaises(ValueError):
                validator.validate(self.folder)

    def test_builtin_and_custom_accept_the_same_semantic_versions(self):
        valid = ["1.2.3", "1.2.3-rc.1+build.7", "0.0.0+001", "1.0.0-0.alpha-x"]
        invalid = ["01.2.3", "1.2.3-01", "1.2.3-alpha..1", "1.2.3+", "1.2.3-a+b+c"]
        for version in valid + invalid:
            text = f"---\nname: example\nversion: {version}\ndescription: x\n---\n"
            (self.folder / "SKILL.md").write_text(text, encoding="utf-8")
            for check in [lambda: validator.validate(self.folder), lambda: validate_entry("example", text)]:
                with self.subTest(version=version, check=check):
                    if version in valid:
                        check()
                    else:
                        with self.assertRaises(ValueError):
                            check()

    def test_builtin_and_custom_agree_on_slug_length_and_policy(self):
        for size in [63, 64]:
            folder = Path(self.temp.name) / ("a" * size)
            folder.mkdir()
            text = f"---\nname: {folder.name}\nversion: 1.0.0\ndescription: x\n---\n"
            (folder / "SKILL.md").write_text(text, encoding="utf-8")
            for check in [lambda: validator.validate(folder), lambda: validate_entry(folder.name, text)]:
                if size == 63:
                    check()
                else:
                    with self.assertRaises(ValueError):
                        check()
        for extra in ["disableModelInvocation: 'false'", "disableModelInvocation: true\ndisable_model_invocation: false"]:
            text = f"---\nname: example\nversion: 1.0.0\ndescription: x\n{extra}\n---\n"
            with self.assertRaises(ValueError):
                validate_entry("example", text)

    def test_creator_validates_itself(self):
        validator.validate(ROOT / "builtin/future-skill-creator")


if __name__ == "__main__":
    unittest.main()
