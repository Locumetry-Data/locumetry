"""Run a site-selection screen and write the result to CSV, one row per district with the scores you asked for.

    LOCUMETRY_API_KEY=... python examples/screen_to_csv.py shortlist.csv

Edit CRITERIA to taste. Thresholds are national percentiles; labels are listed by /labels.
"""

import csv
import os
import sys

import requests

BASE = "https://locumetry.com/api/v1"
KEY = os.environ.get("LOCUMETRY_API_KEY") or sys.exit("set LOCUMETRY_API_KEY first")
OUT = sys.argv[1] if len(sys.argv) > 1 else "shortlist.csv"

CRITERIA = {
    "min_score": ["affluence_score:60", "economic_momentum_score:50"],
    "max_score": ["commercial_saturation_score:60"],
    "without_label": ["declining_area"],
    "min_population": 50000,
    "sort": "commercial_opportunity_score",
    "limit": 1000,
}

rows = requests.get(f"{BASE}/screen", params=CRITERIA, headers={"X-API-Key": KEY}, timeout=60)
rows.raise_for_status()
rows = rows.json()

score_ids = sorted({sid for r in rows for sid in r["scores"]})
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["geo_id", "district", "province", "population", "labels"] + [f"{s}_pct" for s in score_ids])
    for r in rows:
        w.writerow([r["geo_id"], r["name"], r["province"], r["population"], " ".join(r["labels"])]
                   + [r["scores"].get(s, {}).get("percentile") for s in score_ids])
print(f"{len(rows)} districts written to {OUT}")
