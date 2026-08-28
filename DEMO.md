# Run sheet

The organizer presents this repository for you, in 2 minutes, without having seen it before. Write every line for them. Replace every placeholder. Keep it to one screen.

## Say this — 20 seconds

**Team:** Brand Expansion AI (Radu & Edward Nita)

**Track:** `personalized-growth-engines`

**Who has the problem:** D2C e-commerce founders and heads of growth expanding physical consumer products cross-border (e.g. Romanian specialty coffee equipment brand expanding into Germany).

**The job this skill does:** Evaluates expansion viability in under 60 seconds across unit economics (landed margin vs local price ceiling), target market compliance (VerpackG/LUCID, FCM, EU OSS VAT), and real-world Apify community sentiment.

**Boundary — what it never does:** Never recommends expansion without verified local price benchmarks and compliance checks; halts with `INSUFFICIENT_EVIDENCE` instead of hallucinating missing specs.

## Run this — 60 seconds

1. Codex is open at the repository root.
2. Paste [`demo/seed-prompt.md`](demo/seed-prompt.md).
3. Watch for: Output of the **Expansion Viability Decision Brief** with verdict badge `[ GO ]`, 96/100 score, landed margin breakdown (50.0%), and Apify Reddit community sentiment summary.
4. If nothing visible after 60 seconds, open the fallback: [`demo/output/expansion_brief.md`](demo/output/expansion_brief.md)

## Show this — 25 seconds

**Result:** An executive Decision Brief giving founders a clear `GO` verdict, landed unit economics breakdown (€34.50 landed cost vs €69.00 MSRP), LUCID packaging checklist, and Apify consumer purchase drivers.

**Evidence:** Competitor price benchmarks cite real German store URLs (Amazon.de, The Barn Berlin, Coffee Circle); regulatory checks cite official BfR and LUCID registries; community signals cite Apify Reddit scrape run timestamp (`2026-08-28T17:45:00Z`).

**Fallback output was produced:** 2026-08-28 19:00:21 UTC via `$geo-expansion-judge` CLI engine.

## Evals — 10 seconds

| Case | Result | Where |
| :--- | :--- | :--- |
| Intended | Passes with `[ GO ]` (96/100 score, 50.0% landed margin, positive sentiment) | [`demo/evals.md`](demo/evals.md) |
| Insufficient evidence | Passes with `[ INSUFFICIENT_EVIDENCE ]` when specs/COGS are missing | [`demo/evals.md`](demo/evals.md) |
| Failure / exclusion | Passes with `[ NO_GO ]` and kill trigger on lead glaze chemical hazard | [`demo/evals.md`](demo/evals.md) |

## Close — 5 seconds

**Reusable on:** Any physical consumer product (apparel, ceramics, accessories, cosmetics) expanding between European and international corridors with matching baseline configurations.

**Material limitation:** Freight rates and local VAT are based on standard parcel baselines; heavy palletized freight (>30kg) requires custom forwarder quotes.
