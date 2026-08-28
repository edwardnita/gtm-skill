import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))

from scripts.economics import EconomicsEngine
from scripts.compliance import ComplianceEngine
from scripts.sentiment import SentimentEngine
from scripts.decision import DecisionEngine

EU_27_CODES = [
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE"
]

class TestUniversalCoverage(unittest.TestCase):
    def setUp(self):
        self.econ_engine = EconomicsEngine()
        self.comp_engine = ComplianceEngine()
        self.sentiment_engine = SentimentEngine()
        self.decision_engine = DecisionEngine()
        with open("scripts/data/country_baselines.json", "r") as f:
            self.baselines = json.load(f)

    def test_all_27_eu_countries_coverage(self):
        """Verify 100% successful evaluation across all 27 EU Member States."""
        sample_request = {
            "origin_country": "RO",
            "category": "specialty_coffee_brewing_equipment",
            "specifications": {
                "weight_grams": 650,
                "materials": ["Ceramic", "Borosilicate glass", "Silicone"],
                "food_contact_compliance": "EU EC 1935/2004 Compliant"
            },
            "financials": {
                "unit_cogs_ex_factory": 14.50,
                "proposed_target_retail_msrp": 69.00,
                "origin_export_packaging_cost": 2.10
            }
        }
        for code in EU_27_CODES:
            self.assertIn(code, self.baselines, f"Missing baseline for EU country: {code}")
            baseline = self.baselines[code]
            self.assertTrue(baseline["eu_oss_applicable"], f"EU OSS must be true for {code}")
            
            sample_request["target_country"] = code
            econ = self.econ_engine.evaluate(sample_request, baseline)
            comp = self.comp_engine.evaluate(sample_request, baseline)
            pulse = self.sentiment_engine.evaluate({}, target_price_eur=69.00)
            decision = self.decision_engine.evaluate(econ, comp, pulse)
            
            self.assertIn(decision["verdict"], ["GO", "CONDITIONAL_GO"])
            self.assertGreater(econ["landed_margin_pct"], 30.0)
            self.assertGreater(comp["compliance_score"], 80)

    def test_diverse_physical_product_categories(self):
        """Verify compliance rules for Electronics, Cosmetics, Apparel, Toys, and General Goods."""
        de_baseline = self.baselines["DE"]
        
        # 1. Electronics
        req_elec = {
            "category": "smart_audio_earbuds",
            "target_country": "DE",
            "specifications": { "materials": ["Aluminium", "Plastic"], "electrical_components": True }
        }
        res_elec = self.comp_engine.evaluate(req_elec, de_baseline)
        self.assertTrue(any("CE Mark" in a["title"] or "WEEE" in a["title"] for a in res_elec["mandatory_actions"]))

        # 2. Cosmetics / Skincare
        req_cosm = {
            "category": "organic_face_serum",
            "target_country": "DE",
            "specifications": { "materials": ["Glass bottle", "Hyaluronic acid serum", "Pump"] }
        }
        res_cosm = self.comp_engine.evaluate(req_cosm, de_baseline)
        self.assertTrue(any("CPNP" in a["title"] for a in res_cosm["mandatory_actions"]))

        # 3. Apparel / Clothing
        req_app = {
            "category": "merino_wool_sweater",
            "target_country": "DE",
            "specifications": { "materials": ["100% Merino Wool"] }
        }
        res_app = self.comp_engine.evaluate(req_app, de_baseline)
        self.assertTrue(any("Textile" in f["name"] for f in res_app["compliance_frameworks"]))

        # 4. Toys
        req_toy = {
            "category": "wooden_building_blocks_toy",
            "target_country": "DE",
            "specifications": { "materials": ["Natural beech wood", "Water-based non-toxic paint"] }
        }
        res_toy = self.comp_engine.evaluate(req_toy, de_baseline)
        self.assertTrue(any("Toy Safety" in f["name"] for f in res_toy["compliance_frameworks"]))

    def test_global_fallback_for_unknown_country(self):
        """Verify that any arbitrary unlisted ISO code in the world resolves via GLOBAL_DEFAULT."""
        unlisted_req = {
            "origin_country": "RO",
            "target_country": "NZ",  # New Zealand (unlisted)
            "category": "ergonomic_aluminum_laptop_stand",
            "specifications": { "weight_grams": 800, "materials": ["Anodized Aluminum", "Silicone pads"] },
            "financials": { "unit_cogs_ex_factory": 18.00, "proposed_target_retail_msrp": 75.00, "origin_export_packaging_cost": 2.50 }
        }
        fallback_baseline = self.baselines.get("NZ", self.baselines["GLOBAL_DEFAULT"])
        econ = self.econ_engine.evaluate(unlisted_req, fallback_baseline)
        comp = self.comp_engine.evaluate(unlisted_req, fallback_baseline)
        decision = self.decision_engine.evaluate(econ, comp, {"market_pulse_score": 75})
        
        self.assertEqual(econ["gross_msrp_eur"], 75.00)
        self.assertIn("Customs", comp["compliance_frameworks"][1]["name"])
        self.assertIn(decision["verdict"], ["GO", "CONDITIONAL_GO"])

if __name__ == "__main__":
    unittest.main()
