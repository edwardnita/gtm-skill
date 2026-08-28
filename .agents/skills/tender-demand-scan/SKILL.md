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

   `node .agents/skills/tender-demand-scan/scripts/ted-fetch.mjs --cpv <codes,comma-separated> --country <ISO3> --months 12 --report report.html --product "<product label>" --country-name "<Country>" --mapping "<one sentence: which CPV codes you chose and what they cover>"`

   The script queries the live TED API (no key needed), prints one JSON document, computes the four sub-scores, and renders the full HTML report deterministically from `references/report-template.html` — no step of the output is improvised. Do not recompute scores or rewrite the report by hand. Use another `--report` path only if the prompt names one.

   Optional, build-time only (never in a credential-less live run): `scripts/enrich-winners.mjs` resolves the top winners' websites via an Apify search actor (token required) and writes an enrichment JSON; re-rendering with `--enrichment <file>` adds an "Incumbents up close" section. Without it, the report simply omits that section.
4. If the script exits non-zero, the most common cause is a sandbox blocking network access, not the API being down: re-run the command once with network access enabled (approve or escalate the permission prompt if the environment asks). Only if that also fails, report "TED API unreachable — no result" and stop. Never invent counts, winners, or values. If a committed fallback report exists (`demo/output/`), point the user to it and say clearly that it is a snapshot, not live data.
5. Verify the render: the script prints `REPORT written to <path> — <total>/100 <verdict>` and fails loudly if any template token is left unreplaced. Confirm the file exists. Do not edit the generated HTML; if something looks wrong, fix the inputs and re-run.
6. Print: the output path, the score line (`total/100 — verdict` — verdicts: 80–100 Strong, 55–79 Promising, 30–54 Weak, 1–29 Minimal, 0 Insufficient evidence), and a 3-row text summary from the JSON (demand count, top buyer, top winner) so the result is visible without opening the file. If `eu_markets.target_rank` exists, mention it in one sentence.

## Rules

- Never include personal data: no contact persons, emails, or phone numbers from notices. Companies and public authorities acting in their public role only.
- Never state a market fact that is not in the script's JSON output. No market sizes, growth rates, or claims from memory. The report is evidence or silence.
- Never make the bid/no-bid recommendation. The score is a labeled heuristic; the decision stays with the user.
- Never draft outreach to authorities or vendors; refuse if asked and explain this skill stops at the report.
- Zero matching notices is a valid result: produce the report with score 0, verdict "Insufficient evidence", and say the market may still exist below the EU publication threshold.
- Never describe committed or cached data as live. Live data carries the script's `retrieved_at`; fallbacks are named as snapshots.

## Done when

`report.html` exists with no unreplaced tokens, every figure in it traces to the script's JSON (source: TED API, retrieval timestamp shown), the CPV mapping and scoring bands are stated in the report, and the score line was printed to the user.
