from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.schemas import (
    ReviewCreate,
    ReviewUpdate
)
from app.middleware.auth import get_current_user
from app.services.review_service import ReviewService

router = APIRouter()

review_service = ReviewService()


# ---------------- Health Check ----------------
@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "reviews"
    }


# ---------------- Add Review ----------------
@router.post("/")
def add_review(
        review: ReviewCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.add_review(
        db=db,
        user_id=current_user.id,
        review=review
    )


# ---------------- Update Review ----------------
@router.put("/{review_id}")
def update_review(
        review_id: int,
        review: ReviewUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.update_review(
        db=db,
        review_id=review_id,
        user_id=current_user.id,
        review=review
    )


# ---------------- Delete Review ----------------
@router.delete("/{review_id}")
def delete_review(
        review_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.delete_review(
        db=db,
        review_id=review_id,
        user_id=current_user.id
    )


# ---------------- Product Reviews ----------------
@router.get("/product/{product_id}")
def get_product_reviews(
        product_id: int,
        db: Session = Depends(get_db)
):

    return review_service.get_product_reviews(
        db=db,
        product_id=product_id
    )


# ---------------- User Reviews ----------------
@router.get("/my-reviews")
def get_user_reviews(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.get_user_reviews(
        db=db,
        user_id=current_user.id
    )


# ---------------- Review Details ----------------
@router.get("/{review_id}")
def get_review(
        review_id: int,
        db: Session = Depends(get_db)
):

    return review_service.get_review_by_id(
        db=db,
        review_id=review_id
    )


# ---------------- Like Review ----------------
@router.post("/{review_id}/like")
def like_review(
        review_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.like_review(
        db=db,
        review_id=review_id,
        user_id=current_user.id
    )


# ---------------- Dislike Review ----------------
@router.post("/{review_id}/dislike")
def dislike_review(
        review_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.dislike_review(
        db=db,
        review_id=review_id,
        user_id=current_user.id
    )


# ---------------- Sentiment Analysis ----------------
@router.get("/{review_id}/sentiment")
def sentiment_analysis(
        review_id: int
):

    return review_service.sentiment_analysis(
        review_id
    )


# ---------------- Fake Review Detection ----------------
@router.get("/{review_id}/fake-review")
def detect_fake_review(
        review_id: int
):

    return review_service.detect_fake_review(
        review_id
    )


# ---------------- Review Summary ----------------
@router.get("/summary/{product_id}")
def review_summary(
        product_id: int
):

    return review_service.review_summary(
        product_id
    )


# ---------------- Top Reviews ----------------
@router.get("/top/{product_id}")
def top_reviews(
        product_id: int
):

    return review_service.top_reviews(
        product_id
    )


# ---------------- Verify Purchase ----------------
@router.get("/verify-purchase/{product_id}")
def verify_purchase(
        product_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return review_service.verify_purchase(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )

