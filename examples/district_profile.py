"""Print a one-page profile of a district: scores, labels with evidence, key features and five-year history.

    LOCUMETRY_API_KEY=... python examples/district_profile.py TR_06_1747
"""

import os
import sys

import requests

BASE = "https://locumetry.com/api/v1"
KEY = os.environ.get("LOCUMETRY_API_KEY") or sys.exit("set LOCUMETRY_API_KEY first")
GEO_ID = sys.argv[1] if len(sys.argv) > 1 else "TR_06_1747"
KEY_FEATURES = ["population", "population_growth_3y", "population_density", "workplaces_per_1000",
                "commercial_poi_density", "avg_daily_earning", "deposits_per_capita", "population_per_pharmacy"]

api = requests.Session()
api.headers["X-API-Key"] = KEY
catalog = {f["feature_id"]: f for f in api.get(f"{BASE}/catalog/features", timeout=60).json()}
d = api.get(f"{BASE}/districts/{GEO_ID}", timeout=30).json()
history = api.get(f"{BASE}/districts/{GEO_ID}/history", params={"feature": KEY_FEATURES}, timeout=30).json()

geo = d["geo"]
print(f"{geo['name']} ({geo['geo_id']}), {geo['area_km2']:,.0f} km², region {geo['region_code']}")

print("\nScores (national percentile, rank)")
for score_id, s in sorted(d["scores"].items(), key=lambda kv: -kv[1]["percentile"]):
    scope = "" if s["level"] == "district" else "  (province-level)"
    print(f"  {score_id:<40} {s['percentile']:5.1f}  #{s['rank_national']}{scope}")

print("\nLabels")
for label in d["labels"]:
    evidence = ", ".join(f"{k}={v:g}" for k, v in (label["evidence"] or {}).items())
    print(f"  {label['label']}: {label['description']}  [{evidence}]")

print("\nKey features (latest)")
for fid in KEY_FEATURES:
    f = d["features"].get(fid)
    if not f:
        continue
    meta = catalog.get(fid, {})
    flag = "  (estimate)" if f["is_estimated"] else ""
    print(f"  {meta.get('display_name', fid):<42} {f['value']:>14,.3f} {meta.get('unit', ''):<10} {f['year']}{flag}")

print("\nHistory (last five values)")
for fid, series in history.items():
    points = ", ".join(f"{p['year']}: {p['value']:,.3f}" for p in series[-5:])
    print(f"  {catalog.get(fid, {}).get('display_name', fid)}: {points}")
