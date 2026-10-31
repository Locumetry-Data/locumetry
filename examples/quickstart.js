// Node 18+ or any modern browser runtime: a district, a screen and a ranking.
//   LOCUMETRY_API_KEY=... node examples/quickstart.js
const BASE = "https://locumetry.com/api/v1";
const KEY = process.env.LOCUMETRY_API_KEY;
if (!KEY) throw new Error("set LOCUMETRY_API_KEY first");

async function get(path, params = {}) {
  const url = new URL(BASE + path);
  for (const [k, v] of Object.entries(params)) {
    for (const item of Array.isArray(v) ? v : [v]) url.searchParams.append(k, item);
  }
  const res = await fetch(url, { headers: { "X-API-Key": KEY } });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

const sincan = await get("/districts/TR_06_1747");
console.log(sincan.geo.name, "affluence percentile", sincan.scores.affluence_score.percentile.toFixed(1));
console.log("labels:", sincan.labels.map((l) => l.label).join(", "));

const hits = await get("/screen", {
  min_score: ["affluence_score:75", "economic_momentum_score:60"],
  max_score: ["commercial_saturation_score:60"],
  min_population: 100000,
  sort: "commercial_opportunity_score",
  limit: 10,
});
console.log(`\nscreen: ${hits.length} districts`);
for (const d of hits) console.log(" ", d.name, d.province, d.scores.commercial_opportunity_score.percentile);

const top = await get("/rankings", { score: "economic_vitality_score", limit: 5 });
console.log("\neconomic vitality, top 5:", top.map((r) => `${r.name} (${r.province})`).join(", "));
