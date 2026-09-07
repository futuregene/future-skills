import importlib.util
from pathlib import Path
import tempfile
import unittest

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

    def test_creator_validates_itself(self):
        validator.validate(ROOT / "builtin/future-skill-creator")


if __name__ == "__main__":
    unittest.main()
