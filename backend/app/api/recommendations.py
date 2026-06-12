from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.services.recommendation_service import RecommendationService

router = APIRouter()

recommendation_service = RecommendationService()


# ---------- Schemas ----------

class RecommendationRequest(BaseModel):
    user_id: int
    top_k: int = 10


class SimilarProductRequest(BaseModel):
    product_id: int
    top_k: int = 10


class BudgetRecommendationRequest(BaseModel):
    category: str
    budget: float
    top_k: int = 10


# ---------- Personalized Recommendations ----------

@router.get("/personalized")
def personalized_recommendations(
        top_k: int = 10,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return recommendation_service.personalized_recommendations(
        db=db,
        user_id=current_user.id,
        top_k=top_k
    )


# ---------- Similar Products ----------

@router.get("/similar/{product_id}")
def similar_products(
        product_id: int,
        top_k: int = 10,
        db: Session = Depends(get_db)
):

    return recommendation_service.similar_products(
        db=db,
        product_id=product_id,
        top_k=top_k
    )


# ---------- Content-Based Filtering ----------

@router.get("/content-based/{user_id}")
def content_based(
        user_id: int,
        top_k: int = 10
):

    return recommendation_service.content_based(
        user_id=user_id,
        top_k=top_k
    )


# ---------- Collaborative Filtering ----------

@router.get("/collaborative/{user_id}")
def collaborative(
        user_id: int,
        top_k: int = 10
):

    return recommendation_service.collaborative(
        user_id=user_id,
        top_k=top_k
    )


# ---------- Hybrid Recommendation ----------

@router.get("/hybrid/{user_id}")
def hybrid(
        user_id: int,
        top_k: int = 10
):

    return recommendation_service.hybrid(
        user_id=user_id,
        top_k=top_k
    )


# ---------- Explainable Recommendation ----------

@router.get("/explain/{product_id}")
def explain_recommendation(
        product_id: int
):

    return recommendation_service.explain_recommendation(
        product_id
    )


# ---------- Trending Products ----------

@router.get("/trending")
def trending_products():

    return recommendation_service.trending_products()


# ---------- Recently Viewed ----------

@router.get("/recently-viewed")
def recently_viewed(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return recommendation_service.recently_viewed(
        db=db,
        user_id=current_user.id
    )


# ---------- Category Recommendation ----------

@router.get("/category/{category}")
def category_recommendations(
        category: str,
        top_k: int = 10
):

    return recommendation_service.category_recommendations(
        category=category,
        top_k=top_k
    )


# ---------- Budget-Based Recommendation ----------

@router.post("/budget")
def budget_recommendations(
        request: BudgetRecommendationRequest
):

    return recommendation_service.budget_recommendations(
        category=request.category,
        budget=request.budget,
        top_k=request.top_k
    )


# ---------- Best Deals ----------

@router.get("/best-deals")
def best_deals():

    return recommendation_service.best_deals()


# ---------- Personalized Deal Feed ----------

@router.get("/deal-feed")
def personalized_deal_feed(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return recommendation_service.personalized_deal_feed(
        db=db,
        user_id=current_user.id
    )


# ---------- AI Product Comparison ----------

@router.get("/compare/{product1}/{product2}")
def compare_products(
        product1: int,
        product2: int
):

    return recommendation_service.compare_products(
        product1,
        product2
    )


# ---------- Health Check ----------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "recommendation_engine"
    }