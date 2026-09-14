#!/bin/sh
# Compatibility entry. Prefer id_resolver.py directly on Windows.
# Gene example: bash id_resolver.sh gene-symbol TP53 --taxon 9606
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$SCRIPT_DIR/id_resolver.py" "$@"
