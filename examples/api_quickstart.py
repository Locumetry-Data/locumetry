"""Four calls against Locumetry's public API.

    LOCUMETRY_API_KEY=... python examples/api_quickstart.py

Every request carries the key in the X-API-Key header. Districts are addressed by geo_id (TR_06_1130 style),
scores by name, score thresholds as national percentiles. The reference with every endpoint and field is at
https://locumetry.com/api/v1/docs; keys are issued by hello@locumetry.com.
"""

import json
import os
import sys

import requests

BASE = "https://locumetry.com/api/v1"
KEY = os.environ.get("LOCUMETRY_API_KEY") or sys.exit("set LOCUMETRY_API_KEY first")

session = requests.Session()
session.headers["X-API-Key"] = KEY


def get(path: str, **params):
    response = session.get(f"{BASE}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


# 1. The districts of a province, by plate code.
ankara = get("/districts", province="TR_06")
print(f"Ankara has {len(ankara)} districts; the first is {ankara[0]['geo_id']}")

# 2. One district: its latest scores, labels and the measured values behind them.
district = get(f"/districts/{ankara[0]['geo_id']}")
print(json.dumps(district, ensure_ascii=False, indent=1)[:600], "...")

# 3. A site-selection screen: affluent and gaining momentum, not yet saturated, in the Aegean (NUTS1 region TR3),
#    sorted by commercial opportunity. Thresholds are national percentiles of district-level scores.
hits = get(
    "/screen",
    min_score=["affluence_score:75", "economic_momentum_score:60"],
    max_score=["commercial_saturation_score:50"],
    region="TR3",
    sort="commercial_opportunity_score",
    limit=10,
)
print("\nAegean screen:")
for row in hits:
    print(" ", row["geo_id"], row.get("name", ""))

# 4. A national ranking on one score.
top = get("/rankings", score="economic_vitality_score", limit=10)
print("\nEconomic vitality, top 10:")
for row in top:
    print(" ", row["geo_id"], row.get("name", ""))

# Remaining calls per minute and the limit are reported by /usage.
print("\nusage:", get("/usage"))
