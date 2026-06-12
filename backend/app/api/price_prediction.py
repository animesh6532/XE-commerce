from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.price_prediction_service import PricePredictionService

router = APIRouter()

price_service = PricePredictionService()


# ---------------- Pydantic Schemas ----------------

class PricePredictionRequest(BaseModel):
    product_id: int


class BulkPredictionRequest(BaseModel):
    product_ids: List[int]


class PriceComparisonRequest(BaseModel):
    product_ids: List[int]


# ---------------- Predict Future Price ----------------

@router.post("/predict")
def predict_price(request: PricePredictionRequest):
    try:
        result = price_service.predict_price(request.product_id)

        return {
            "success": True,
            "prediction": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Price Trend ----------------

@router.get("/trend/{product_id}")
def price_trend(product_id: int):
    try:
        return price_service.price_trend(product_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Historical Prices ----------------

@router.get("/history/{product_id}")
def price_history(product_id: int):
    try:
        return price_service.price_history(product_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Best Time To Buy ----------------

@router.get("/best-time/{product_id}")
def best_time_to_buy(product_id: int):
    try:
        return price_service.best_time_to_buy(product_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- AI Deal Score ----------------

@router.get("/deal-score/{product_id}")
def deal_score(product_id: int):
    try:
        return price_service.deal_score(product_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Price Comparison ----------------

@router.post("/compare")
def compare_prices(request: PriceComparisonRequest):
    try:
        return price_service.compare_prices(
            request.product_ids
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Bulk Prediction ----------------

@router.post("/bulk-predict")
def bulk_predict(request: BulkPredictionRequest):
    try:
        return price_service.bulk_predict(
            request.product_ids
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Model Metrics ----------------

@router.get("/metrics")
def model_metrics():
    try:
        return price_service.model_metrics()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Health Check ----------------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "price_prediction"
    }