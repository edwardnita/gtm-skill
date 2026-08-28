#!/usr/bin/env node
// Fetches EU public-tender evidence from the official TED API (no key needed) and
// computes the deterministic market-entry signal sub-scores used by $tender-demand-scan.
// Zero dependencies. Node >= 18 (built-in fetch).
//
// Usage: node ted-fetch.mjs --cpv 72000000[,72200000] --country ROU [--months 12]
// Prints one JSON document to stdout. Exits 1 with a plain error line on failure.

const API = "https://api.ted.europa.eu/v3/notices/search";

function arg(name, fallback = null) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const cpvs = (arg("cpv") ?? "").split(",").map((s) => s.trim()).filter(Boolean);
const country = (arg("country") ?? "").trim().toUpperCase();
const months = Number(arg("months") ?? 12);

if (cpvs.length === 0 || !/^[A-Z]{3}$/.test(country)) {
  console.error("usage: node ted-fetch.mjs --cpv <code[,code]> --country <ISO3, e.g. ROU> [--months 12]");
  process.exit(1);
}

const since = new Date();
since.setMonth(since.getMonth() - months);
const sinceStr = since.toISOString().slice(0, 10).replaceAll("-", "");

// Pick a readable string out of TED's {lang: [values]} maps. Prefer English, then Romanian.
function text(v) {
  if (v == null) return null;
  if (typeof v === "string") return v;
  if (Array.isArray(v)) return v[0] ?? null;
  const langs = ["eng", "ron", ...Object.keys(v)];
  for (const l of langs) {
    const x = v[l];
    if (typeof x === "string" && x) return x;
    if (Array.isArray(x) && x.length) return x[0];
  }
  return null;
}

async function search(extra, fields, limit) {
  const query =
    `(classification-cpv IN (${cpvs.join(" ")})) AND (place-of-performance IN (${country}))` +
    ` AND (publication-date>=${sinceStr})${extra} SORT BY publication-date DESC`;
  let lastErr;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, fields, limit }),
      });
      if (!res.ok) throw new Error(`TED API returned HTTP ${res.status}`);
      return await res.json();
    } catch (e) {
      lastErr = e;
      if (attempt < 3) await new Promise((r) => setTimeout(r, attempt * 700));
    }
  }
  throw lastErr;
}

function band(value, steps) {
  // steps: [[min, points], ...] evaluated from highest min down
  for (const [min, pts] of steps) if (value >= min) return pts;
  return 0;
}

try {
  const retrievedAt = new Date().toISOString();

  const demand = await search(" AND (notice-type IN (cn-standard cn-social cn-desg))",
    ["publication-number", "notice-title", "buyer-name", "publication-date"], 20);
  const awards = await search(" AND (notice-type IN (can-standard can-social can-desg))",
    ["publication-number", "notice-title", "buyer-name", "winner-name", "total-value", "total-value-cur", "publication-date"], 100);

  const demandCount = demand.totalNoticeCount ?? 0;
  const awardCount = awards.totalNoticeCount ?? 0;
  const awardSample = awards.notices ?? [];

  // Winners: count notices won per company (deduped per notice — multi-lot awards repeat names).
  const winners = new Map();
  const buyers = new Map();
  const valueByCurrency = {};
  for (const n of awardSample) {
    const buyer = text(n["buyer-name"]);
    if (buyer) buyers.set(buyer, (buyers.get(buyer) ?? 0) + 1);
    const names = new Set((Object.values(n["winner-name"] ?? {}).flat() ?? []).map((s) => s.trim()).filter(Boolean));
    for (const w of names) winners.set(w, (winners.get(w) ?? 0) + 1);
    const cur = (n["total-value-cur"] ?? [])[0];
    const val = Number(n["total-value"]);
    if (cur && Number.isFinite(val)) valueByCurrency[cur] = (valueByCurrency[cur] ?? 0) + val;
  }
  const topWinners = [...winners.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([name, wonNotices]) => ({ name, wonNotices }));
  const topBuyers = [...buyers.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([name, notices]) => ({ name, notices }));

  const recent = (demand.notices ?? []).slice(0, 3).map((n) => ({
    number: n["publication-number"],
    title: text(n["notice-title"]),
    buyer: text(n["buyer-name"]),
    date: String(n["publication-date"] ?? "").slice(0, 10),
    url: `https://ted.europa.eu/en/notice/${n["publication-number"]}`,
  }));

  const latest = recent[0]?.date ? new Date(recent[0].date) : null;
  const daysSinceLatest = latest ? Math.round((Date.now() - latest.getTime()) / 86400000) : null;
  const topShare = awardSample.length && topWinners[0] ? topWinners[0].wonNotices / awardSample.length : null;

  // Deterministic 0-100 heuristic: four sub-scores of 25. Bands are stated, not tuned.
  const score = {
    demand_volume: band(demandCount, [[200, 25], [50, 18], [10, 12], [1, 6]]),
    buyer_diversity: band(buyers.size, [[25, 25], [10, 18], [2, 10], [1, 5]]),
    winner_openness: topShare == null ? 0 : band(1 - topShare, [[0.75, 25], [0.5, 18], [0.25, 10], [0, 5]]),
    recency: daysSinceLatest == null ? 0 : band(-daysSinceLatest, [[-30, 25], [-60, 18], [-180, 12], [-99999, 5]]),
  };
  score.total = score.demand_volume + score.buyer_diversity + score.winner_openness + score.recency;

  console.log(JSON.stringify({
    meta: {
      source: "TED — Tenders Electronic Daily (official EU procurement journal)",
      api: API,
      cpv: cpvs, country, window_months: months, since: sinceStr,
      retrieved_at: retrievedAt,
      note: "Live API data at retrieval time. Award sample capped at 100 most recent notices.",
    },
    demand: { contract_notices: demandCount, days_since_latest: daysSinceLatest, recent_examples: recent },
    awards: {
      award_notices: awardCount, sample_size: awardSample.length,
      distinct_buyers_in_sample: buyers.size, top_buyers: topBuyers,
      top_winners: topWinners, awarded_value_by_currency_in_sample: valueByCurrency,
    },
    score,
    score_bands: {
      demand_volume: "contract notices in window: 0=0, 1-9=6, 10-49=12, 50-199=18, 200+=25",
      buyer_diversity: "distinct buyers in award sample: 0=0, 1=5, 2-9=10, 10-24=18, 25+=25",
      winner_openness: "top winner share of sampled awards: no awards=0, >75%=5, 50-75%=10, 25-50%=18, <25%=25",
      recency: "days since latest contract notice: none=0, >180=5, 61-180=12, 31-60=18, <=30=25",
    },
  }, null, 2));
} catch (e) {
  console.error(`ERROR: ${e.message}. TED API may be unreachable; do not invent results — use the committed fallback and say so.`);
  process.exit(1);
}
