import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from scripts.compliance import ComplianceEngine

class TestComplianceEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ComplianceEngine()
        self.sample_request = {
            "origin_country": "RO",
            "target_country": "DE",
            "category": "specialty_coffee_brewing_equipment",
            "specifications": {
                "weight_grams": 650,
                "materials": [
                    "High-fired thermal ceramic dripper",
                    "Borosilicate heat-resistant glass carafe",
                    "BPA-free food-grade silicone collar",
                    "Recycled kraft cardboard packaging"
                ],
                "food_contact_compliance": "EU EC 1935/2004 & German LFGB Compliant"
            }
        }
        self.sample_country_baseline = {
            "country_name": "Germany",
            "packaging_compliance": {
                "framework": "VerpackG (German Packaging Act)",
                "register": "LUCID (Zentrale Stelle Verpackungsregister)",
                "dual_system_mandatory": True,
                "reference_url": "https://www.verpackungsregister.org/en/"
            },
            "food_contact_compliance": {
                "framework": "EU EC 1935/2004 & German LFGB §§ 30, 31",
                "declaration_required": True,
                "declaration_type": "Declaration of Compliance (DoC)",
                "reference_url": "https://www.bfr.bund.de/en/food_contact_materials-231.html"
            }
        }

    def test_compliant_evaluation(self):
        result = self.engine.evaluate(self.sample_request, self.sample_country_baseline)
        self.assertEqual(result["compliance_score"], 95)
        self.assertFalse(result["kill_trigger_triggered"])
        self.assertIn("mandatory_actions", result)
        self.assertTrue(any("LUCID" in action["title"] for action in result["mandatory_actions"]))

    def test_prohibited_material_kill_trigger(self):
        unsafe_request = {
            "origin_country": "RO",
            "target_country": "DE",
            "category": "specialty_coffee_brewing_equipment",
            "specifications": {
                "materials": ["Lead-based glaze ceramic", "Plastic"],
                "food_contact_compliance": "None"
            }
        }
        result = self.engine.evaluate(unsafe_request, self.sample_country_baseline)
        self.assertTrue(result["kill_trigger_triggered"])
        self.assertEqual(result["compliance_score"], 0)
        self.assertIn("lead-based", result["kill_reason"].lower())

if __name__ == "__main__":
    unittest.main()
