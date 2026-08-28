---
name: geo-expansion-judge
description: Evaluates cross-border e-commerce expansion viability for physical products across unit economics, target country compliance, and Apify community market sentiment. Trigger when an e-commerce brand or founder wants to evaluate expanding physical products into a new country or requests a Go/No-Go market expansion assessment.
---

# Geo-Expansion Viability Judge

Evaluates whether any physical e-commerce consumer product will gain traction, comply with cross-border regulations, and remain profitable when expanding into a foreign market (with 100% coverage across all 27 EU Member States and global fallback support).

## Input Contract

The skill accepts a structured JSON expansion request profile (default: `demo/input/expansion_request.json`):
- `product_name`: Physical product name.
- `origin_country`: ISO 2-letter country code (e.g. `RO`, `DE`, `US`, `UK`).
- `target_country`: Any ISO 2-letter country code (all 27 EU member states: `AT`, `BE`, `BG`, `HR`, `CY`, `CZ`, `DK`, `EE`, `FI`, `FR`, `DE`, `GR`, `HU`, `IE`, `IT`, `LV`, `LT`, `LU`, `MT`, `NL`, `PL`, `PT`, `RO`, `SK`, `SI`, `ES`, `SE`, plus global destinations like `US`, `GB`, `JP`, `AU`, `CA`, `BR`, `MX`, `SG`, `CH`, `NO`).
- `category`: Physical product category (e.g. `kitchenware`/`coffee`, `electronics`/`audio`, `cosmetics`/`skincare`, `apparel`/`textiles`, `toys`/`baby`, `fitness`/`general_goods`).
- `specifications`: Weight in grams, dimensions, packaging, and list of physical materials.
- `financials`: `unit_cogs_ex_factory`, `proposed_target_retail_msrp`, `origin_export_packaging_cost`.
- `local_competitor_benchmarks`: List of local competitor products with verified retail prices, seller names, and source URLs.

Supporting inputs:
- `demo/input/apify_reddit_signals.json`: Scraped community pulse dataset from Apify Reddit Scraper.
- `scripts/data/country_baselines.json`: 38+ pre-computed country tax (VAT/OSS), packaging act (EPR/VerpackG), and compliance standards.

## Output Contract

The skill writes an **Expansion Viability Decision Brief** to `demo/output/expansion_brief.md` containing:
1. Executive Verdict (`[ GO ]`, `[ CONDITIONAL_GO ]`, `[ NO_GO ]`, or `[ INSUFFICIENT_EVIDENCE ]`) and Viability Score (0–100).
2. Landed Unit Economics & Gross Margin Benchmark table vs local competitor median prices.
3. Cross-Border Compliance Matrix with specific category directives (e.g. GPSR, CE/WEEE/RoHS for electronics, CPNP for cosmetics, FCM for kitchenware, REACH for apparel).
4. Real-World Community Pulse & Sentiment Analysis (purchase drivers, willingness-to-pay range, friction points).
5. Kill Trigger Audit (halts on negative margins, hazardous materials, or extreme consumer hostility).
6. Comprehensive Grounded Citations Table with verifiable source URLs and retrieval dates.

## Operational Workflow

1. **Input Ingestion & Validation:**
   - Read the input request profile.
   - Verify that origin/target country, MSRP, COGS, and physical materials are defined.
   - If any required parameter is missing or unparseable, immediately halt and emit an `INSUFFICIENT_EVIDENCE` brief detailing the missing fields. Do not guess or hallucinate missing data.

2. **Execute Analytical Engines:**
   - Run `python3 scripts/evaluate_expansion.py --input <input_path> --output <output_path>`.
   - **Pillar 1 (Economics - 40%):** Calculate landed cost (`COGS + Export Packaging + Freight + Destination VAT + Packaging Licensing Fee`), net realized revenue, landed gross margin %, and competitor price ratio.
   - **Pillar 2 (Compliance - 35%):** Screen materials against chemical regulations (REACH/LFGB), Packaging EPR, destination category directives (GPSR, CE/WEEE, CPNP, FCM), and EU OSS / DDP customs rules.
   - **Pillar 3 (Apify Market Pulse - 25%):** Ingest Apify Reddit sentiment dataset, compute positive/negative ratio, compare target MSRP against community willingness-to-pay median, and extract local customer friction points.

3. **Composite Scoring & Decision Formulation:**
   - Calculate `Viability Score = (0.40 * Econ) + (0.35 * Comp) + (0.25 * Pulse)`.
   - Assign Verdict:
     - `GO` (Viability Score >= 75): Favorable margins, clear compliance, strong sentiment.
     - `CONDITIONAL_GO` (50–74): Viable with adjustments (e.g. margin optimization or certification).
     - `NO_GO` (< 50 or active Kill Trigger): Unviable unit economics, hazardous materials, or severe community hostility.

4. **Render and Save Brief:**
   - Write the full decision brief to `demo/output/expansion_brief.md`.
   - Output executive summary to the terminal.

## Boundaries & Non-Negotiables

- **Never Fabricate Sources:** Every competitor price, VAT rate, and regulatory law MUST cite a real URL and retrieval timestamp.
- **Never Skip Compliance / Kill Triggers:** Prohibited substances or negative landed margins must trigger an immediate `NO_GO`.
- **Refusal over Hallucination:** If essential specs or country data cannot be resolved, emit `INSUFFICIENT_EVIDENCE`.
- **No Private Credentials Needed:** Runs strictly in Codex desktop app using local data and public references.

## Done When

`demo/output/expansion_brief.md` is written, contains a definitive verdict and viability score, presents the 3-pillar breakdown, and includes verifiable citations and kill trigger evaluations.
