#!/bin/bash
# Rate-limited API caller for NCBI E-utilities (and other rate-limited services)
# Usage: bash rate_limiter.sh <service> <curl_args...>
#
# Services:
#   ncbi       — NCBI E-utilities (3 req/sec without key, 10 req/sec with key)
#   ncbi-key   — NCBI E-utilities with API key
#   ensembl    — Ensembl REST (15 req/sec)
#   noaa       — NOAA CDO (5 req/sec with token)
#   sec-edgar  — SEC EDGAR (10 req/sec)
#
# Example:
#   bash rate_limiter.sh ncbi -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=TP53&retmode=json"

set -eu

SERVICE="${1:-}"
shift || true

if [ -z "$SERVICE" ]; then
    echo "Usage: rate_limiter.sh <service> <curl_args...>"
    echo "Services: ncbi, ncbi-key, ensembl, noaa, sec-edgar"
    exit 1
fi

# Delay between requests in seconds
case "$SERVICE" in
    ncbi)       DELAY=0.35 ;;  # ~3 req/sec
    ncbi-key)   DELAY=0.10 ;;  # ~10 req/sec
    ensembl)    DELAY=0.07 ;;  # ~15 req/sec
    noaa)       DELAY=0.20 ;;  # ~5 req/sec
    sec-edgar)  DELAY=0.10 ;;  # ~10 req/sec
    *)
        echo "Unknown service: $SERVICE"
        echo "Valid: ncbi, ncbi-key, ensembl, noaa, sec-edgar"
        exit 1
        ;;
esac

# Add a small random jitter (±20%) to avoid thundering herd
JITTER=$(python3 -c "import random; print(random.uniform(-0.2, 0.2) * $DELAY)")
SLEEP_TIME=$(python3 -c "print(max(0.05, $DELAY + $JITTER))")

sleep "$SLEEP_TIME"
curl -s "$@"
