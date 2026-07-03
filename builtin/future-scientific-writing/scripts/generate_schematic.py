#!/usr/bin/env python3
"""
Scientific schematic generation using AI with smart iterative refinement.

Generate any scientific diagram by describing it in natural language.
Uses future CLI image_gen for generation and read_image for quality review.

Smart iteration: Only regenerates if quality is below threshold for your document type.

Authentication is automatic via ~/.future/agent/auth.json. No API key needed.

Usage:
    # Generate for journal paper (highest quality threshold)
    python generate_schematic.py "CONSORT flowchart" -o flowchart.png --doc-type journal

    # Generate for presentation (lower threshold, faster)
    python generate_schematic.py "Transformer architecture" -o transformer.png --doc-type presentation

    # Generate for poster
    python generate_schematic.py "MAPK signaling pathway" -o pathway.png --doc-type poster
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Command-line interface — thin wrapper around generate_schematic_ai.py."""
    script_dir = Path(__file__).parent
    ai_script = script_dir / "generate_schematic_ai.py"

    if not ai_script.exists():
        print(f"Error: AI generation script not found: {ai_script}")
        sys.exit(1)

    # Passthrough all arguments to the AI script
    cmd = [sys.executable, str(ai_script)] + sys.argv[1:]
    result = subprocess.run(cmd, check=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
