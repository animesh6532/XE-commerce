from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.services.sentiment_service import SentimentService

router = APIRouter()

sentiment_service = SentimentService()


# ---------- Schemas ----------

class SentimentRequest(BaseModel):
    text: str


class BatchSentimentRequest(BaseModel):
    reviews: List[str]


# ---------- Single Review Sentiment ----------

@router.post("/analyze")
def analyze_sentiment(
        request: SentimentRequest
):

    return sentiment_service.analyze_sentiment(
        request.text
    )


# ---------- Batch Sentiment ----------

@router.post("/batch")
def batch_sentiment_analysis(
        request: BatchSentimentRequest
):

    return sentiment_service.batch_sentiment_analysis(
        request.reviews
    )


# ---------- Product Sentiment Summary ----------

@router.get("/product/{product_id}")
def product_sentiment(
        product_id: int,
        db: Session = Depends(get_db)
):

    return sentiment_service.product_sentiment(
        db=db,
        product_id=product_id
    )


# ---------- Review Sentiment ----------

@router.get("/review/{review_id}")
def review_sentiment(
        review_id: int,
        db: Session = Depends(get_db)
):

    return sentiment_service.review_sentiment(
        db=db,
        review_id=review_id
    )


# ---------- User Sentiment History ----------

@router.get("/history")
def sentiment_history(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return sentiment_service.sentiment_history(
        db=db,
        user_id=current_user.id
    )


# ---------- Positive Reviews ----------

@router.get("/positive/{product_id}")
def positive_reviews(
        product_id: int,
        db: Session = Depends(get_db)
):

    return sentiment_service.positive_reviews(
        db=db,
        product_id=product_id
    )


# ---------- Negative Reviews ----------

@router.get("/negative/{product_id}")
def negative_reviews(
        product_id: int,
        db: Session = Depends(get_db)
):

    return sentiment_service.negative_reviews(
        db=db,
        product_id=product_id
    )


# ---------- Neutral Reviews ----------

@router.get("/neutral/{product_id}")
def neutral_reviews(
        product_id: int,
        db: Session = Depends(get_db)
):

    return sentiment_service.neutral_reviews(
        db=db,
        product_id=product_id
    )


# ---------- Sentiment Statistics ----------

@router.get("/statistics")
def sentiment_statistics():

    return sentiment_service.sentiment_statistics()


# ---------- Product Rating Insights ----------

@router.get("/insights/{product_id}")
def product_insights(
        product_id: int,
        db: Session = Depends(get_db)
):

    return sentiment_service.product_insights(
        db=db,
        product_id=product_id
    )


# ---------- Trending Opinions ----------

@router.get("/trending")
def trending_opinions():

    return sentiment_service.trending_opinions()


# ---------- Dashboard Data ----------

@router.get("/dashboard")
def dashboard():

    return sentiment_service.dashboard_data()


# ---------- Health Check ----------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "sentiment_analysis"
    }