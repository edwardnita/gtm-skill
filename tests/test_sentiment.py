import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from scripts.sentiment import SentimentEngine

class TestSentimentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SentimentEngine()
        self.sample_apify_data = {
            "actor_metadata": {
                "actor_id": "trudax/reddit-scraper-lite",
                "run_id": "apify-run-20260828-coffee-de",
                "run_url": "https://api.apify.com/v2/acts/trudax~reddit-scraper-lite/runs/20260828-coffee-de",
                "dataset_public_url": "https://api.apify.com/v2/datasets/sample-gtm-coffee-de/items?format=json",
                "retrieval_timestamp": "2026-08-28T17:45:00Z"
            },
            "aggregated_metrics": {
                "total_posts_analyzed": 42,
                "total_comments_analyzed": 318,
                "sentiment_distribution": {
                    "positive_pct": 76.5,
                    "neutral_pct": 14.2,
                    "negative_pct": 9.3
                },
                "net_sentiment_score": 67.2,
                "willingness_to_pay_range_eur": { "min": 50.00, "optimal_median": 68.00, "max": 95.00 },
                "key_purchase_drivers": ["Thermal stability and ceramic craftsmanship"],
                "key_friction_points": ["Severe annoyance with non-EU customs clearance fees on UK/US orders"]
            },
            "sample_scraped_items": [
                {
                    "source_url": "https://www.reddit.com/r/Coffee/comments/1example1/",
                    "title": "Best ceramic pour over in Europe without US import customs?",
                    "subreddit": "r/Coffee"
                }
            ]
        }

    def test_evaluate_positive_sentiment(self):
        result = self.engine.evaluate(self.sample_apify_data, target_price_eur=69.00)
        self.assertGreaterEqual(result["market_pulse_score"], 70)
        self.assertFalse(result["kill_trigger_triggered"])
        self.assertEqual(result["total_signals_analyzed"], 360)
        self.assertTrue(result["price_within_willingness_range"])
        self.assertEqual(len(result["key_friction_points"]), 1)

    def test_evaluate_negative_sentiment_kill_trigger(self):
        hostile_apify_data = {
            "actor_metadata": {
                "actor_id": "trudax/reddit-scraper-lite",
                "retrieval_timestamp": "2026-08-28T17:45:00Z"
            },
            "aggregated_metrics": {
                "total_posts_analyzed": 10,
                "total_comments_analyzed": 50,
                "sentiment_distribution": {
                    "positive_pct": 10.0,
                    "neutral_pct": 10.0,
                    "negative_pct": 80.0
                },
                "net_sentiment_score": -70.0,
                "willingness_to_pay_range_eur": { "min": 10.00, "optimal_median": 20.00, "max": 30.00 },
                "key_purchase_drivers": [],
                "key_friction_points": ["Product category rejected by local community"]
            }
        }
        result = self.engine.evaluate(hostile_apify_data, target_price_eur=69.00)
        self.assertTrue(result["kill_trigger_triggered"])
        self.assertLessEqual(result["market_pulse_score"], 25)
        self.assertFalse(result["price_within_willingness_range"])

if __name__ == "__main__":
    unittest.main()
