#!/usr/bin/env python3
"""
Generate and edit images using the future CLI image tools.

Supports:
- Image generation from text prompts (future tools call image_gen)
- Image editing from text prompts + input image (future tools call image_edit)

Authentication is automatic — the future CLI reads credentials from ~/.future/agent/auth.json.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _run_future(args: list, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a future CLI command and return the result."""
    try:
        result = subprocess.run(
            ["future"] + args,
            capture_output=True, text=True, timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print("❌ Error: Command timed out")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: `future` CLI not found. Please install it first.")
        sys.exit(1)


def generate_image(
    prompt: str,
    output_path: str = "generated_image.png",
    size: str = "1024x1024",
    quality: str = "high",
    input_image: str | None = None
) -> dict:
    """
    Generate or edit an image using the future CLI.

    Args:
        prompt: Text description or editing instructions
        output_path: Path to save the generated image
        size: Image size (1024x1024, 1792x1024, 1024x1792, 2560x1440, 3840x2160)
        quality: Image quality (low, medium, high)
        input_image: Path to an input image for editing (optional)

    Returns:
        dict: Parsed JSON response from the CLI
    """
    if input_image:
        tool = "image_edit"
        args_dict = {
            "prompt": prompt,
            "image_path": str(Path(input_image).resolve()),
            "quality": quality,
            "output_format": Path(output_path).suffix.lstrip(".") or "png"
        }
        print(f"✏️ Editing image: {input_image}")
        print(f"📝 Edit prompt: {prompt}")
    else:
        tool = "image_gen"
        args_dict = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "output_format": Path(output_path).suffix.lstrip(".") or "png"
        }
        print(f"🎨 Generating image")
        print(f"📝 Prompt: {prompt}")
        print(f"📐 Size: {size}")

    print(f"⏳ Working (this may take a few minutes)...")

    result = _run_future([
        "tools", "call", tool,
        "--args", json.dumps(args_dict),
        "--output", output_path
    ])

    if result.returncode != 0:
        # Try to parse error from stderr or stdout
        error_msg = result.stderr.strip() or result.stdout.strip()
        try:
            error_json = json.loads(error_msg)
            error_msg = error_json.get("error", error_json.get("message", str(error_json)))
        except (json.JSONDecodeError, TypeError):
            pass
        print(f"❌ CLI Error: {error_msg}")
        sys.exit(1)

    # Parse JSON output for any warnings/notes
    try:
        response = json.loads(result.stdout.strip()) if result.stdout.strip() else {}
    except json.JSONDecodeError:
        response = {"raw": result.stdout.strip()}

    print(f"✅ Image saved to: {output_path}")
    return response


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images using future CLI image tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate an image
  python generate_image.py "A beautiful sunset over mountains"

  # Specify output path
  python generate_image.py "Abstract art" --output my_image.png

  # Edit an existing image
  python generate_image.py "Make the sky purple" --input photo.jpg --output edited.png

  # Custom size
  python generate_image.py "A wide landscape" --size 1792x1024

  # Fast generation (lower quality)
  python generate_image.py "Quick sketch" --quality low

Sizes: 1024x1024 (default), 1792x1024, 1024x1792, 2560x1440, 3840x2160

Authentication is automatic via `~/.future/agent/auth.json`.
No API key needed.
        """
    )

    parser.add_argument(
        "prompt",
        type=str,
        help="Text description of the image to generate, or editing instructions"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default="generated_image.png",
        help="Output file path (default: generated_image.png)"
    )

    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input image path for editing (enables edit mode)"
    )

    parser.add_argument(
        "--size", "-s",
        type=str,
        default="1024x1024",
        choices=["1024x1024", "1792x1024", "1024x1792", "2560x1440", "3840x2160"],
        help="Image size (default: 1024x1024)"
    )

    parser.add_argument(
        "--quality", "-q",
        type=str,
        default="high",
        choices=["low", "medium", "high"],
        help="Image quality (default: high)"
    )

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output_path=args.output,
        size=args.size,
        quality=args.quality,
        input_image=args.input
    )


if __name__ == "__main__":
    main()
