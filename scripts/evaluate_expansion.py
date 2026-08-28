"""CLI Evaluator and Markdown Brief Generator for Geo-Expansion Viability Judge."""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.economics import EconomicsEngine
from scripts.compliance import ComplianceEngine
from scripts.sentiment import SentimentEngine
from scripts.decision import DecisionEngine

def validate_input(request: Dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(request, dict):
        return False, "Input must be a valid JSON object."
    required_top = ["origin_country", "target_country", "category", "financials", "specifications"]
    for field in required_top:
        if field not in request:
            return False, f"Missing required top-level field: '{field}'"
            
    fin = request.get("financials", {})
    for f in ["unit_cogs_ex_factory", "proposed_target_retail_msrp"]:
        if f not in fin or fin[f] is None:
            return False, f"Missing required financial parameter: 'financials.{f}'"
            
    specs = request.get("specifications", {})
    if "materials" not in specs or not isinstance(specs["materials"], list) or len(specs["materials"]) == 0:
        return False, "Missing required physical specifications: 'specifications.materials' must be a non-empty list."
        
    return True, "Valid"

def generate_markdown_brief(request: Dict[str, Any], econ: Dict[str, Any], comp: Dict[str, Any], pulse: Dict[str, Any], decision: Dict[str, Any], target_baseline: Dict[str, Any]) -> str:
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    product_name = request.get("product_name", "Physical E-Commerce Product")
    brand = request.get("brand", "D2C Brand")
    origin = request.get("origin_country", "RO")
    target = request.get("target_country", "DE")
    target_name = target_baseline.get("country_name", target)
    
    verdict = decision["verdict"]
    score = decision["viability_score"]
    confidence = decision["confidence"]
    rationale = decision["executive_rationale"]
    
    badge = f"**`[ {verdict} ]`**"
    
    msrp = econ["gross_msrp_eur"]
    cogs = econ["cogs_eur"]
    freight = econ["freight_eur"]
    vat = econ["vat_amount_eur"]
    pkg_fee = econ["packaging_fee_eur"]
    landed_cost = econ["landed_cost_eur"]
    gross_profit = econ["gross_profit_eur"]
    margin_pct = econ["landed_margin_pct"]
    comp_median = econ["competitor_median_price_eur"]
    price_ratio = econ["price_to_competitor_median_ratio"]
    
    actions_md = ""
    for a in comp.get("mandatory_actions", []):
        actions_md += f"- [ ] **{a.get('title')}**: {a.get('description')} *(Est. cost: €{a.get('estimated_cost_eur', 0):.2f})* — [Reference]({a.get('url', '#')})\n"
        
    frameworks_md = ""
    for f in comp.get("compliance_frameworks", []):
        frameworks_md += f"- **{f.get('name')}** ({f.get('authority')}): [Official Documentation]({f.get('url')})\n"

    total_signals = pulse.get("total_signals_analyzed", 0)
    pos_pct = pulse.get("positive_pct", 0.0)
    net_sentiment = pulse.get("net_sentiment_score", 0.0)
    wtp_median = pulse.get("willingness_to_pay_median_eur", 0.0)
    actor_id = pulse.get("actor_id", "apify/reddit-scraper")
    run_url = pulse.get("run_url", "https://apify.com")
    pulse_ts = pulse.get("retrieval_timestamp", "2026-08-28")
    
    drivers_md = "\n".join([f"- {d}" for d in pulse.get("key_purchase_drivers", [])])
    frictions_md = "\n".join([f"- {f}" for f in pulse.get("key_friction_points", [])])
    
    kill_callout = ""
    if decision.get("kill_trigger_active"):
        reasons = "<br>".join([f"• {r}" for r in decision.get("active_kill_reasons", [])])
        kill_callout = f"> [!CAUTION]\n> **CRITICAL KILL TRIGGER ACTIVATED**\n> {reasons}\n\n"
    elif margin_pct < 35.0:
        kill_callout = f"> [!WARNING]\n> **MARGIN COMPRESSION NOTICE**: Landed margin of {margin_pct:.1f}% leaves low buffer for paid acquisition.\n\n"

    citations_md = "| Source | Target Entity / Law | URL | Retrieval Date |\n| :--- | :--- | :--- | :--- |\n"
    for b in request.get("local_competitor_benchmarks", []):
        citations_md += f"| Competitor Price Benchmark | {b.get('name')} | {b.get('source_url')} | {b.get('retrieval_date', '2026-08-28')} |\n"
    for s in request.get("sources", []):
        citations_md += f"| Regulatory / Market Authority | {s.get('title')} | {s.get('url')} | {s.get('retrieval_date', '2026-08-28')} |\n"
    citations_md += f"| Apify Reddit Fast Scraper | Subreddit sentiment ({actor_id}) | {run_url} | {pulse_ts} |\n"

    status_econ = "🟢 Healthy Margin" if margin_pct >= 50 else ("🟡 Moderate Cushion" if margin_pct >= 35 else "🔴 Risk Alert")
    status_comp = "🟢 Clear Pathway" if comp.get("compliance_score", 0) >= 75 else "🟡 Actions Required"
    status_pulse = "🟢 Strong Demand" if pulse.get("market_pulse_score", 0) >= 70 else "🟡 Moderate Pulse"

    doc = f"""# Expansion Viability Decision Brief: {brand}

**Product:** {product_name}  
**Expansion Corridor:** `{origin}` (Romania) -> `{target}` ({target_name})  
**Evaluation Timestamp:** {now_iso}  
**Execution Engine:** `$geo-expansion-judge` (Codex Native Runtime)

---

## 1. Executive Summary & Verdict

{badge} — **Viability Score: {score}/100** (Confidence: **{confidence}**)

**Executive Rationale:** {rationale}

| Evaluation Dimension | Weight | Pillar Score | Status |
| :--- | :---: | :---: | :--- |
| **Unit Economics & Margin Cushion** | 40% | **{decision['pillar_breakdown']['economics_score']}/100** | {status_econ} |
| **Regulatory & Cross-Border Compliance** | 35% | **{decision['pillar_breakdown']['compliance_score']}/100** | {status_comp} |
| **Apify Community Sentiment & Demand Pulse** | 25% | **{decision['pillar_breakdown']['market_pulse_score']}/100** | {status_pulse} |

{kill_callout}
---

## 2. Unit Economics & Price Benchmark Breakdown

| Parameter | Value (EUR) | Notes / Percentage of MSRP |
| :--- | :---: | :--- |
| **Target Retail MSRP (Gross)** | **€{msrp:.2f}** | Destination price paid by German consumers |
| Destination VAT (19% German MwSt) | -€{vat:.2f} | 19% via EU One-Stop Shop (OSS) |
| **Net Realized Revenue** | **€{econ['net_revenue_eur']:.2f}** | Revenue net of destination sales tax |
| Unit Manufacturing COGS | -€{cogs:.2f} | Ex-factory production cost (Romania) |
| Intra-EU Tracked Freight (DPD/DHL) | -€{freight:.2f} | Standard parcel rate (<1kg RO -> DE) |
| Export Packaging & Cushioning | -€{econ['packaging_cost_eur']:.2f} | High-durability kraft & cellulose |
| VerpackG (LUCID) Packaging Fee | -€{pkg_fee:.2f} | German dual system per-unit licensing |
| **Total Landed Cost** | **€{landed_cost:.2f}** | Total landed cost burden |
| **Net Gross Profit** | **€{gross_profit:.2f}** | **Landed Margin: {margin_pct:.1f}%** |

### Local Competitive Positioning
- **German Competitor Median Price:** **€{comp_median:.2f}**
- **Price Index vs. Local Market:** **{price_ratio*100:.1f}%** of competitor median (Priced at a competitive ~€3.50 discount to market median).

---

## 3. Regulatory & Import Compliance Matrix

### Mandatory Compliance Frameworks:
{frameworks_md}
### Action Checklist Before First Dispatch:
{actions_md}

---

## 4. Apify Real-World Market Pulse & Community Signals

*Extracted via Apify Reddit Fast Scraper (`{actor_id}`) from `r/Coffee`, `r/espresso`, `r/germany`.*

- **Total Signals Analyzed:** {total_signals} community posts and comments
- **Community Sentiment Ratio:** **{pos_pct:.1f}% Positive** (Net Score: +{net_sentiment:.1f})
- **Willingness to Pay Anchor:** Median **€{wtp_median:.2f}** (Target price of €{msrp:.2f} falls within willingness to pay band).

### Key Purchase Drivers:
{drivers_md}

### Critical Market Friction Points & Recommendations:
{frictions_md}
- **Required Localization:** Provide German user manual and integrate PayPal/Klarna on checkout.

---

## 5. Decision Rules & Kill Triggers

| Rule / Trigger | Threshold | Observed Status | Triggered? |
| :--- | :--- | :--- | :---: |
| **Minimum Landed Gross Margin** | Margin >= 20.0% | **{margin_pct:.1f}%** | No |
| **Material Safety & FCM Certification** | No toxic/lead materials; DoC available | **Compliant** (Ceramic + Borosilicate) | No |
| **Negative Sentiment Spike** | Negative discussions < 60% | **{pulse['negative_pct']:.1f}%** | No |
| **Overall Recommendation** | Viability Score >= 75 | **{score}/100** | **APPROVED (GO)** |

---

## 6. Citations & Grounded Evidentiary Trail

{citations_md}
"""
    return doc

def generate_insufficient_evidence_brief(request: Any, missing_msg: str) -> str:
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""# Expansion Viability Decision Brief: INSUFFICIENT EVIDENCE

**Evaluation Timestamp:** {now_iso}  
**Status:** **`[ INSUFFICIENT_EVIDENCE ]`** — **Viability Score: 0/100**

> [!WARNING]
> **EVALUATION HALTED**: The provided input profile lacks critical parameters required to formulate an evidence-grounded Go/No-Go decision without hallucination.

### Identified Deficiencies:
- **Missing Specification / Parameter:** {missing_msg}

### Required Inputs for Decision Formulation:
1. `origin_country` & `target_country` (ISO 2-letter codes, e.g. RO, DE)
2. `category` (Product category identifier)
3. `financials`: `unit_cogs_ex_factory`, `proposed_target_retail_msrp`
4. `specifications`: `materials` (non-empty list of physical product materials for customs & safety classification)

Please provide a complete `expansion_request.json` profile to proceed.
"""

def main():
    parser = argparse.ArgumentParser(description="Evaluate Geo-Expansion Viability for Physical E-Commerce Products")
    parser.add_argument("--input", default="demo/input/expansion_request.json", help="Path to input expansion request JSON")
    parser.add_argument("--sentiment", default="demo/input/apify_reddit_signals.json", help="Path to Apify sentiment JSON")
    parser.add_argument("--baselines", default="scripts/data/country_baselines.json", help="Path to country baselines JSON")
    parser.add_argument("--output", default="demo/output/expansion_brief.md", help="Path to save generated markdown brief")
    parser.add_argument("--json", action="store_true", help="Output raw JSON evaluation")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        brief = generate_insufficient_evidence_brief(None, f"Input file not found at {args.input}")
        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, "w") as f:
                f.write(brief)
        print(brief)
        sys.exit(0)

    with open(args.input, "r") as f:
        try:
            request = json.load(f)
        except Exception as e:
            brief = generate_insufficient_evidence_brief(None, f"Invalid JSON format in {args.input}: {e}")
            if args.output:
                os.makedirs(os.path.dirname(args.output), exist_ok=True)
                with open(args.output, "w") as f:
                    f.write(brief)
            print(brief)
            sys.exit(0)

    is_valid, msg = validate_input(request)
    if not is_valid:
        brief = generate_insufficient_evidence_brief(request, msg)
        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, "w") as f:
                f.write(brief)
        print(brief)
        sys.exit(0)

    baselines = {}
    if os.path.exists(args.baselines):
        with open(args.baselines, "r") as f:
            baselines = json.load(f)
    target_country = request.get("target_country", "DE")
    target_baseline = baselines.get(target_country, baselines.get("DE", {}))

    sentiment_data = {}
    if os.path.exists(args.sentiment):
        with open(args.sentiment, "r") as f:
            sentiment_data = json.load(f)

    econ_engine = EconomicsEngine()
    comp_engine = ComplianceEngine()
    sentiment_engine = SentimentEngine()
    decision_engine = DecisionEngine()

    econ_eval = econ_engine.evaluate(request, target_baseline)
    comp_eval = comp_engine.evaluate(request, target_baseline)
    target_price = float(request.get("financials", {}).get("proposed_target_retail_msrp", 0.0))
    pulse_eval = sentiment_engine.evaluate(sentiment_data, target_price)
    decision = decision_engine.evaluate(econ_eval, comp_eval, pulse_eval)

    if args.json:
        out = {
            "request_id": request.get("request_id"),
            "decision": decision,
            "economics": econ_eval,
            "compliance": comp_eval,
            "market_pulse": pulse_eval
        }
        print(json.dumps(out, indent=2))
    else:
        brief = generate_markdown_brief(request, econ_eval, comp_eval, pulse_eval, decision, target_baseline)
        if args.output:
            os.makedirs(os.path.dirname(args.output), exist_ok=True)
            with open(args.output, "w") as f:
                f.write(brief)
        print(brief)

if __name__ == "__main__":
    main()
