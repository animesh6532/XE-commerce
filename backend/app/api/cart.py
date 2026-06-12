from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.schemas import (
    CartCreate,
    CartUpdate,
    CouponRequest
)
from app.services.cart_service import CartService
from app.middleware.auth import get_current_user

router = APIRouter()

cart_service = CartService()


# ---------------- Add Item To Cart ----------------
@router.post("/add")
def add_to_cart(
    cart: CartCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.add_to_cart(
        db=db,
        user_id=current_user.id,
        cart_data=cart
    )


# ---------------- Get User Cart ----------------
@router.get("/")
def get_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.get_cart(
        db=db,
        user_id=current_user.id
    )


# ---------------- Update Quantity ----------------
@router.put("/update/{product_id}")
def update_quantity(
    product_id: int,
    cart: CartUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.update_quantity(
        db=db,
        user_id=current_user.id,
        product_id=product_id,
        quantity=cart.quantity
    )


# ---------------- Remove Product ----------------
@router.delete("/remove/{product_id}")
def remove_from_cart(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.remove_from_cart(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )


# ---------------- Clear Cart ----------------
@router.delete("/clear")
def clear_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.clear_cart(
        db=db,
        user_id=current_user.id
    )


# ---------------- Cart Summary ----------------
@router.get("/summary")
def cart_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.cart_summary(
        db=db,
        user_id=current_user.id
    )


# ---------------- Apply Coupon ----------------
@router.post("/apply-coupon")
def apply_coupon(
    coupon: CouponRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.apply_coupon(
        db=db,
        user_id=current_user.id,
        coupon_code=coupon.code
    )


# ---------------- Save For Later ----------------
@router.post("/save-for-later/{product_id}")
def save_for_later(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.save_for_later(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )


# ---------------- Move To Wishlist ----------------
@router.post("/move-to-wishlist/{product_id}")
def move_to_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.move_to_wishlist(
        db=db,
        user_id=current_user.id,
        product_id=product_id
    )


# ---------------- Checkout Preview ----------------
@router.get("/checkout-preview")
def checkout_preview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return cart_service.checkout_preview(
        db=db,
        user_id=current_user.id
    )