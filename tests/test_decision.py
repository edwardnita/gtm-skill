import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from scripts.decision import DecisionEngine

class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DecisionEngine()

    def test_go_verdict(self):
        econ_eval = {"economics_score": 100, "kill_trigger_triggered": False, "kill_reason": None}
        comp_eval = {"compliance_score": 95, "kill_trigger_triggered": False, "kill_reason": None}
        pulse_eval = {"market_pulse_score": 85, "kill_trigger_triggered": False, "kill_reason": None}
        
        result = self.engine.evaluate(econ_eval, comp_eval, pulse_eval)
        # Viability = 0.40*100 + 0.35*95 + 0.25*85 = 40 + 33.25 + 21.25 = 94.5 -> 95
        self.assertEqual(result["verdict"], "GO")
        self.assertGreaterEqual(result["viability_score"], 90)
        self.assertFalse(result["kill_trigger_active"])

    def test_conditional_go_verdict(self):
        econ_eval = {"economics_score": 70, "kill_trigger_triggered": False, "kill_reason": None}
        comp_eval = {"compliance_score": 60, "kill_trigger_triggered": False, "kill_reason": None}
        pulse_eval = {"market_pulse_score": 60, "kill_trigger_triggered": False, "kill_reason": None}
        
        result = self.engine.evaluate(econ_eval, comp_eval, pulse_eval)
        # Viability = 0.40*70 + 0.35*60 + 0.25*60 = 28 + 21 + 15 = 64
        self.assertEqual(result["verdict"], "CONDITIONAL_GO")
        self.assertEqual(result["viability_score"], 64)
        self.assertFalse(result["kill_trigger_active"])

    def test_hard_kill_trigger_overrides_score_to_no_go(self):
        econ_eval = {"economics_score": 100, "kill_trigger_triggered": False, "kill_reason": None}
        comp_eval = {"compliance_score": 0, "kill_trigger_triggered": True, "kill_reason": "Lead in glaze"}
        pulse_eval = {"market_pulse_score": 90, "kill_trigger_triggered": False, "kill_reason": None}
        
        result = self.engine.evaluate(econ_eval, comp_eval, pulse_eval)
        self.assertEqual(result["verdict"], "NO_GO")
        self.assertTrue(result["kill_trigger_active"])
        self.assertEqual(len(result["active_kill_reasons"]), 1)
        self.assertIn("Lead", result["active_kill_reasons"][0])

if __name__ == "__main__":
    unittest.main()
