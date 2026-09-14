#!/usr/bin/env python3
"""Compatibility entry for the retired generator; never invokes paid tools."""
import sys

from generate_schematic_ai import main


if __name__ == "__main__":
    sys.exit(main())
