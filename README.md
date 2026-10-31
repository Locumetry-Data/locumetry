<p align="center"><img src="https://locumetry.com/static/icon-512.png" width="72" alt=""></p>
<h1 align="center">Locumetry</h1>
<p align="center">District-level economic and location intelligence for Türkiye.<br>
<a href="https://locumetry.com">locumetry.com</a> · <a href="https://locumetry-data.github.io/locumetry/">API guide</a> · <a href="https://locumetry.com/api/v1/docs">OpenAPI reference</a> · <a href="https://locumetry.com/methodology">Methodology</a> · <a href="https://locumetry.com/pricing">Pricing</a></p>

Locumetry answers one question for people who choose places: **which districts of Türkiye fit, and why.**
It covers all 973 districts in 81 provinces on one consistent boundary set, with more than 1.2 million
observations going back to 2000, and turns them into scores, labels and evidence that can be compared,
screened and exported.

This repository is the public home of the product: what it is, how it works, how to use the API, and where to
report problems. The service itself runs at [locumetry.com](https://locumetry.com); the
[API guide](https://locumetry-data.github.io/locumetry/) documents every endpoint with real responses and recipes.

## What you get

- **District and province profiles.** Population and its change, age structure, income proxies, employment,
  business openings and closures, credit, tourism, industry, housing, and the places on the ground (shops,
  cafés, clinics, gyms, schools, transport), each with its period and source.
- **Scores.** Economic vitality, affluence, commercial saturation, economic momentum, industrial opportunity,
  household demand growth, financial services opportunity and underserved demand (`commercial_opportunity_score`,
  a volume reading: many, dense and growing residents against few shops per resident), plus category
  opportunity scores for gyms, pharmacies, supermarkets and EV chargers. Every score is published as a national
  percentile and rank, with the measured features behind it.
- **Labels.** Plain-language flags such as growing, affluent or underserved in a category, derived from the
  same features by fixed rules.
- **Comparison and screening.** Put districts side by side, or ask for every district that is, say, above the
  75th percentile on affluence, gaining momentum and not yet saturated, in a region of your choice. Nine curated
  comparisons (İstanbul's two sides, Ankara, İzmir, the coasts, the Kocaeli industrial belt) are kept current nightly.
- **History.** Scores and features over time, so a district can be judged on its trajectory, not a snapshot.
- **Readings.** A short generated summary on every district and province page, in English and Turkish, written
  from that place's own numbers and checked against them before it is shown. Rewritten only when the numbers change.
- **An API.** Everything above as JSON, keyed by stable district identifiers, for your own models, maps and
  reports.

Typical users are retail and food-service chains planning expansion, franchise networks, real-estate teams,
market researchers and analysts who need Turkish regional data in one consistent shape.

## How it works

1. **Collect.** Official statistics and open map data are downloaded exactly as published and kept, so every
   number can be traced to the file it came from. Publishers' revisions are stored as new versions, never
   overwritten.
2. **Align.** Everything is keyed to one geography: `TR_34` is a province (plate code), `TR_34_1421` a district
   (TÜİK code), `TR_34_1421_<id>` a neighbourhood. Names are matched Turkish-aware and never used as keys.
3. **Measure.** Features are computed only where the source actually measures that geography. Values that had
   to be allocated or modelled are flagged as estimates and shown as such, and they enter a score at a quarter of
   the weight of a measured value, so a district never inherits its province's wealth wholesale.
4. **Score.** Features are combined into scores and expressed as national percentiles, so a 90 means "higher
   than 90 percent of districts". The methodology page explains what goes into each score and how to read it.
5. **Publish.** The site, the comparison and screening tools, the reports and the API read from the same
   nightly build.

The methodology is described in full at [locumetry.com/methodology](https://locumetry.com/methodology).

## Sources

| Source | What | Level | Cadence |
|---|---|---|---|
| TÜİK | population, age groups, GDP, vehicles, marriages, housing sales, neighbourhood population | district, province, neighbourhood | yearly, some monthly |
| BDDK FinTürk | deposits, loans, non-performing loans, branches, by bank group | province | quarterly |
| TBB | bank branches and ATMs | province | yearly |
| TCMB EVDS | macro series, housing price index, policy rate | national, NUTS2 | daily to monthly |
| SGK | workplaces, insured employees, earnings | province | monthly |
| TOBB | companies founded and closed; industrial capacity | province | monthly, yearly |
| KTB | licensed tourism facilities and beds | province | monthly |
| OSBÜK | organised industrial zones | district | snapshot |
| geoBoundaries | province and district boundaries | province, district | static |
| OpenStreetMap | places, infrastructure, roads and rail | point | monthly |
| Overture Maps | places | point | monthly |
| Foursquare OS Places | places | point | monthly |

Three map sources are mapped onto one category vocabulary so that counts line up district by district; every
snapshot is kept with its date, so openings and closures can be followed over time.

## Using the API

Every request carries your key in the `X-API-Key` header. Keys are issued with a plan from the
[pricing page](https://locumetry.com/pricing); write to hello@locumetry.com for an evaluation key.

```bash
curl -s https://locumetry.com/api/v1/districts/TR_06_1747 -H "X-API-Key: $LOCUMETRY_API_KEY"
```

```python
import requests

api = requests.Session()
api.headers["X-API-Key"] = "your key"

# Affluent, gaining momentum, not yet saturated, at least 100,000 residents; thresholds are national percentiles
hits = api.get("https://locumetry.com/api/v1/screen", params={
    "min_score": ["affluence_score:75", "economic_momentum_score:60"],
    "max_score": ["commercial_saturation_score:60"],
    "min_population": 100000,
    "sort": "commercial_opportunity_score",
    "limit": 10,
}).json()
for row in hits:
    print(row["geo_id"], row["name"], row["province"], row["scores"]["commercial_opportunity_score"]["percentile"])
# TR_41_2059 Çayırova Kocaeli 99.9
# TR_34_2048 Arnavutköy İstanbul 99.6
# ...
```

| Endpoint | Returns |
|---|---|
| `/districts`, `/provinces` | the geography, filterable by province or name |
| `/districts/{geo_id}` | one district: latest scores with their inputs, labels with evidence, every measured feature, the generated reading |
| `/districts/{geo_id}/history` | a district's features by year |
| `/districts/{geo_id}/observations` | the publisher's raw numbers behind the features, with period, unit and source |
| `/districts/{geo_id}/similar` | the districts that look most like it, and where they differ |
| `/screen` | districts matching label and percentile conditions, sorted by a score |
| `/rankings`, `/features` | national or regional ranking on one score, or on one measured feature |
| `/scores/history` | a district's scores by year |
| `/labels`, `/scores`, `/catalog/features`, `/metrics` | the catalogues: what each label, score, feature and metric means |
| `/neighborhoods`, `/h3` | neighbourhood population; a district as a hexagon grid with population and distances |
| `/usage`, `/health` | your meter; the service's state |

The [API guide](https://locumetry-data.github.io/locumetry/) shows each endpoint with a real response and the
parameters it takes; the [OpenAPI reference](https://locumetry.com/api/v1/docs) is generated from the service.

### Examples

| Script | What it does |
|---|---|
| [`examples/api_quickstart.py`](examples/api_quickstart.py) | find a district, read its profile, run a screen, read a ranking, check your meter |
| [`examples/district_profile.py`](examples/district_profile.py) | a one-page profile: scores, labels with evidence, key features, five-year history |
| [`examples/screen_to_csv.py`](examples/screen_to_csv.py) | run a screen and write the shortlist to CSV |
| [`examples/lookalikes.py`](examples/lookalikes.py) | the ten districts most like a given one, outside its province |
| [`examples/quickstart.js`](examples/quickstart.js) | the same first steps in JavaScript (Node 18+) |
| [`examples/screen.sh`](examples/screen.sh) | the screen with `curl` |

```bash
pip install -r examples/requirements.txt
LOCUMETRY_API_KEY=... python examples/api_quickstart.py
```

## Reading the numbers

- A score is a **national percentile** among districts (or among provinces for province-level scores); it says
  where a place stands, not how big it is.
- Every value carries its **period**: the first day of the year, quarter or month it describes.
- **Estimated** values, where a national or provincial figure had to be allocated to a district, are marked.
  Measured values are shown separately from estimates on the site and in the API.
- Locumetry is **information, not advice**. It is built to make a shortlist defensible, not to replace a visit.

## Issues and contact

Found a wrong figure, a district that does not match its boundary, or an API response that does not do what the
reference says? [Open an issue](https://github.com/Locumetry-Data/locumetry/issues). For plans, keys and
everything else: hello@locumetry.com.

## Licence

The examples in this repository are MIT licensed. The data and the service are provided under Locumetry's
[terms](https://locumetry.com/terms); source data remains under each publisher's terms, listed on the
methodology page.
