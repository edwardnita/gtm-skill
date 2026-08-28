---
name: tender-demand-scan
description: Scans live EU public-procurement data (TED API) for a product or service in a target EU country and writes a self-contained HTML market-entry report — demand volume, buying authorities, winning competitors, three linked example tenders, a deterministic 0-100 signal score, and a top-5 ranking of EU countries by demand for the same product, all with sources and retrieval dates. Use when the user asks whether there is public-sector demand for something in an EU market, who buys it, who wins those contracts, or which EU countries to consider.
---

# Tender demand scan

## Input

A product/service description and one target EU country, given in the prompt or in a file the prompt names (e.g. `demo/input/request.md`). If either is missing, ask for it and stop.

## Steps

1. Validate the country. TED covers EU/EEA procurement. If the country is not covered (e.g. USA, UK post-2021), say so plainly and stop — do not substitute another country.
2. Map the product/service description to 1–3 CPV codes (the EU procurement taxonomy). Prefer one division-level code (e.g. `72000000` for IT services) plus at most two narrower ones. Write the mapping down — it must appear in the report so it can be challenged.
3. Convert the country to ISO3 (Romania → ROU) and run, from the repository root:

   `node .agents/skills/tender-demand-scan/scripts/ted-fetch.mjs --cpv <codes,comma-separated> --country <ISO3> --months 12`

   The script queries the live TED API (no key needed), prints one JSON document, and computes the four sub-scores deterministically. Do not recompute or adjust the scores.
4. If the script exits non-zero, the most common cause is a sandbox blocking network access, not the API being down: re-run the command once with network access enabled (approve or escalate the permission prompt if the environment asks). Only if that also fails, report "TED API unreachable — no result" and stop. Never invent counts, winners, or values. If a committed fallback report exists (`demo/output/`), point the user to it and say clearly that it is a snapshot, not live data.
5. Read the JSON and derive:
   - Verdict from `score.total`: 80–100 "Strong signal", 55–79 "Promising signal", 30–54 "Weak signal", 1–29 "Minimal signal", 0 "Insufficient evidence".
   - Score color: total ≥ 70 → `#0e8345`, 35–69 → `#b54708`, < 35 → `#b42318`.
   - One headline finding in plain language, using only numbers present in the JSON.
6. Copy `references/report-template.html` (next to this file), delete its leading instruction comment, and replace every `{{TOKEN}}` and every `data-fill` tbody with real rows from the JSON:
   - Bar widths: `PCT_* = points / 25 * 100`. The `WHY_*` lines quote the underlying number (e.g. "733 contract notices in 12 months").
   - `VALUE_SUMMARY`: format the per-currency `sum` values compactly (e.g. "1.73 bn RON + 244 m EUR"); `AVG_VALUE`: the per-currency `average` values, same format.
   - Every table row keeps its source: examples link to their `url`; buyer/winner tables state they come from the award-notice sample.
   - The "Where else in the EU" table comes from `eu_markets.top5`; its fine print states the basis (contract-notice volume only), how many of the 27 countries were scanned, and the target country's rank. If the scan partially failed, say so — never fill missing countries from memory.
   - Fill the scoring-band lines from `score_bands` verbatim. `EXTRA_LIMITATION`: state the honest one for this run (e.g. broad CPV mapping, small sample). For product CPVs, note that matches include bundled tenders — the product may be one component of a larger project, and published values cover the whole bundle.
7. Write the finished report to `report.html` at the repository root, unless the prompt names another output path. Leave no `{{TOKEN}}` unreplaced.
8. Print: the output path, the score line (`total/100 — verdict`), and a 3-row text summary (demand count, top buyer, top winner) so the result is visible without opening the file.

## Rules

- Never include personal data: no contact persons, emails, or phone numbers from notices. Companies and public authorities acting in their public role only.
- Never state a market fact that is not in the script's JSON output. No market sizes, growth rates, or claims from memory. The report is evidence or silence.
- Never make the bid/no-bid recommendation. The score is a labeled heuristic; the decision stays with the user.
- Never draft outreach to authorities or vendors; refuse if asked and explain this skill stops at the report.
- Zero matching notices is a valid result: produce the report with score 0, verdict "Insufficient evidence", and say the market may still exist below the EU publication threshold.
- Never describe committed or cached data as live. Live data carries the script's `retrieved_at`; fallbacks are named as snapshots.

## Done when

`report.html` exists with no unreplaced tokens, every figure in it traces to the script's JSON (source: TED API, retrieval timestamp shown), the CPV mapping and scoring bands are stated in the report, and the score line was printed to the user.
