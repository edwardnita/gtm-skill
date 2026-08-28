#!/usr/bin/env node
// Fetches EU public-tender evidence from the official TED API (no key needed) and
// computes the deterministic market-entry signal sub-scores used by $tender-demand-scan.
// Zero dependencies. Node >= 18 (built-in fetch).
//
// Usage: node ted-fetch.mjs --cpv 72000000[,72200000] --country ROU [--months 12]
//          [--report report.html --product "label" [--country-name "Romania"] [--mapping "how CPV was chosen"]]
// Prints one JSON document to stdout. With --report it ALSO renders references/report-template.html
// deterministically into the given path — no LLM writes any HTML. Exits 1 with a plain error line on failure.

import { fileURLToPath } from "node:url";
import { readFileSync as readFile, writeFileSync } from "node:fs";
import { dirname as dirName, join as joinPath } from "node:path";

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

const EU27 = { AUT: "Austria", BEL: "Belgium", BGR: "Bulgaria", HRV: "Croatia", CYP: "Cyprus", CZE: "Czechia", DNK: "Denmark", EST: "Estonia", FIN: "Finland", FRA: "France", DEU: "Germany", GRC: "Greece", HUN: "Hungary", IRL: "Ireland", ITA: "Italy", LVA: "Latvia", LTU: "Lithuania", LUX: "Luxembourg", MLT: "Malta", NLD: "Netherlands", POL: "Poland", PRT: "Portugal", ROU: "Romania", SVK: "Slovakia", SVN: "Slovenia", ESP: "Spain", SWE: "Sweden" };

// Count contract notices for one country (demand volume only; used by the EU-wide ranking).
async function countryCount(iso3) {
  const query =
    `(classification-cpv IN (${cpvs.join(" ")})) AND (place-of-performance IN (${iso3}))` +
    ` AND (publication-date>=${sinceStr}) AND (notice-type IN (cn-standard cn-social cn-desg))`;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, fields: ["publication-number"], limit: 1 }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return (await res.json()).totalNoticeCount ?? 0;
    } catch (e) {
      if (attempt === 3) throw e;
      await new Promise((r) => setTimeout(r, attempt * 600));
    }
  }
}

async function euScan() {
  const rows = [];
  let failed = 0;
  const codes = Object.keys(EU27);
  for (let i = 0; i < codes.length; i += 3) {
    const batch = codes.slice(i, i + 3);
    const results = await Promise.allSettled(batch.map((c) => countryCount(c)));
    results.forEach((r, j) => {
      if (r.status === "fulfilled") rows.push({ country: batch[j], country_name: EU27[batch[j]], contract_notices: r.value });
      else failed++;
    });
    if (i + 3 < codes.length) await new Promise((r) => setTimeout(r, 250));
  }
  rows.sort((a, b) => b.contract_notices - a.contract_notices);
  const targetRank = rows.findIndex((r) => r.country === country) + 1;
  return {
    basis: "contract-notice volume only, same CPV codes and 12-month window",
    countries_scanned: rows.length,
    countries_failed: failed,
    target_rank: targetRank || null,
    top5: rows.slice(0, 5),
  };
}

