# Run sheet

## Say this — 20 seconds

**Team:** Tender Radar

**Track:** custom

**Who has the problem:** A GTM/BD lead at a B2B company (in this demo: a software-services firm) deciding whether a new EU country is worth entering.

**The job this skill does:** It asks the official EU procurement journal (TED) — live, no API key — whether the public sector in that country buys what you sell, who buys it, and who keeps winning, and writes a scored one-page HTML report with a source and retrieval date on every figure.

**Boundary — what it never does:** Never extracts personal contacts, never states a market fact it didn't fetch, never makes the bid/no-bid call.

## Run this — 60 seconds

1. Codex is open at the repository root.
2. Paste [`demo/seed-prompt.md`](demo/seed-prompt.md).
3. Watch for: two fast calls to `api.ted.europa.eu` via the skill's zero-dependency Node script, then **`report.html` written at the repo root** and a printed score line ("…/100 — verdict"). Open `report.html` in the browser: a scored market-entry report built from tenders **published this very day**.
4. If nothing visible after 60 seconds, open the fallback: [`demo/output/report.html`](demo/output/report.html)

## Show this — 25 seconds

**Result:** A self-contained HTML report: 0–100 market-entry signal score (four counted sub-scores), the authorities that buy, the incumbent companies that win, and three clickable live tenders. A GTM lead uses it to decide in minutes whether a market deserves a real business case.

**Evidence:** The header and footer carry the TED API source and retrieval timestamp; the three example tenders link to ted.europa.eu; the raw API response is committed at [`demo/output/ted-data.json`](demo/output/ted-data.json); the scoring bands are printed in the report so the score can be challenged.

**Fallback output was produced:** 2026-08-28, ~19:30 EEST, by running the seed prompt against the live TED API during the build window (retrieval timestamp 16:30 UTC is embedded in the report). The report has one-click PDF/print and CSV export.

## Evals — 10 seconds

| Case | Result | Where |
| --- | --- | --- |
| Intended | Pass — 100/100 report, every figure sourced | [`demo/evals.md`](demo/evals.md) |
| Insufficient evidence | Pass — niche product returned 0 notices → score 0, "Insufficient evidence", nothing invented | [`demo/evals.md`](demo/evals.md) |
| Failure / exclusion | Pass — refused to extract procurement officers' emails | [`demo/evals.md`](demo/evals.md) |

## Close — 5 seconds

**Reusable on:** any product/service × any EU/EEA country, unchanged — verified during the event on Poland (5,418 notices, score 100) with the same skill and script.

**Material limitation:** TED only lists above-EU-threshold tenders; smaller national tenders (e.g. Romania's SICAP-only procedures) are not counted — so demand is understated, never overstated, and awarded values can be framework ceilings rather than actual spend.
