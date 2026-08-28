# Run sheet

## Say this — 20 seconds

**Team:** Tender Radar

**Track:** custom

**Who has the problem:** A GTM/BD lead at a B2B company (in this demo: a medical-imaging equipment maker) deciding whether a new EU country is worth entering.

**The job this skill does:** It asks the official EU procurement journal (TED) — live, no API key — whether the public sector in that country buys what you sell, who buys it, and who keeps winning, and writes a scored one-page HTML report — plus a ranking of the top 5 EU countries for the same product — with a source and retrieval date on every figure.

**Boundary — what it never does:** Never extracts personal contacts, never states a market fact it didn't fetch, never makes the bid/no-bid call.

## Run this — 60 seconds

1. Codex is open at the repository root.
2. Paste [`demo/seed-prompt.md`](demo/seed-prompt.md).
3. Watch for: the skill's zero-dependency Node script calling `api.ted.europa.eu`, then the line **`REPORT written to report.html — 86/100 Strong signal`** (the HTML is rendered deterministically by the script, not written by the model). Open `report.html` in the browser: a scored market-entry report built from live tender data, including the top-5 EU markets table (Romania is the EU's #2 X-ray market; Poland leads at 7× the volume).
4. If nothing visible after 60 seconds, open the fallback: [`demo/output/report.html`](demo/output/report.html)

## Show this — 25 seconds

**Result:** A self-contained HTML report: 0–100 market-entry signal score (four counted sub-scores), the hospitals and authorities that buy, the incumbent suppliers that win, three clickable live tenders, and the top-5 EU countries ranked by demand for the same product. A GTM lead uses it to decide in minutes whether a market deserves a real business case.

**Evidence:** The header and footer carry the TED API source and retrieval timestamp; the three example tenders link to ted.europa.eu; the raw API response is committed at [`demo/output/ted-data.json`](demo/output/ted-data.json); the scoring bands are printed in the report so the score can be challenged.

**Fallback output was produced:** 2026-08-28, ~20:09 EEST, by the same script the live run uses, against the live TED API (retrieval timestamp 17:09 UTC is embedded in the report). The report has one-click PDF/print and CSV export.

## Evals — 10 seconds

| Case | Result | Where |
| --- | --- | --- |
| Intended | Pass — 86/100 report (X-ray devices, Romania), every figure sourced | [`demo/evals.md`](demo/evals.md) |
| Insufficient evidence | Pass — niche product returned 0 notices → score 0, "Insufficient evidence", nothing invented | [`demo/evals.md`](demo/evals.md) |
| Failure / exclusion | Pass — refused to extract procurement officers' emails | [`demo/evals.md`](demo/evals.md) |

## Close — 5 seconds

**Reusable on:** any product/service × any EU/EEA country, unchanged — verified during the event on Poland (score 100, 5,418 notices) and on 20 further product/service × country runs. If asked "does it always say 100?": no — this very demo scores 86 (one supplier holds 38% of awards), and across 20+ test runs scores ranged 0–100 (ambulances 52, drone equipment 67, software 100). The fixed scoring bands are printed in every report.

**Material limitation:** TED only lists above-EU-threshold tenders; smaller national tenders (e.g. Romania's SICAP-only procedures) are not counted — so demand is understated, never overstated, and awarded values can be framework ceilings or whole-bundle totals rather than the product's own slice. Scraping national portals (e.g. SICAP, via an Apify actor) is the natural next step.
