"""Universal Physical Product Unit Economics & Landed Cost Benchmark Engine."""

import statistics
from typing import Dict, Any, List

class EconomicsEngine:
    def __init__(self):
        pass

    def evaluate(self, request: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        fin = request.get("financials", {})
        cogs = float(fin.get("unit_cogs_ex_factory", 0.0))
        packaging_cost = float(fin.get("origin_export_packaging_cost", 0.0))
        msrp = float(fin.get("proposed_target_retail_msrp", 0.0))
        
        specs = request.get("specifications", {})
        weight_grams = float(specs.get("weight_grams", 500.0))
        
        vat_rate = float(baseline.get("standard_vat_rate", 0.20))
        packaging_fee = float(baseline.get("packaging_compliance", {}).get("per_unit_packaging_fee_eur", 0.08))
        
        # Base freight calculation (scales with weight)
        base_freight = float(baseline.get("logistics_baseline", {}).get("standard_intra_eu_freight_eur", 7.00))
        if weight_grams > 1000.0:
            weight_factor = 1.0 + ((weight_grams - 1000.0) / 1000.0) * 0.40
            freight = base_freight * weight_factor
        else:
            freight = base_freight
        
        # Net revenue calculation: MSRP = Net Revenue * (1 + VAT/Duty)
        net_revenue = msrp / (1.0 + vat_rate) if (1.0 + vat_rate) > 0 else msrp
        vat_amount = msrp - net_revenue
        
        # Landed cost
        landed_cost_ex_vat = cogs + packaging_cost + freight + packaging_fee
        total_landed_cost = landed_cost_ex_vat + vat_amount
        
        gross_profit = msrp - total_landed_cost
        landed_margin_pct = (gross_profit / msrp * 100.0) if msrp > 0 else 0.0
        
        # Competitor benchmarks
        benchmarks: List[Dict[str, Any]] = request.get("local_competitor_benchmarks", [])
        prices = [float(b.get("price_eur", 0.0)) for b in benchmarks if b.get("price_eur")]
        competitor_median = statistics.median(prices) if prices else msrp
        price_to_median_ratio = (msrp / competitor_median) if competitor_median > 0 else 1.0
        
        # Margin scoring: >50% -> 100, 35-50% -> 70, 20-34% -> 40, <20% -> 0
        kill_trigger = False
        kill_reason = None
        
        if landed_margin_pct >= 50.0:
            margin_score = 100
        elif landed_margin_pct >= 35.0:
            margin_score = 70
        elif landed_margin_pct >= 20.0:
            margin_score = 40
        else:
            margin_score = 0
            kill_trigger = True
            kill_reason = f"Landed gross margin ({landed_margin_pct:.1f}%) is below the minimum viable 20.0% threshold."
            
        # Price competitiveness penalty
        if price_to_median_ratio > 1.30:
            economics_score = max(0, margin_score - 20)
        else:
            economics_score = margin_score

        return {
            "gross_msrp_eur": round(msrp, 2),
            "net_revenue_eur": round(net_revenue, 2),
            "vat_amount_eur": round(vat_amount, 2),
            "cogs_eur": round(cogs, 2),
            "packaging_cost_eur": round(packaging_cost, 2),
            "freight_eur": round(freight, 2),
            "packaging_fee_eur": round(packaging_fee, 2),
            "landed_cost_ex_vat_eur": round(landed_cost_ex_vat, 2),
            "landed_cost_eur": round(total_landed_cost, 2),
            "gross_profit_eur": round(gross_profit, 2),
            "landed_margin_pct": round(landed_margin_pct, 1),
            "competitor_median_price_eur": round(competitor_median, 2),
            "price_to_competitor_median_ratio": round(price_to_median_ratio, 2),
            "economics_score": economics_score,
            "kill_trigger_triggered": kill_trigger,
            "kill_reason": kill_reason
        }
