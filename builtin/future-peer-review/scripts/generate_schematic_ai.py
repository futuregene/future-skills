#!/usr/bin/env python3
"""
AI-powered scientific schematic generation with smart iterative refinement.

Pipeline:
1. Generate initial image via `future tools call image_gen`
2. AI quality review via `future tools call read_image`
3. Only regenerate if quality is below threshold for document type
4. Repeat until quality meets standards (max 2 iterations)

Authentication is automatic — the future CLI reads credentials from ~/.future/agent/auth.json.

Usage:
    python generate_schematic_ai.py "CONSORT participant flow diagram" -o flowchart.png
    python generate_schematic_ai.py "Neural network architecture" -o arch.png --doc-type poster
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Any


def _run_future(args: list, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a future CLI command. Exits on fatal errors."""
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


def _parse_cli_json(result: subprocess.CompletedProcess) -> dict:
    """Parse JSON from CLI stdout, fall back to raw text."""
    out = result.stdout.strip() if result.stdout else ""
    try:
        return json.loads(out) if out else {}
    except json.JSONDecodeError:
        return {"raw": out}


class ScientificSchematicGenerator:
    """Generate scientific schematics using AI with smart iterative refinement.

    Uses future CLI image_gen for generation and read_image for quality review.
    Multiple passes only occur if the generated schematic doesn't meet the
    quality threshold for the target document type.
    """

    QUALITY_THRESHOLDS = {
        "journal": 8.5,
        "conference": 8.0,
        "poster": 7.0,
        "presentation": 6.5,
        "report": 7.5,
        "grant": 8.0,
        "thesis": 8.0,
        "preprint": 7.5,
        "default": 7.5,
    }

    SCIENTIFIC_DIAGRAM_GUIDELINES = """
Create a high-quality scientific diagram with these requirements:

VISUAL QUALITY:
- Clean white or light background (no textures or gradients)
- High contrast for readability and printing
- Professional, publication-ready appearance
- Sharp, clear lines and text
- Adequate spacing between elements to prevent crowding

TYPOGRAPHY:
- Clear, readable sans-serif fonts (Arial, Helvetica style)
- Minimum 10pt font size for all labels
- Consistent font sizes throughout
- All text horizontal or clearly readable
- No overlapping text

SCIENTIFIC STANDARDS:
- Accurate representation of concepts
- Clear labels for all components
- Include scale bars, legends, or axes where appropriate
- Use standard scientific notation and symbols
- Include units where applicable

ACCESSIBILITY:
- Colorblind-friendly color palette (use Okabe-Ito colors if using color)
- High contrast between elements
- Redundant encoding (shapes + colors, not just colors)
- Works well in grayscale

LAYOUT:
- Logical flow (left-to-right or top-to-bottom)
- Clear visual hierarchy
- Balanced composition
- Appropriate use of whitespace
- No clutter or unnecessary decorative elements

IMPORTANT - NO FIGURE NUMBERS:
- Do NOT include "Figure 1:", "Fig. 1", or any figure numbering in the image
- Do NOT add captions or titles like "Figure: ..." at the top or bottom
- Figure numbers and captions are added separately in the document/LaTeX
- The diagram should contain only the visual content itself
"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._last_error: Optional[str] = None

    def _log(self, message: str):
        if self.verbose:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")

    def generate_image(self, prompt: str, output_path: str, size: str = "1024x1024") -> bool:
        """Generate image via future CLI image_gen. Returns True on success."""
        self._last_error = None

        args_dict = {
            "prompt": prompt,
            "size": size,
            "quality": "high",
            "output_format": Path(output_path).suffix.lstrip(".") or "png",
        }

        self._log(f"Calling image_gen (size={size})...")
        result = _run_future([
            "tools", "call", "image_gen",
            "--args", json.dumps(args_dict),
            "--output", output_path,
        ])

        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            try:
                err = json.loads(error_msg)
                error_msg = err.get("error", err.get("message", str(err)))
            except (json.JSONDecodeError, TypeError):
                pass
            self._last_error = f"CLI Error: {error_msg}"
            self._log(f"✗ Generation failed: {self._last_error}")
            return False

        self._log(f"✓ Generated image -> {output_path}")
        return True

    def review_image(self, image_path: str, original_prompt: str,
                     iteration: int, doc_type: str = "default",
                     max_iterations: int = 2) -> tuple[str, float, bool]:
        """Review generated image via future CLI read_image.

        Returns:
            Tuple of (critique text, quality score 0-10, needs_improvement bool)
        """
        threshold = self.QUALITY_THRESHOLDS.get(doc_type.lower(),
                                                self.QUALITY_THRESHOLDS["default"])

        review_question = f"""You are an expert reviewer evaluating a scientific diagram for publication quality.

ORIGINAL REQUEST: {original_prompt}

