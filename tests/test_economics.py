import unittest
import sys
import os

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath("."))

from scripts.economics import EconomicsEngine

class TestEconomicsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EconomicsEngine()
        self.sample_request = {
            "origin_country": "RO",
            "target_country": "DE",
            "financials": {
                "unit_cogs_ex_factory": 14.50,
                "proposed_target_retail_msrp": 69.00,
                "origin_export_packaging_cost": 2.10
            },
            "local_competitor_benchmarks": [
                {"name": "Comp A", "price_eur": 54.90},
                {"name": "Comp B", "price_eur": 89.00},
                {"name": "Comp C", "price_eur": 72.50}
            ]
        }
        self.sample_country_baseline = {
            "standard_vat_rate": 0.19,
            "packaging_compliance": {"per_unit_packaging_fee_eur": 0.08},
            "logistics_baseline": {"standard_intra_eu_freight_eur": 6.80}
        }

    def test_calculate_landed_cost(self):
        result = self.engine.evaluate(self.sample_request, self.sample_country_baseline)
        
        # Net MSRP = 69.00 / 1.19 = ~57.98 EUR
        # VAT = 69.00 - 57.98 = ~11.02 EUR
        # Total Landed Cost = COGS (14.50) + Packaging (2.10) + Freight (6.80) + Packaging Fee (0.08) + VAT (11.02) = ~34.50 EUR
        self.assertIn("landed_cost_eur", result)
        self.assertAlmostEqual(result["landed_cost_eur"], 34.50, delta=0.5)
        self.assertAlmostEqual(result["net_revenue_eur"], 57.98, delta=0.5)

    def test_calculate_margin_and_competitor_benchmark(self):
        result = self.engine.evaluate(self.sample_request, self.sample_country_baseline)
        
        # Competitor Median = median(54.90, 72.50, 89.00) = 72.50
        self.assertEqual(result["competitor_median_price_eur"], 72.50)
        self.assertAlmostEqual(result["price_to_competitor_median_ratio"], 69.00 / 72.50, places=2)
        
        # Gross profit = 69.00 - 34.50 = 34.50
        # Margin % = (34.50 / 69.00) = 50.0%
        self.assertGreaterEqual(result["landed_margin_pct"], 45.0)
        self.assertEqual(result["economics_score"], 100)
        self.assertFalse(result["kill_trigger_triggered"])

    def test_low_margin_kill_trigger(self):
        unviable_request = {
            "origin_country": "RO",
            "target_country": "DE",
            "financials": {
                "unit_cogs_ex_factory": 45.00,
                "proposed_target_retail_msrp": 50.00,
                "origin_export_packaging_cost": 5.00
            },
            "local_competitor_benchmarks": [{"price_eur": 50.00}]
        }
        result = self.engine.evaluate(unviable_request, self.sample_country_baseline)
        self.assertTrue(result["kill_trigger_triggered"])
        self.assertEqual(result["economics_score"], 0)

if __name__ == "__main__":
    unittest.main()
