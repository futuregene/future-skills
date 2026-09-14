#!/bin/bash
# Sequential request pacer, NOT a cross-process/global rate limiter.
# Use only in one sequential caller; parallel callers need a shared limiter.
# Requires a POSIX shell, Python 3 and curl (not native PowerShell).
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
if [ "$#" -gt 0 ]; then shift; fi

if [ -z "$SERVICE" ] || [ "$#" -eq 0 ]; then
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

# Positive-only jitter: never shorten the minimum service interval.
SLEEP_TIME=$(python3 -c "import random; print($DELAY * random.uniform(1.0, 1.2))")

sleep "$SLEEP_TIME"
# Preserve HTTP/transport failure status and bound a stalled request.
# No automatic retries: the caller owns retry and aggregate request budgets.
curl --silent --show-error --fail --connect-timeout 10 --max-time 30 "$@"