try {
  const retrievedAt = new Date().toISOString();

  const [demand, awards, eu_markets] = await Promise.all([
    search(" AND (notice-type IN (cn-standard cn-social cn-desg))",
      ["publication-number", "notice-title", "buyer-name", "publication-date"], 20),
    search(" AND (notice-type IN (can-standard can-social can-desg))",
      ["publication-number", "notice-title", "buyer-name", "buyer-profile", "winner-name", "total-value", "total-value-cur", "publication-date"], 100),
    euScan().catch(() => null),
  ]);

  const demandCount = demand.totalNoticeCount ?? 0;
  const awardCount = awards.totalNoticeCount ?? 0;
  const awardSample = awards.notices ?? [];

  // Winners: count notices won per company (deduped per notice — multi-lot awards repeat names).
  const winners = new Map();
  const buyers = new Map();
  const buyerProfiles = new Map();
  const valueByCurrency = {};
  for (const n of awardSample) {
    const buyer = text(n["buyer-name"]);
    if (buyer) {
      buyers.set(buyer, (buyers.get(buyer) ?? 0) + 1);
      // Keep a buyer-profile URL only when it points somewhere specific, not a portal homepage.
      const prof = (n["buyer-profile"] ?? [])[0];
      if (prof && !buyerProfiles.has(buyer)) {
        try {
          if (new URL(prof).pathname.replace(/\/+$/, "").length > 1) buyerProfiles.set(buyer, prof);
        } catch { /* ignore malformed URLs */ }
      }
    }
    const names = new Set((Object.values(n["winner-name"] ?? {}).flat() ?? []).map((s) => s.trim()).filter(Boolean));
    for (const w of names) winners.set(w, (winners.get(w) ?? 0) + 1);
    const cur = (n["total-value-cur"] ?? [])[0];
    const val = Number(n["total-value"]);
    if (cur && Number.isFinite(val)) {
      const v = (valueByCurrency[cur] ??= { sum: 0, notices_with_value: 0, average: 0 });
      v.sum += val;
      v.notices_with_value += 1;
      v.average = v.sum / v.notices_with_value;
    }
  }
  const topWinners = [...winners.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([name, wonNotices]) => ({ name, wonNotices }));
  const topBuyers = [...buyers.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([name, notices]) => ({ name, notices, ...(buyerProfiles.has(name) ? { profile: buyerProfiles.get(name) } : {}) }));

  const recent = (demand.notices ?? []).slice(0, 3).map((n) => ({
    number: n["publication-number"],
    title: text(n["notice-title"]),
    buyer: text(n["buyer-name"]),
    date: String(n["publication-date"] ?? "").slice(0, 10),
    url: `https://ted.europa.eu/en/notice/-/detail/${n["publication-number"]}`,
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

  const out = {
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
    eu_markets: eu_markets ?? { basis: "scan failed; per-country ranking unavailable this run", top5: [] },
    score,
    score_bands: {
      demand_volume: "contract notices in window: 0=0, 1-9=6, 10-49=12, 50-199=18, 200+=25",
      buyer_diversity: "distinct buyers in award sample: 0=0, 1=5, 2-9=10, 10-24=18, 25+=25",
      winner_openness: "top winner share of sampled awards: no awards=0, >75%=5, 50-75%=10, 25-50%=18, <25%=25",
      recency: "days since latest contract notice: none=0, >180=5, 61-180=12, 31-60=18, <=30=25",
    },
  };
  console.log(JSON.stringify(out, null, 2));

  const reportPath = arg("report");
  if (reportPath) renderReport(out, reportPath);
} catch (e) {
  console.error(`ERROR: ${e.message}. TED API may be unreachable; do not invent results — use the committed fallback and say so.`);
  process.exit(1);
}

// ---- deterministic report rendering (--report) ---------------------------------------
function renderReport(out, reportPath) {
  const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const money = (v, c) => (v >= 1e9 ? `${(v / 1e9).toFixed(2)} bn ${c}` : v >= 1e6 ? `${(v / 1e6).toFixed(2)} m ${c}` : `${(v / 1e3).toFixed(0)} k ${c}`);
  const product = arg("product") ?? `CPV ${out.meta.cpv.join(", ")}`;
  const countryName = arg("country-name") ?? out.meta.country;
  const mapping = arg("mapping") ?? `CPV ${out.meta.cpv.join(", ")}, selected by the agent from the product description`;

  const s = out.score;
  const total = s.total;
  const verdict = total >= 80 ? "Strong signal" : total >= 55 ? "Promising signal" : total >= 30 ? "Weak signal" : total >= 1 ? "Minimal signal" : "Insufficient evidence";
  const color = total >= 70 ? "#0e8345" : total >= 35 ? "#b54708" : "#b42318";
  const aw = out.awards, dm = out.demand, eu = out.eu_markets;
  const tw = aw.top_winners[0];
  const valsEntries = Object.entries(aw.awarded_value_by_currency_in_sample).sort((a, b) => b[1].sum - a[1].sum);
  const valueSummary = valsEntries.map(([c, v]) => money(v.sum, c)).join(" + ") || "none published";
  const avgValue = valsEntries.map(([c, v]) => money(v.average, c)).join(" + ") || "n/a";
  const retrieved = out.meta.retrieved_at.slice(0, 16).replace("T", " ") + " UTC";
  const since = `${out.meta.since.slice(0, 4)}-${out.meta.since.slice(4, 6)}-${out.meta.since.slice(6)}`;
  const euRank = eu?.target_rank ? ` — the #${eu.target_rank} volume among ${eu.countries_scanned} EU countries scanned (${esc(eu.top5[0]?.country_name)} leads with ${eu.top5[0]?.contract_notices})` : "";

  const tokens = {
    PRODUCT: esc(product), COUNTRY_NAME: esc(countryName), COUNTRY_ISO3: out.meta.country,
    CPV_LIST: out.meta.cpv.join(", "), MONTHS: String(out.meta.window_months),
    RETRIEVED_AT: retrieved, SINCE_DATE: since, API_URL: "api.ted.europa.eu/v3/notices/search",
    SCORE_TOTAL: String(total), SCORE_COLOR: color, SCORE_VERDICT: verdict,
    S_DEMAND: String(s.demand_volume), PCT_DEMAND: String(s.demand_volume * 4),
    S_BUYERS: String(s.buyer_diversity), PCT_BUYERS: String(s.buyer_diversity * 4),
    S_OPEN: String(s.winner_openness), PCT_OPEN: String(s.winner_openness * 4),
    S_RECENCY: String(s.recency), PCT_RECENCY: String(s.recency * 4),
    WHY_DEMAND: `${dm.contract_notices} contract notices in the last ${out.meta.window_months} months`,
    WHY_BUYERS: `${aw.distinct_buyers_in_sample} distinct authorities in the ${aw.sample_size}-notice award sample`,
    WHY_OPEN: tw ? `top winner holds ${Math.round((tw.wonNotices / aw.sample_size) * 100)}% of sampled awards (${tw.wonNotices}/${aw.sample_size})` : "no awards in sample",
    WHY_RECENCY: dm.days_since_latest == null ? "no contract notices in window" : `latest contract notice published ${dm.days_since_latest} day(s) ago`,
    HEADLINE_FINDING: dm.contract_notices === 0
      ? `No calls for tender matching ${esc(product)} were published in ${esc(countryName)} in the window — insufficient evidence for a signal. The market may still exist below the EU publication threshold.`
      : `${esc(countryName)} published <strong>${dm.contract_notices} calls for tender</strong> for ${esc(product)} in the last ${out.meta.window_months} months${euRank}. The ${aw.sample_size} most recent awards total <strong>≈ ${valueSummary}</strong> across ${aw.distinct_buyers_in_sample} different buyers${tw ? `; the busiest winner (${esc(tw.name)}) took ${tw.wonNotices} of ${aw.sample_size} sampled awards` : ""}.`,
    DEMAND_NARRATIVE: `${dm.contract_notices} contract notices (calls for tender) and ${aw.award_notices} award notices were published in the window${dm.recent_examples[0] ? `, the most recent on ${dm.recent_examples[0].date}` : ""}.${aw.top_buyers[0] ? ` The most frequent buyers in the award sample: ${aw.top_buyers.slice(0, 3).map((b) => esc(b.name)).join("; ")}.` : ""}`,
    SAMPLE_SIZE: String(aw.sample_size), VALUE_SUMMARY: `≈ ${valueSummary}`, AVG_VALUE: `≈ ${avgValue}`,
    CPV_MAPPING_EXPLANATION: esc(mapping),
    BAND_DEMAND: out.score_bands.demand_volume, BAND_BUYERS: out.score_bands.buyer_diversity,
    BAND_OPEN: out.score_bands.winner_openness, BAND_RECENCY: out.score_bands.recency,
    EXTRA_LIMITATION: "<strong>Values:</strong> awarded values are summed per currency over the sampled award notices only; framework agreements may publish ceiling values, and product CPVs can match bundled tenders where the value covers the whole project.",
    EU_NOTE: eu && eu.top5.length
      ? `Ranked by ${esc(eu.basis)}. Scanned ${eu.countries_scanned} of 27 EU countries${eu.countries_failed ? ` (${eu.countries_failed} unreachable this run)` : ""}${eu.target_rank ? `; the target country ranks #${eu.target_rank} overall` : ""}. A full per-country signal needs its own scan.`
      : "EU-wide scan unavailable this run; per-country ranking omitted rather than estimated.",
  };

  // Optional build-time enrichment (see scripts/enrich-winners.mjs). Absent → section removed.
  let enrichment = null;
  const enrichPath = arg("enrichment");
  if (enrichPath) {
    try { enrichment = JSON.parse(readFile(enrichPath, "utf8")); } catch { enrichment = null; }
  }

  let t = readFile(joinPath(dirName(fileURLToPath(import.meta.url)), "..", "references", "report-template.html"), "utf8");
  t = t.replace(/<!-- Template for \$tender-demand-scan[\s\S]*?-->\n/, "");
  if (enrichment?.items?.length) {
    tokens.ENRICH_NOTE = `Websites resolved and fetched at build time (${enrichment.retrieved_at.slice(0, 10)}) via ${esc(enrichment.source)}; descriptions are the companies' own homepage wording. Not part of the live no-credentials run.`;
    t = t.replace(/<!-- ENRICH:START -->|<!-- ENRICH:END -->/g, "");
  } else {
    t = t.replace(/<!-- ENRICH:START -->[\s\S]*?<!-- ENRICH:END -->\n?/, "");
  }
  for (const [k, v] of Object.entries(tokens)) t = t.replaceAll(`{{${k}}}`, v);
  const fills = {
    buyers: aw.top_buyers.map((x) => `<tr><td>${x.profile ? `<a href="${esc(x.profile)}">${esc(x.name)}</a>` : esc(x.name)}</td><td class="num">${x.notices}</td></tr>`),
    winners: aw.top_winners.map((x) => `<tr><td>${esc(x.name)}</td><td class="num">${x.wonNotices}</td></tr>`),
    examples: dm.recent_examples.map((x) => `<tr><td><a href="${x.url}">${esc((x.title ?? "").slice(0, 160))}</a></td><td>${esc(x.buyer)}</td><td class="num">${x.date}</td></tr>`),
    markets: (eu?.top5 ?? []).map((r, i) => `<tr><td class="num">${i + 1}</td><td>${esc(r.country_name)}${r.country === out.meta.country ? " — target" : ""}</td><td class="num">${r.contract_notices}</td></tr>`),
    ...(enrichment?.items?.length ? {
      enriched: enrichment.items.map((x) => `<tr><td>${esc(x.name)}</td><td class="num">${x.wonNotices}</td><td>${x.website ? `<a href="${esc(x.website)}">${esc(new URL(x.website).hostname)}</a>` : "not resolved"}</td><td class="fine">${esc((x.page_description ?? x.page_title ?? "—").slice(0, 160))}</td></tr>`),
    } : {}),
  };
  for (const [key, rows] of Object.entries(fills)) {
    const body = rows.length ? rows.join("\n        ") : `<tr><td colspan="3" class="fine">none in this run</td></tr>`;
    t = t.replace(new RegExp(`(<tbody data-fill="${key}">)[\\s\\S]*?(</tbody>)`), `$1\n        ${body}\n      $2`);
  }
  const leftover = t.match(/\{\{[A-Z_]+\}\}/g);
  if (leftover) throw new Error(`unreplaced template tokens: ${leftover.join(", ")}`);
  writeFileSync(reportPath, t);
  console.error(`REPORT written to ${reportPath} — ${total}/100 ${verdict}`);
}
