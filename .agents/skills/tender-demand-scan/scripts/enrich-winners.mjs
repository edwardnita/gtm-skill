#!/usr/bin/env node
// Build-time enrichment for $tender-demand-scan: resolves the top award winners' websites
// via Apify's Google Search Scraper actor, then fetches each homepage directly for its
// title and meta description. Company-level facts only; never collects personal data.
//
// This is NOT part of the live judged run (the jury laptop has no credentials). Run it
// during a build with an Apify token, commit the JSON it produces, and re-render the
// report with ted-fetch.mjs --enrichment <file>.
//
// Token: env APIFY_TOKEN, or a gitignored .apify_token file in the repository root.
// Usage: node enrich-winners.mjs --data demo/output/ted-data.json [--top 5] [--out demo/output/enrichment.json]

import { readFileSync, writeFileSync, existsSync } from "node:fs";

function arg(name, fallback = null) {
  const i = process.argv.indexOf(`--${name}`);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : fallback;
}

const dataPath = arg("data");
const top = Number(arg("top") ?? 5);
const outPath = arg("out") ?? "demo/output/enrichment.json";
if (!dataPath || !existsSync(dataPath)) {
  console.error("usage: node enrich-winners.mjs --data <ted-fetch output.json> [--top 5] [--out enrichment.json]");
  process.exit(1);
}

let token = process.env.APIFY_TOKEN ?? "";
if (!token && existsSync(".apify_token")) token = readFileSync(".apify_token", "utf8").trim();
if (!token) {
  console.error("SKIPPED: no Apify token. Set APIFY_TOKEN or put the token in a gitignored .apify_token file. No enrichment was produced; the report renders without the incumbents section.");
  process.exit(1);
}

const data = JSON.parse(readFileSync(dataPath, "utf8"));
const countryName = { ROU: "Romania", POL: "Poland" }[data.meta.country] ?? data.meta.country;
const winners = (data.awards?.top_winners ?? []).slice(0, top);
if (winners.length === 0) {
  console.error("SKIPPED: no winners in the data file.");
  process.exit(1);
}

// Domains that are registries/aggregators, not the company's own site.
const NOT_OFFICIAL = /linkedin|facebook|listafirme|romanian-companies|targetare|risco\.|termene\.|cylex|europages|ted\.europa|e-licitatie|kompass|zoominfo|dnb\.com|bloomberg|crunchbase/i;

async function searchSite(name) {
  const res = await fetch(`https://api.apify.com/v2/acts/apify~google-search-scraper/run-sync-get-dataset-items?token=${token}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ queries: `${name} ${countryName}`, resultsPerPage: 5, maxPagesPerQuery: 1 }),
  });
  if (!res.ok) throw new Error(`Apify HTTP ${res.status}`);
  const items = await res.json();
  const organic = items.flatMap((i) => i.organicResults ?? []);
  const hit = organic.find((r) => r.url && !NOT_OFFICIAL.test(r.url));
  return hit?.url ?? null;
}

async function fetchMeta(url) {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(10000), headers: { "user-agent": "Mozilla/5.0 (tender-demand-scan enrichment)" } });
    if (!res.ok) return {};
    const html = (await res.text()).slice(0, 200000);
    const title = /<title[^>]*>([^<]{1,200})/i.exec(html)?.[1]?.trim();
    const desc = /<meta[^>]+name=["']description["'][^>]+content=["']([^"']{1,300})/i.exec(html)?.[1]?.trim()
      ?? /<meta[^>]+content=["']([^"']{1,300})["'][^>]+name=["']description["']/i.exec(html)?.[1]?.trim();
    return { page_title: title ?? null, page_description: desc ?? null };
  } catch {
    return {};
  }
}

const items = [];
for (const w of winners) {
  process.stderr.write(`resolving: ${w.name} ... `);
  try {
    const website = await searchSite(w.name);
    const meta = website ? await fetchMeta(website) : {};
    items.push({ name: w.name, wonNotices: w.wonNotices, website, search_query: `${w.name} ${countryName}`, ...meta });
    console.error(website ?? "not resolved");
  } catch (e) {
    items.push({ name: w.name, wonNotices: w.wonNotices, website: null, error: e.message });
    console.error(`failed (${e.message})`);
  }
}

writeFileSync(outPath, JSON.stringify({
  source: "Apify google-search-scraper (website resolution) + direct homepage fetch (title/description)",
  note: "Build-time enrichment; descriptions are the companies' own homepage wording. Company-level facts only.",
  country: data.meta.country,
  retrieved_at: new Date().toISOString(),
  items,
}, null, 2));
console.error(`written ${outPath} (${items.filter((i) => i.website).length}/${items.length} resolved)`);
