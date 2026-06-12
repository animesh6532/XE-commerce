import numpy as np
from scipy.stats import ks_2samp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DriftDetector:

    def __init__(self, threshold=0.05):
        """
        threshold:
        p-value below threshold indicates drift.
        """
        self.threshold = threshold

    # =====================================================
    # Numerical Feature Drift Detection
    # =====================================================
    def detect_feature_drift(
            self,
            reference_data,
            current_data,
            feature_name="feature"
    ):

        statistic, p_value = ks_2samp(
            reference_data,
            current_data
        )

        drift_detected = p_value < self.threshold

        result = {
            "feature": feature_name,
            "drift_detected": drift_detected,
            "ks_statistic": round(statistic, 4),
            "p_value": round(p_value, 6),
            "timestamp": datetime.utcnow()
        }

        logger.info(
            f"Drift Check [{feature_name}] -> "
            f"Drift={drift_detected}"
        )

        return result

    # =====================================================
    # Prediction Drift
    # =====================================================
    def detect_prediction_drift(
            self,
            old_predictions,
            new_predictions
    ):

        statistic, p_value = ks_2samp(
            old_predictions,
            new_predictions
        )

        drift_detected = p_value < self.threshold

        return {
            "drift_detected": drift_detected,
            "ks_statistic": round(statistic, 4),
            "p_value": round(p_value, 6),
            "timestamp": datetime.utcnow()
        }

    # =====================================================
    # Recommendation Drift
    # =====================================================
    def recommendation_drift(
            self,
            historical_scores,
            recent_scores
    ):

        return self.detect_prediction_drift(
            historical_scores,
            recent_scores
        )

    # =====================================================
    # Sentiment Drift
    # =====================================================
    def sentiment_drift(
            self,
            old_sentiments,
            new_sentiments
    ):

        return self.detect_prediction_drift(
            old_sentiments,
            new_sentiments
        )

    # =====================================================
    # Price Prediction Drift
    # =====================================================
    def price_prediction_drift(
            self,
            old_prices,
            new_prices
    ):

        return self.detect_prediction_drift(
            old_prices,
            new_prices
        )

    # =====================================================
    # Demand Forecast Drift
    # =====================================================
    def demand_forecast_drift(
            self,
            historical_demand,
            current_demand
    ):

        return self.detect_prediction_drift(
            historical_demand,
            current_demand
        )

    # =====================================================
    # Search Embedding Drift
    # =====================================================
    def search_drift(
            self,
            old_embeddings,
            new_embeddings
    ):

        return self.detect_prediction_drift(
            old_embeddings,
            new_embeddings
        )

    # =====================================================
    # Overall Drift Summary
    # =====================================================
    def overall_summary(
            self,
            recommendation_result,
            sentiment_result,
            price_result,
            demand_result
    ):

        drift_count = sum([
            recommendation_result["drift_detected"],
            sentiment_result["drift_detected"],
            price_result["drift_detected"],
            demand_result["drift_detected"]
        ])

        return {
            "overall_status":
                "RETRAIN_REQUIRED"
                if drift_count > 1
                else "NORMAL",

            "models_with_drift": drift_count,

            "recommendation_model":
                recommendation_result,

            "sentiment_model":
                sentiment_result,

            "price_prediction_model":
                price_result,

            "demand_forecast_model":
                demand_result,

            "timestamp":
                datetime.utcnow()
        }