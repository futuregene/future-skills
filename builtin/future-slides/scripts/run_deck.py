#!/usr/bin/env python3
"""Manifest-driven slide generation, validation and PDF assembly.

Only the `generate` subcommand invokes paid Future tools. It never retries.
A process timeout does NOT establish cancellation of the remote generation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import subprocess
import tempfile
import uuid

from PIL import Image


def local_path(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or PureWindowsPath(value).drive:
        raise ValueError("Artifact paths must be relative to the manifest directory")
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Artifact escapes the deck directory: {value}")
    return path


def load_manifest(path):
    root = path.resolve().parent
    manifest = json.loads(path.read_text(encoding="utf-8"))
    slides = manifest.get("slides") if isinstance(manifest, dict) else None
    if not isinstance(slides, list) or not slides:
        raise ValueError("Manifest needs a nonempty slides array in presentation order")
    ids, outputs = set(), set()
    for slide in slides:
        if not isinstance(slide, dict):
            raise ValueError("Each slide must be an object")
        idx = slide.get("idx")
        if not isinstance(idx, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", idx) or idx in ids:
            raise ValueError("Slide IDs must be unique safe strings")
        ids.add(idx)
        image = local_path(root, slide.get("image"))
        key = str(image).casefold()
        if image.suffix.lower() != ".png" or key in outputs:
            raise ValueError("Each slide must name a distinct PNG (portable case-insensitive paths)")
        outputs.add(key)
        if not isinstance(slide.get("prompt"), str) or not slide["prompt"].strip():
            raise ValueError(f"Slide {idx} needs its exact prompt")
    return root, slides


def inspect_image(path):
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError(f"Not a PNG: {path}")
        width, height = image.size
        image.verify()
    # Decode as well: valid container metadata is not enough for a usable slide.
    with Image.open(path) as image:
        image.load()
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "width": width, "height": height}


def check_slides(root, slides, require_review=False):
    records = []
    for slide in slides:
        info = inspect_image(local_path(root, slide["image"]))
        if require_review and (slide.get("sha256") != info["sha256"]
                               or slide.get("reviewed") is not True
                               or not isinstance(slide.get("review_note"), str)
                               or not slide["review_note"].strip()):
            raise ValueError(f"Slide {slide['idx']} needs review evidence bound to its current image hash")
        records.append({"idx": slide["idx"], "image": slide["image"], **info})
    return records


def generate_one(root, slide, timeout):
    record = {"idx": slide["idx"], "image": slide["image"], "status": "failed"}
    try:
        target = local_path(root, slide["image"])
        if target.exists():
            raise ValueError("Image already exists: select a new revision path or generate only missing slides")
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=f".slide-{slide['idx']}-", dir=root) as temporary:
            candidate = Path(temporary) / "candidate.png"
            payload = {"prompt": slide["prompt"], "size": slide.get("size", "1792x1024"),
                       "quality": slide.get("quality", "medium"), "output_format": "png", "n": 1}
            call = subprocess.run(
                ["future", "tools", "call", "image_gen", "--stdin", "--output", str(candidate),
                 "--timeout", str(timeout)], input=json.dumps(payload), capture_output=True,
                text=True, timeout=timeout + 30, check=False,
            )
            record["exit_code"] = call.returncode
            if call.returncode:
                raise ValueError((call.stderr or call.stdout or "Generation failed")[-2000:])
            info = inspect_image(candidate)
            os.replace(candidate, target)
            record.update(status="generated", **info)
    except subprocess.TimeoutExpired:
        record.update(status="uncertain", error="CLI timeout; remote completion/cost unknown. Inspect before any retry.")
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as error:
        record["error"] = str(error)
    return record


def generate(root, slides, jobs, timeout):
    records = []
    # Only one batch is dispatched at a time; settle that batch, stop on any
    # failure/uncertainty, and never queue the rest of the deck after a failure.
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for start in range(0, len(slides), jobs):
            futures = [pool.submit(generate_one, root, slide, timeout)
                       for slide in slides[start:start + jobs]]
            batch = [future.result() for future in futures]
            records.extend(batch)
            if any(record["status"] != "generated" for record in batch):
                break
    return records


def assemble(root, slides, output):
    import img2pdf
    check_slides(root, slides, require_review=True)
    destination = local_path(root, output)
    if destination.suffix.lower() != ".pdf":
        raise ValueError("PDF output must end in .pdf")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exact manifest order: never glob, so _fixed images are not added twice.
    paths = [str(local_path(root, slide["image"])) for slide in slides]
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".pdf", delete=False) as file:
        temporary = Path(file.name)
    try:
        with temporary.open("wb") as file:
            img2pdf.convert(paths, outputstream=file)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["generate", "check", "assemble"])
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--only", help="Comma-separated slide IDs to generate; no automatic retries")
    parser.add_argument("--jobs", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--timeout", type=int, default=600, help="Per CLI HTTP timeout; process allowance is 30s longer")
    parser.add_argument("--output", default="slides.pdf", help="PDF path relative to the manifest")
    args = parser.parse_args(argv)
    try:
        if args.timeout <= 0:
            raise ValueError("Timeout must be positive")
        root, slides = load_manifest(args.manifest)
        if args.command == "generate":
            selected = slides
            if args.only:
                wanted = set(args.only.split(","))
                if not wanted <= {slide["idx"] for slide in slides}:
                    raise ValueError("--only contains unknown slide IDs")
                selected = [slide for slide in slides if slide["idx"] in wanted]
            records = generate(root, selected, args.jobs, args.timeout)
            receipt = root / f"generation-{uuid.uuid4().hex}.json"
            receipt.write_text(json.dumps({"manifest": str(args.manifest.resolve()), "results": records},
                                           ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"receipt": str(receipt), "results": records}, ensure_ascii=False))
            return 0 if len(records) == len(selected) and all(r["status"] == "generated" for r in records) else 1
        if args.only:
            raise ValueError("--only is valid only for generate; final validation/assembly must cover every slide")
        if args.command == "check":
            print(json.dumps({"images": check_slides(root, slides), "visual_review": "not assessed"}))
        else:
            print(json.dumps({"pdf": str(assemble(root, slides, args.output)), "slides": len(slides)}))
        return 0
    except (OSError, ValueError, ImportError, SyntaxError, Image.DecompressionBombError) as error:
        print(json.dumps({"error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
