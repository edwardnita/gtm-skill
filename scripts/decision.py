"""Composite Scoring & Decision Engine."""

from typing import Dict, Any, List

class DecisionEngine:
    def __init__(self, econ_weight: float = 0.40, comp_weight: float = 0.35, pulse_weight: float = 0.25):
        self.econ_weight = econ_weight
        self.comp_weight = comp_weight
        self.pulse_weight = pulse_weight

    def evaluate(self, econ_eval: Dict[str, Any], comp_eval: Dict[str, Any], pulse_eval: Dict[str, Any]) -> Dict[str, Any]:
        econ_score = float(econ_eval.get("economics_score", 0))
        comp_score = float(comp_eval.get("compliance_score", 0))
        pulse_score = float(pulse_eval.get("market_pulse_score", 0))
        
        # Check for kill triggers
        active_kill_reasons = []
        if econ_eval.get("kill_trigger_triggered"):
            active_kill_reasons.append(econ_eval.get("kill_reason", "Economics failure"))
        if comp_eval.get("kill_trigger_triggered"):
            active_kill_reasons.append(comp_eval.get("kill_reason", "Compliance failure"))
        if pulse_eval.get("kill_trigger_triggered"):
            active_kill_reasons.append(pulse_eval.get("kill_reason", "Market sentiment failure"))
            
        has_kill_trigger = len(active_kill_reasons) > 0
        
        raw_viability = (self.econ_weight * econ_score) + (self.comp_weight * comp_score) + (self.pulse_weight * pulse_score)
        viability_score = int(round(raw_viability))
        
        if has_kill_trigger:
            verdict = "NO_GO"
            viability_score = min(viability_score, 30)
            confidence = "HIGH (Kill Trigger Active)"
            executive_rationale = f"Expansion aborted due to critical risk: {active_kill_reasons[0]}"
        elif viability_score >= 75:
            verdict = "GO"
            confidence = "HIGH"
            executive_rationale = "Strong economic margin cushion, clear compliance pathways, and favorable target market consumer sentiment."
        elif viability_score >= 50:
            verdict = "CONDITIONAL_GO"
            confidence = "MEDIUM"
            executive_rationale = "Expansion is viable with localized adjustments (e.g. margin optimization or certification resolution)."
        else:
            verdict = "NO_GO"
            confidence = "HIGH"
            executive_rationale = "Unfavorable unit economics or significant friction points render expansion unprofitable under current parameters."

        return {
            "verdict": verdict,
            "viability_score": viability_score,
            "confidence": confidence,
            "executive_rationale": executive_rationale,
            "pillar_breakdown": {
                "economics_score": int(econ_score),
                "compliance_score": int(comp_score),
                "market_pulse_score": int(pulse_score)
            },
            "kill_trigger_active": has_kill_trigger,
            "active_kill_reasons": active_kill_reasons
        }
