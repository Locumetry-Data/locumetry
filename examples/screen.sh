#!/usr/bin/env bash
# The same site-selection screen as api_quickstart.py, from the shell.
#   LOCUMETRY_API_KEY=... ./examples/screen.sh
set -euo pipefail
: "${LOCUMETRY_API_KEY:?set LOCUMETRY_API_KEY first}"
curl -sS -G "https://locumetry.com/api/v1/screen" \
  -H "X-API-Key: $LOCUMETRY_API_KEY" \
  --data-urlencode "min_score=affluence_score:75" \
  --data-urlencode "min_score=economic_momentum_score:60" \
  --data-urlencode "max_score=commercial_saturation_score:50" \
  --data-urlencode "region=TR3" \
  --data-urlencode "sort=commercial_opportunity_score" \
  --data-urlencode "limit=10" | python3 -m json.tool
