"""Apify Market Pulse & Social Sentiment Engine."""

from typing import Dict, Any, List

class SentimentEngine:
    def __init__(self):
        pass

    def evaluate(self, apify_data: Dict[str, Any], target_price_eur: float = 0.0) -> Dict[str, Any]:
        meta = apify_data.get("actor_metadata", {})
        agg = apify_data.get("aggregated_metrics", {})
        
        posts_count = int(agg.get("total_posts_analyzed", 0))
        comments_count = int(agg.get("total_comments_analyzed", 0))
        total_signals = posts_count + comments_count
        
        sentiment_dist = agg.get("sentiment_distribution", {})
        positive_pct = float(sentiment_dist.get("positive_pct", 50.0))
        negative_pct = float(sentiment_dist.get("negative_pct", 10.0))
        net_score = float(agg.get("net_sentiment_score", positive_pct - negative_pct))
        
        wtp = agg.get("willingness_to_pay_range_eur", {})
        wtp_min = float(wtp.get("min", 0.0))
        wtp_max = float(wtp.get("max", 999.0))
        wtp_median = float(wtp.get("optimal_median", (wtp_min + wtp_max) / 2.0))
        
        price_within_range = (wtp_min <= target_price_eur <= wtp_max) if target_price_eur > 0 else True
        
        # Base market pulse score from positive sentiment & net score
        # Scale: net_score ranges from -100 to +100 -> normalize to 0 to 100
        normalized_net = max(0.0, min(100.0, (net_score + 100.0) / 2.0))
        
        # Price alignment adjustment
        price_bonus = 10 if price_within_range else -25
        
        pulse_score = int(max(0, min(100, (0.7 * normalized_net) + (0.3 * positive_pct) + price_bonus)))
        
        # Kill trigger: severely negative sentiment (< 25) or > 60% hostile discussions
        kill_trigger = False
        kill_reason = None
        if pulse_score < 25 or negative_pct >= 60.0:
            kill_trigger = True
            kill_reason = f"Severe consumer sentiment hostility detected in target community ({negative_pct:.1f}% negative reactions)."

        return {
            "market_pulse_score": pulse_score,
            "net_sentiment_score": net_score,
            "positive_pct": positive_pct,
            "negative_pct": negative_pct,
            "total_signals_analyzed": total_signals,
            "price_within_willingness_range": price_within_range,
            "willingness_to_pay_median_eur": wtp_median,
            "key_purchase_drivers": agg.get("key_purchase_drivers", []),
            "key_friction_points": agg.get("key_friction_points", []),
            "actor_id": meta.get("actor_id", "apify/reddit-scraper"),
            "run_url": meta.get("run_url", ""),
            "retrieval_timestamp": meta.get("retrieval_timestamp", ""),
            "kill_trigger_triggered": kill_trigger,
            "kill_reason": kill_reason
        }
