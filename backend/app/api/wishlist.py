from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.services.wishlist_service import WishlistService

router = APIRouter()

wishlist_service = WishlistService()


# ---------- Schemas ----------

class WishlistRequest(BaseModel):
    product_id: int


# ---------- Add Product To Wishlist ----------

@router.post("/add")
def add_to_wishlist(
        request: WishlistRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.add_to_wishlist(
        db=db,
        user_id=current_user.id,
        product_id=request.product_id
    )


# ---------- Remove Product ----------

@router.delete("/remove/{product_id}")
def remove_from_wishlist(
        product_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.remove_from_wishlist(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )


# ---------- Get Wishlist ----------

@router.get("/")
def get_wishlist(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.get_wishlist(
        db=db,
        user_id=current_user.id
    )


# ---------- Clear Wishlist ----------

@router.delete("/clear")
def clear_wishlist(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.clear_wishlist(
        db=db,
        user_id=current_user.id
    )


# ---------- Move Item To Cart ----------

@router.post("/move-to-cart/{product_id}")
def move_to_cart(
        product_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.move_to_cart(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )


# ---------- Save For Later ----------

@router.post("/save-for-later/{product_id}")
def save_for_later(
        product_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.save_for_later(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )


# ---------- AI Deal Tracking ----------

@router.get("/deal-tracking")
def deal_tracking(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.deal_tracking(
        db=db,
        user_id=current_user.id
    )


# ---------- Price Drop Alerts ----------

@router.get("/price-alerts")
def price_alerts(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.price_alerts(
        db=db,
        user_id=current_user.id
    )


# ---------- Wishlist Recommendations ----------

@router.get("/recommendations")
def wishlist_recommendations(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.wishlist_recommendations(
        db=db,
        user_id=current_user.id
    )


# ---------- Wishlist Analytics ----------

@router.get("/analytics")
def wishlist_analytics(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return wishlist_service.wishlist_analytics(
        db=db,
        user_id=current_user.id
    )


# ---------- Health Check ----------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "wishlist"
    }