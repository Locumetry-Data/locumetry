"""Given a district that works for you, list the ten most similar ones outside its province, with the features
where each differs most and the labels they share.

    LOCUMETRY_API_KEY=... python examples/lookalikes.py TR_06_1747
"""

import os
import sys

import requests

BASE = "https://locumetry.com/api/v1"
KEY = os.environ.get("LOCUMETRY_API_KEY") or sys.exit("set LOCUMETRY_API_KEY first")
GEO_ID = sys.argv[1] if len(sys.argv) > 1 else "TR_06_1747"

twins = requests.get(f"{BASE}/districts/{GEO_ID}/similar", params={"limit": 10, "exclude_province": "true"},
                     headers={"X-API-Key": KEY}, timeout=30)
twins.raise_for_status()
for t in twins.json():
    differences = "; ".join(f"{d['feature']} {d['direction']}" for d in t["differences"])
    print(f"{t['rank']:>2}. {t['name']} ({t['province']})  distance {t['distance']:.2f}")
    print(f"    differs: {differences}")
    print(f"    shares:  {', '.join(t['shared_labels']) or 'no labels'}")