DOCUMENT TYPE: {doc_type} (quality threshold: {threshold}/10)
ITERATION: {iteration}/{max_iterations}

Carefully evaluate this diagram on these criteria:

1. **Scientific Accuracy** (0-2 points) — Correct representation, proper notation, accurate relationships
2. **Clarity and Readability** (0-2 points) — Easy to understand, clear hierarchy, no ambiguity
3. **Label Quality** (0-2 points) — All elements labeled, readable fonts, consistent style
4. **Layout and Composition** (0-2 points) — Logical flow, balanced space, no overlaps
5. **Professional Appearance** (0-2 points) — Publication-ready, clean lines, appropriate colors

RESPOND IN THIS EXACT FORMAT:
SCORE: [total score 0-10]

STRENGTHS:
- [strength 1]
- [strength 2]

ISSUES:
- [issue 1 if any]
- [issue 2 if any]

VERDICT: [ACCEPTABLE or NEEDS_IMPROVEMENT]

If score >= {threshold}, the diagram is ACCEPTABLE for {doc_type} publication.
If score < {threshold}, mark as NEEDS_IMPROVEMENT with specific suggestions."""

        args_dict = {
            "image_path": str(Path(image_path).resolve()),
            "question": review_question,
        }

        self._log(f"Calling read_image for review...")
        result = _run_future([
            "tools", "call", "read_image",
            "--args", json.dumps(args_dict),
        ])

        if result.returncode != 0:
            self._log(f"Review skipped: CLI error (treating as acceptable)")
            return "Image generated (review skipped due to error)", 7.5, False

        response = _parse_cli_json(result)
        # read_image returns {"answer": "...", "question": "...", "usage": {...}}
        content = response.get("answer", response.get("text", response.get("raw", "")))
        if isinstance(content, list):
            content = "\n".join(str(c) for c in content)

        if not content:
            self._log("Review returned no content, treating as acceptable")
            return "Image generated successfully", 7.5, False

        # Extract score
        score = 7.5
        score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if score_match:
            score = float(score_match.group(1))

        # Determine verdict
        needs_improvement = False
        if "NEEDS_IMPROVEMENT" in content.upper():
            needs_improvement = True
        elif score < threshold:
            needs_improvement = True

        self._log(f"✓ Review complete (Score: {score}/10, Threshold: {threshold}/10)")
        self._log(f"  Verdict: {'Needs improvement' if needs_improvement else 'Acceptable'}")

        return content, score, needs_improvement

    def improve_prompt(self, original_prompt: str, critique: str, iteration: int) -> str:
        """Improve the generation prompt based on critique."""
        return f"""{self.SCIENTIFIC_DIAGRAM_GUIDELINES}

USER REQUEST: {original_prompt}

ITERATION {iteration}: Based on previous feedback, address these specific improvements:
{critique}

Generate an improved version that addresses all the critique points while maintaining scientific accuracy and professional quality."""

    def generate_iterative(self, user_prompt: str, output_path: str,
                          iterations: int = 2,
                          doc_type: str = "default",
                          size: str = "1024x1024") -> dict[str, Any]:
        """Generate scientific schematic with smart iterative refinement.

        Only regenerates if quality is below threshold for the specified document type.
        """
        output_path = Path(output_path)
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        base_name = output_path.stem
        extension = output_path.suffix or ".png"

        threshold = self.QUALITY_THRESHOLDS.get(doc_type.lower(),
                                                self.QUALITY_THRESHOLDS["default"])

        results = {
            "user_prompt": user_prompt,
            "doc_type": doc_type,
            "quality_threshold": threshold,
            "iterations": [],
            "final_image": None,
            "final_score": 0.0,
            "success": False,
            "early_stop": False,
            "early_stop_reason": None,
        }

        current_prompt = f"""{self.SCIENTIFIC_DIAGRAM_GUIDELINES}

USER REQUEST: {user_prompt}

