#!/usr/bin/env python3
"""Retired legacy diagram generator: fail closed without remote calls.

Scientific peer review does not require generating diagrams. For an explicitly
requested illustration, use future-image's current CLI, upload, verification and
paid-retry contract. A model-assigned quality score is not scientific validation.
"""
import sys


def main():
    print(
        "This legacy generator is retired. No image was generated or reviewed. "
        "Use the future-image skill for an authorized illustration request; "
        "peer review itself does not require image generation. "
        "Do not retry the former score-based auto-refinement workflow.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
