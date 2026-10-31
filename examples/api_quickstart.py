"""Five calls against Locumetry's public API.

    LOCUMETRY_API_KEY=... python examples/api_quickstart.py

Every request carries the key in the X-API-Key header. Districts are addressed by geo_id (TR_06_1747 is Sincan),
scores by name, score thresholds as national percentiles. The guide with every endpoint and real responses is at
https://locumetry-data.github.io/locumetry/ and the OpenAPI reference at https://locumetry.com/api/v1/docs.
Get a sandbox key at https://locumetry.com/partners#sandbox.
"""

import os
import sys

import requests

BASE = "https://locumetry.com/api/v1"
KEY = os.environ.get("LOCUMETRY_API_KEY") or sys.exit("set LOCUMETRY_API_KEY first")

api = requests.Session()
api.headers["X-API-Key"] = KEY


def get(path: str, **params):
    response = api.get(f"{BASE}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


# 1. The districts of a province, by plate code; or find one by name.
ankara = get("/districts", province="TR_06")
sincan = get("/districts", q="sincan")[0]
print(f"Ankara has {len(ankara)} districts; Sincan is {sincan['geo_id']}")

# 2. One district: its latest scores, labels and the measured values behind them.
d = get(f"/districts/{sincan['geo_id']}")
pop = d["features"]["population"]
print(f"\n{d['geo']['name']}: population {pop['value']:,.0f} ({pop['year']})")
for score_id, s in sorted(d["scores"].items()):
    if s["level"] == "district":
        print(f"  {score_id:<40} percentile {s['percentile']:5.1f}  rank {s['rank_national']}")
print("  labels:", ", ".join(label["label"] for label in d["labels"]))

# 3. A site-selection screen: affluent and gaining momentum, not yet saturated, at least 100,000 residents,
#    sorted by commercial opportunity. Thresholds are national percentiles of district-level scores.
hits = get(
    "/screen",
    min_score=["affluence_score:75", "economic_momentum_score:60"],
    max_score=["commercial_saturation_score:60"],
    min_population=100000,
    sort="commercial_opportunity_score",
    limit=10,
)
print(f"\nScreen: {len(hits)} districts")
for row in hits:
    opp = row["scores"]["commercial_opportunity_score"]["percentile"]
    print(f"  {row['name']:<14} {row['province']:<12} opportunity {opp:5.1f}  {', '.join(row['labels'][:3])}")

# 4. A regional ranking on one score: the Aegean (NUTS1 region TR3).
top = get("/rankings", score="commercial_opportunity_score", region="TR3", limit=5)
print("\nAegean, commercial opportunity:")
for row in top:
    print(f"  {row['rank_region']:>2}. {row['name']:<14} {row['province']:<10} national rank {row['rank_national']}")

# 5. Your own meter: requests per day and route.
print("\nusage today:", sum(u["requests"] for u in get("/usage", days=1)), "requests")