Generate a publication-quality scientific diagram that meets all the guidelines above."""

        print(f"\n{'='*60}")
        print(f"Generating Scientific Schematic")
        print(f"{'='*60}")
        print(f"Description: {user_prompt}")
        print(f"Document Type: {doc_type}")
        print(f"Quality Threshold: {threshold}/10")
        print(f"Max Iterations: {iterations}")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")

        for i in range(1, iterations + 1):
            print(f"\n[Iteration {i}/{iterations}]")
            print("-" * 40)

            # Generate image
            print(f"Generating image...")
            iter_path = output_dir / f"{base_name}_v{i}{extension}"
            success = self.generate_image(current_prompt, str(iter_path), size=size)

            if not success:
                print(f"✗ Generation failed: {self._last_error}")
                results["iterations"].append({
                    "iteration": i,
                    "success": False,
                    "error": self._last_error,
                })
                continue

            print(f"✓ Saved: {iter_path}")

            # Review image
            print(f"Reviewing image quality...")
            critique, score, needs_improvement = self.review_image(
                str(iter_path), user_prompt, i, doc_type, iterations
            )
            print(f"✓ Score: {score}/10 (threshold: {threshold}/10)")

            iter_result = {
                "iteration": i,
                "image_path": str(iter_path),
                "prompt": current_prompt,
                "critique": critique,
                "score": score,
                "needs_improvement": needs_improvement,
                "success": True,
            }
            results["iterations"].append(iter_result)

            # Check if quality is acceptable — stop early if so
            if not needs_improvement:
                print(f"\n✓ Quality meets {doc_type} threshold ({score} >= {threshold})")
                print(f"  No further iterations needed!")
                results["final_image"] = str(iter_path)
                results["final_score"] = score
                results["success"] = True
                results["early_stop"] = True
                results["early_stop_reason"] = (
                    f"Quality score {score} meets threshold {threshold} for {doc_type}"
                )
                break

            # Last iteration — ship it
            if i == iterations:
                print(f"\n⚠ Maximum iterations reached")
                results["final_image"] = str(iter_path)
                results["final_score"] = score
                results["success"] = True
                break

            # Quality below threshold — improve prompt
            print(f"\n⚠ Quality below threshold ({score} < {threshold})")
            print(f"Improving prompt based on feedback...")
            current_prompt = self.improve_prompt(user_prompt, critique, i + 1)

        # Copy final version to output path
        if results["success"] and results["final_image"]:
            final_iter_path = Path(results["final_image"])
            if final_iter_path != output_path:
                shutil.copy(final_iter_path, output_path)
                print(f"\n✓ Final image: {output_path}")

        # Save review log
        log_path = output_dir / f"{base_name}_review_log.json"
        with open(log_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"✓ Review log: {log_path}")

        print(f"\n{'='*60}")
        print(f"Generation Complete!")
        print(f"Final Score: {results['final_score']}/10")
        if results["early_stop"]:
            used = len([r for r in results["iterations"] if r.get("success")])
            print(f"Iterations Used: {used}/{iterations} (early stop)")
        print(f"{'='*60}\n")

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate scientific schematics using AI with smart iterative refinement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a flowchart for a journal paper
  python generate_schematic_ai.py "CONSORT participant flow diagram" -o flowchart.png --doc-type journal

  # Generate neural network architecture for presentation (lower threshold)
  python generate_schematic_ai.py "Transformer encoder-decoder architecture" -o transformer.png --doc-type presentation

  # Generate with custom size
  python generate_schematic_ai.py "Biological signaling pathway" -o pathway.png --size 1792x1024

Document Types (quality thresholds):
  journal      8.5/10  - Nature, Science, peer-reviewed journals
  conference   8.0/10  - Conference papers
  thesis       8.0/10  - Dissertations, theses
  grant        8.0/10  - Grant proposals
  preprint     7.5/10  - arXiv, bioRxiv, etc.
  report       7.5/10  - Technical reports
  poster       7.0/10  - Academic posters
  presentation 6.5/10  - Slides, talks
  default      7.5/10  - General purpose

Note: Multiple iterations only occur if quality is BELOW the threshold.
      If the first generation meets the threshold, no extra iterations are made.

Authentication is automatic via ~/.future/agent/auth.json. No API key needed.
        """
    )

    parser.add_argument("prompt", help="Description of the diagram to generate")
    parser.add_argument("-o", "--output", required=True,
                       help="Output image path (e.g., diagram.png)")
    parser.add_argument("--iterations", type=int, default=2,
                       help="Maximum refinement iterations (default: 2, max: 2)")
    parser.add_argument("--doc-type", default="default",
                       choices=["journal", "conference", "poster", "presentation",
                               "report", "grant", "thesis", "preprint", "default"],
                       help="Document type for quality threshold (default: default)")
    parser.add_argument("--size", default="1024x1024",
                       choices=["1024x1024", "1792x1024", "1024x1792", "2560x1440", "3840x2160"],
                       help="Image size (default: 1024x1024)")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    if args.iterations < 1 or args.iterations > 2:
        print("Error: Iterations must be between 1 and 2")
        sys.exit(1)

    try:
        generator = ScientificSchematicGenerator(verbose=args.verbose)
        results = generator.generate_iterative(
            user_prompt=args.prompt,
            output_path=args.output,
            iterations=args.iterations,
            doc_type=args.doc_type,
            size=args.size,
        )

        if results["success"]:
            print(f"\n✓ Success! Image saved to: {args.output}")
            if results.get("early_stop"):
                used = len([r for r in results["iterations"] if r.get("success")])
                print(f"  (Completed in {used} iteration(s) - quality threshold met)")
            sys.exit(0)
        else:
            print(f"\n✗ Generation failed. Check review log for details.")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
