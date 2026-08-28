# Specification: Geo-Expansion Viability Judge (`geo-expansion-mvp`)

## 1. Overview & Problem Statement
Cross-border e-commerce expansion for physical products frequently fails due to unverified landed margins, hidden cross-border regulatory compliance costs (e.g. German Packaging Act LUCID), and lack of real consumer demand signals in the target market.
This track implements the MVP for `$geo-expansion-judge`, a deterministic, evidence-grounded agent skill that synthesizes unit economics, compliance rules, and real-world Apify Reddit/web market pulse into an executive **Expansion Decision Brief** in under 60 seconds without private API keys.

## 2. Target User & Persona
- **Persona:** D2C E-commerce Founder or VP of Growth selling physical consumer goods (e.g., Romanian specialty coffee equipment brand expanding into Germany/EU).
- **Core Need:** A fast, de-risked Go / Caution / No-Go verdict grounded in verified local prices, compliance requirements, and genuine consumer sentiment.

## 3. The 3 Evaluation Pillars & Functional Requirements
- **FR1: Input Schema Ingestion (`demo/input/`):**
  - Reads `demo/input/expansion_request.json` (Product specs, origin RO, target DE/EU, MSRP, COGS, weight/dimensions, materials).
  - Ingests `demo/input/apify_reddit_signals.json` (Genuinely sourced Apify Reddit scraping dataset containing localized community posts, comments, and sentiment from `r/Coffee`, `r/espresso`, `r/germany`).
  - Gracefully halts with `INSUFFICIENT_EVIDENCE` if essential data is missing.
- **FR2: Unit Economics & Landed Cost Engine (Pillar 1 - 40%):**
  - Calculates landed cost: `COGS + Intra-EU Freight + Local VAT (19% German MwSt via EU OSS) + Packaging Disposal Fee`.
  - Calculates Landed Gross Margin vs. Local German Competitor Price Medians (e.g. Comandante, Fellow, Hario DE).
  - Margin Scoring: `>50%` = 100 pts, `35–50%` = 70 pts, `20–34%` = 40 pts, `<20%` = 0 pts (triggers margin Kill Trigger).
- **FR3: Regulatory & Market Compliance Matrix (Pillar 2 - 35%):**
  - Verifies target country compliance requirements:
    - German Packaging Act (VerpackG / LUCID registration & Dual System recycling licensing).
    - EU Food Contact Materials (FCM Regulation EC 1935/2004) material safety declaration.
    - EU VAT One-Stop Shop (OSS) cross-border B2C distance sales thresholds.
  - Assigns Compliance Score (0–100) and outputs specific compliance action items.
- **FR4: Apify Market Pulse & Sentiment Engine (Pillar 3 - 25%):**
  - Ingests Apify Reddit dataset and analyzes:
    - Net Sentiment Ratio (Positive vs. Critical/Negative discussions in target category).
    - Key Local Unmet Needs (e.g., complaints about long cross-border delivery times, lack of local EU warranty).
    - Price Anchors & Category Resonance.
  - Assigns Demand & Sentiment Score (0–100).
- **FR5: Composite Scoring & Decision Matrix:**
  - `Viability Score = (0.40 * Economics) + (0.35 * Compliance) + (0.25 * Apify Market Pulse)`
  - Verdicts: `GO` (Score ≥ 75), `CONDITIONAL_GO` (50–74), `NO_GO` (< 50).
  - Hard Kill Triggers: Landed margin < 20%, prohibited/non-compliant materials, or severely negative sentiment (< 25) forces `NO_GO`.
- **FR6: Decision Brief Generation (`demo/output/expansion_brief.md`):**
  - Executive Verdict Badge (`[ GO ]`, `[ CONDITIONAL_GO ]`, `[ NO_GO ]`).
  - Unit economics breakdown vs. local price ceilings.
  - Compliance checklist with official government/regulatory URLs.
  - Apify Reddit community pulse summary and key consumer quotes.
  - Actionable launch roadmap & kill triggers.

## 4. Non-Functional & Evaluation Requirements
- **Cold Run Execution:** Runs end-to-end in Codex in < 60 seconds using standard Python 3.
- **Zero Hallucinations & Real-World Signal:** All competitor prices, Apify sentiment data, and compliance laws cite real URLs and retrieval timestamps.
- **Eval Cases (`demo/evals.md`):**
  1. *Intended Success Case:* Specialty Coffee Kit (RO -> DE) with valid specs & positive Apify sentiment -> Output `GO` / `CONDITIONAL_GO`.
  2. *Insufficient Evidence Case:* Missing material/weight or missing country -> Halts with `INSUFFICIENT_EVIDENCE`.
  3. *Exclusion/Failure Case:* Prohibited food contact material or negative landed margin -> Output `NO_GO` + Kill Trigger.
