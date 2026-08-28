"""Apify Multi-Signal Market Pulse Engine (Community Sentiment + Competitor Moat + White Space + Demand Velocity)."""

from typing import Dict, Any, List

class SentimentEngine:
    def __init__(self):
        pass

    def evaluate(self, apify_data: Dict[str, Any], target_price_eur: float = 0.0) -> Dict[str, Any]:
        # Handle both multi-signal structure and legacy aggregated_metrics
        meta = apify_data.get("actor_suite_metadata", apify_data.get("actor_metadata", {}))
        comm = apify_data.get("community_sentiment", apify_data.get("aggregated_metrics", {}))
        moat = apify_data.get("competitor_moat_analysis", {})
        defects = apify_data.get("competitor_white_space_defects", [])
        trends = apify_data.get("search_demand_velocity", {})
        
        posts_count = int(comm.get("total_posts_analyzed", 0))
        comments_count = int(comm.get("total_comments_analyzed", 0))
        total_signals = posts_count + comments_count
        
        sentiment_dist = comm.get("sentiment_distribution", {})
        positive_pct = float(sentiment_dist.get("positive_pct", 50.0))
        negative_pct = float(sentiment_dist.get("negative_pct", 10.0))
        net_score = float(comm.get("net_sentiment_score", positive_pct - negative_pct))
        
        wtp = comm.get("willingness_to_pay_range_eur", {})
        wtp_min = float(wtp.get("min", 0.0))
        wtp_max = float(wtp.get("max", 999.0))
        wtp_median = float(wtp.get("optimal_median", (wtp_min + wtp_max) / 2.0))
        
        price_within_range = (wtp_min <= target_price_eur <= wtp_max) if target_price_eur > 0 else True
        
        # 1. Sentiment component (0-100)
        normalized_net = max(0.0, min(100.0, (net_score + 100.0) / 2.0))
        sentiment_component = (0.7 * normalized_net) + (0.3 * positive_pct)
        if not price_within_range and target_price_eur > 0:
            sentiment_component = max(0.0, sentiment_component - 25.0)
            
        # 2. Competitor Moat component (0-100)
        moat_level = moat.get("moat_barrier_level", "MODERATE")
        if "LOW" in moat_level:
            moat_score = 95
        elif "MODERATE" in moat_level:
            moat_score = 80
        elif "HIGH" in moat_level:
            moat_score = 45
        else:
            moat_score = 70
            
        # 3. Search Demand Velocity component (0-100)
        growth_pct = float(trends.get("yoy_search_growth_pct", 10.0))
        if growth_pct >= 20.0:
            velocity_score = 95
        elif growth_pct >= 5.0:
            velocity_score = 80
        elif growth_pct >= -5.0:
            velocity_score = 65
        else:
            velocity_score = 40
            
        # Composite Multi-Signal Market Pulse Score (0-100)
        pulse_score = int(round((0.50 * sentiment_component) + (0.25 * moat_score) + (0.25 * velocity_score)))
        pulse_score = max(0, min(100, pulse_score))
        
        # Kill trigger: severe hostility or > 60% negative discussions
        kill_trigger = False
        kill_reason = None
        if pulse_score < 25 or negative_pct >= 60.0:
            pulse_score = min(pulse_score, 20)
            kill_trigger = True
            kill_reason = f"Severe consumer sentiment hostility detected in target community ({negative_pct:.1f}% negative reactions)."

        return {
            "market_pulse_score": pulse_score,
            "net_sentiment_score": round(net_score, 1),
            "positive_pct": round(positive_pct, 1),
            "negative_pct": round(negative_pct, 1),
            "total_signals_analyzed": total_signals,
            "price_within_willingness_range": price_within_range,
            "willingness_to_pay_median_eur": round(wtp_median, 2),
            "key_purchase_drivers": comm.get("key_purchase_drivers", []),
            "key_friction_points": comm.get("key_friction_points", []),
            "moat_barrier_level": moat_level,
            "median_competitor_reviews": moat.get("median_review_count", 0),
            "competitor_white_space_defects": defects,
            "search_demand_growth_pct": round(growth_pct, 1),
            "demand_trajectory": trends.get("demand_trajectory", "STABLE"),
            "seasonality_notes": trends.get("seasonality_note", "Standard annual distribution"),
            "actor_id": meta.get("primary_actor", meta.get("actor_id", "apify/multi-signal-suite")),
            "run_url": meta.get("run_url", "https://apify.com"),
            "retrieval_timestamp": meta.get("retrieval_timestamp", "2026-08-28"),
            "kill_trigger_triggered": kill_trigger,
            "kill_reason": kill_reason
        }
