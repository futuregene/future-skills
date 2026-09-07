from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_deck as runner


class DeckRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.slides = [dict(idx=f"{i:02}", prompt=f"Slide {i}", image=f"slide_{i:02}.png")
                       for i in range(1, 4)]
        self.manifest = self.root / "deck.json"
        self.save_manifest()

    def save_manifest(self):
        self.manifest.write_text(json.dumps({"slides": self.slides}), encoding="utf-8")

    def image(self, name):
        path = self.root / name
        Image.new("RGB", (16, 16), "white").save(path)
        return path

    def fake_generation(self, command, **kwargs):
        self.assertEqual(command[:4], ["future", "tools", "call", "image_gen"])
        self.assertEqual(json.loads(kwargs["input"])["n"], 1)
        Image.new("RGB", (16, 16), "white").save(command[command.index("--output") + 1])
        return subprocess.CompletedProcess(command, 0, "saved", "")

    def test_success_has_verified_image_metadata_and_no_implicit_review(self):
        with patch.object(runner.subprocess, "run", side_effect=self.fake_generation):
            records = runner.generate(self.root, self.slides, 2, 600)
        self.assertEqual([r["status"] for r in records], ["generated"] * 3)
        self.assertTrue(all(r["width"] == 16 and len(r["sha256"]) == 64 for r in records))
        with self.assertRaises(ValueError):
            runner.check_slides(self.root, self.slides, require_review=True)

    def test_failed_generation_exits_nonzero_and_stops_dispatch(self):
        with patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", "failed")) as call:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(["generate", str(self.manifest)]), 1)
        call.assert_called_once()
        receipt = json.loads(next(self.root.glob("generation-*.json")).read_text())
        self.assertEqual(receipt["results"][0]["status"], "failed")
        self.assertFalse((self.root / "slide_01.png").exists())

    def test_zero_exit_without_image_is_failure(self):
        with patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "", "")):
            record = runner.generate_one(self.root, self.slides[0], 600)
        self.assertEqual(record["status"], "failed")

    def test_timeout_is_uncertain_and_never_retried(self):
        with patch.object(runner.subprocess, "run", side_effect=subprocess.TimeoutExpired("future", 630)) as call:
            records = runner.generate(self.root, self.slides, 1, 600)
        call.assert_called_once()
        self.assertEqual(records[0]["status"], "uncertain")
        self.assertIn("remote completion/cost unknown", records[0]["error"])

    def test_existing_image_is_never_mistaken_for_new_success(self):
        path = self.image("slide_01.png")
        original = path.read_bytes()
        with patch.object(runner.subprocess, "run") as call:
            record = runner.generate_one(self.root, self.slides[0], 600)
        call.assert_not_called()
        self.assertEqual(record["status"], "failed")
        self.assertEqual(path.read_bytes(), original)

    def test_invalid_manifest_paths_and_collisions(self):
        for value in ["../escape.png", str(self.root / "absolute.png"), "C:\\escape.png"]:
            with self.assertRaises(ValueError):
                runner.local_path(self.root, value)
        self.slides[1]["image"] = "SLIDE_01.PNG"
        self.save_manifest()
        with self.assertRaises(ValueError):
            runner.load_manifest(self.manifest)

    def test_assembly_requires_all_images_and_current_hashes(self):
        self.image("slide_01.png")
        with self.assertRaises(OSError):
            runner.check_slides(self.root, self.slides)
        for slide in self.slides:
            self.image(slide["image"])
            slide.update(reviewed=True, review_note="Synthetic test review", sha256="wrong")
        with self.assertRaises(ValueError):
            runner.assemble(self.root, self.slides, "out.pdf")
        self.assertFalse((self.root / "out.pdf").exists())

    def test_pdf_uses_exact_manifest_order_and_one_revision_per_slide(self):
        self.image("slide_01.png")  # obsolete original is deliberately present
        self.slides[0]["image"] = "slide_01_fixed.png"
        for slide in self.slides:
            path = self.image(slide["image"])
            slide.update(reviewed=True, review_note="Synthetic test review", **runner.inspect_image(path))
        self.slides.reverse()
        import img2pdf
        real_convert = img2pdf.convert
        with patch.object(img2pdf, "convert", wraps=real_convert) as convert:
            result = runner.assemble(self.root, self.slides, "out.pdf")
        self.assertEqual(convert.call_args.args[0], [str(self.root / s["image"]) for s in self.slides])
        self.assertTrue(result.read_bytes().startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
