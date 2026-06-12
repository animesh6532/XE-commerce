from datetime import datetime
from typing import Dict

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error
)

from app.monitoring.logs import model_logger


class ModelMetrics:

    # =====================================================
    # Classification Metrics
    # =====================================================

    def classification_metrics(
            self,
            y_true,
            y_pred
    ) -> Dict:

        metrics = {

            "accuracy":
                round(
                    accuracy_score(y_true, y_pred),
                    4
                ),

            "precision":
                round(
                    precision_score(
                        y_true,
                        y_pred,
                        average="weighted",
                        zero_division=0
                    ),
                    4
                ),

            "recall":
                round(
                    recall_score(
                        y_true,
                        y_pred,
                        average="weighted",
                        zero_division=0
                    ),
                    4
                ),

            "f1_score":
                round(
                    f1_score(
                        y_true,
                        y_pred,
                        average="weighted",
                        zero_division=0
                    ),
                    4
                ),

            "timestamp":
                datetime.utcnow()
        }

        model_logger.info(
            f"Classification metrics: {metrics}"
        )

        return metrics

    # =====================================================
    # Regression Metrics
    # =====================================================

    def regression_metrics(
            self,
            y_true,
            y_pred
    ) -> Dict:

        mse = mean_squared_error(
            y_true,
            y_pred
        )

        metrics = {

            "mae":
                round(
                    mean_absolute_error(
                        y_true,
                        y_pred
                    ),
                    4
                ),

            "mse":
                round(
                    mse,
                    4
                ),

            "rmse":
                round(
                    np.sqrt(mse),
                    4
                ),

            "timestamp":
                datetime.utcnow()
        }

        model_logger.info(
            f"Regression metrics: {metrics}"
        )

        return metrics

    # =====================================================
    # Recommendation CTR
    # =====================================================

    def recommendation_ctr(
            self,
            clicks: int,
            impressions: int
    ):

        if impressions == 0:
            ctr = 0

        else:
            ctr = (
                clicks / impressions
            ) * 100

        result = {

            "ctr_percent":
                round(
                    ctr,
                    2
                ),

            "clicks":
                clicks,

            "impressions":
                impressions,

            "timestamp":
                datetime.utcnow()
        }

        model_logger.info(
            f"Recommendation CTR: {result}"
        )

        return result

    # =====================================================
    # Sentiment Model Metrics
    # =====================================================

    def sentiment_metrics(
            self,
            y_true,
            y_pred
    ):

        return self.classification_metrics(
            y_true,
            y_pred
        )

    # =====================================================
    # Fake Review Model Metrics
    # =====================================================

    def fake_review_metrics(
            self,
            y_true,
            y_pred
    ):

        return self.classification_metrics(
            y_true,
            y_pred
        )

    # =====================================================
    # Recommendation Model Metrics
    # =====================================================

    def recommendation_metrics(
            self,
            clicks,
            impressions
    ):

        return self.recommendation_ctr(
            clicks,
            impressions
        )

    # =====================================================
    # Price Prediction Metrics
    # =====================================================

    def price_prediction_metrics(
            self,
            actual_prices,
            predicted_prices
    ):

        return self.regression_metrics(
            actual_prices,
            predicted_prices
        )

    # =====================================================
    # Demand Forecast Metrics
    # =====================================================

    def demand_forecast_metrics(
            self,
            actual_demand,
            predicted_demand
    ):

        return self.regression_metrics(
            actual_demand,
            predicted_demand
        )

    # =====================================================
    # Search Model Metrics
    # =====================================================

    def semantic_search_metrics(
            self,
            y_true,
            y_pred
    ):

        return self.classification_metrics(
            y_true,
            y_pred
        )

    # =====================================================
    # Overall AI Dashboard Metrics
    # =====================================================

    def overall_metrics(
            self,
            recommendation_ctr,
            sentiment_accuracy,
            fake_review_accuracy,
            price_rmse
    ):

        result = {

            "recommendation_ctr":
                recommendation_ctr,

            "sentiment_accuracy":
                sentiment_accuracy,

            "fake_review_accuracy":
                fake_review_accuracy,

            "price_prediction_rmse":
                price_rmse,

            "timestamp":
                datetime.utcnow()
        }

        model_logger.info(
            f"Overall AI metrics: {result}"
        )

        return result