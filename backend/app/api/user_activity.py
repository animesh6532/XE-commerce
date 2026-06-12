from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.services.activity_service import ActivityService

router = APIRouter()

activity_service = ActivityService()


# ---------- Schemas ----------

class ProductViewRequest(BaseModel):
    product_id: int


class SearchActivityRequest(BaseModel):
    query: str


class ClickActivityRequest(BaseModel):
    product_id: int
    source: Optional[str] = None


# ---------- Product View Tracking ----------

@router.post("/view")
def track_product_view(
        request: ProductViewRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.track_product_view(
        db=db,
        user_id=current_user.id,
        product_id=request.product_id
    )


# ---------- Search Tracking ----------

@router.post("/search")
def track_search(
        request: SearchActivityRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.track_search(
        db=db,
        user_id=current_user.id,
        query=request.query
    )


# ---------- Product Click Tracking ----------

@router.post("/click")
def track_click(
        request: ClickActivityRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.track_click(
        db=db,
        user_id=current_user.id,
        product_id=request.product_id,
        source=request.source
    )


# ---------- Cart Activity ----------

@router.get("/cart")
def cart_activity(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.cart_activity(
        db=db,
        user_id=current_user.id
    )


# ---------- Wishlist Activity ----------

@router.get("/wishlist")
def wishlist_activity(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.wishlist_activity(
        db=db,
        user_id=current_user.id
    )


# ---------- Purchase History ----------

@router.get("/purchases")
def purchase_history(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.purchase_history(
        db=db,
        user_id=current_user.id
    )


# ---------- Recently Viewed Products ----------

@router.get("/recently-viewed")
def recently_viewed(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.recently_viewed(
        db=db,
        user_id=current_user.id
    )


# ---------- Session Analytics ----------

@router.get("/session")
def session_analytics(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.session_analytics(
        db=db,
        user_id=current_user.id
    )


# ---------- User Behavior Analytics ----------

@router.get("/behavior")
def behavior_analytics(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.behavior_analytics(
        db=db,
        user_id=current_user.id
    )


# ---------- Recommendation Features ----------

@router.get("/preferences")
def user_preferences(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.user_preferences(
        db=db,
        user_id=current_user.id
    )


# ---------- Dashboard Summary ----------

@router.get("/summary")
def activity_summary(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return activity_service.activity_summary(
        db=db,
        user_id=current_user.id
    )


# ---------- Health Check ----------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "user_activity"
    }