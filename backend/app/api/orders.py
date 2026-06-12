from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.schemas import (
    OrderCreate,
    OrderStatusUpdate,
    ReturnOrderRequest
)
from app.services.order_service import OrderService
from app.middleware.auth import get_current_user

router = APIRouter()

order_service = OrderService()


# ---------------- Place Order ----------------
@router.post("/place")
def place_order(
        order: OrderCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.place_order(
        db=db,
        user_id=current_user.id,
        order_data=order
    )


# ---------------- Get User Orders ----------------
@router.get("/")
def get_user_orders(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.get_user_orders(
        db=db,
        user_id=current_user.id
    )


# ---------------- Get Order By ID ----------------
@router.get("/{order_id}")
def get_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.get_order_by_id(
        db=db,
        user_id=current_user.id,
        order_id=order_id
    )


# ---------------- Track Order ----------------
@router.get("/track/{order_id}")
def track_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.track_order(
        db=db,
        order_id=order_id
    )


# ---------------- Cancel Order ----------------
@router.put("/cancel/{order_id}")
def cancel_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.cancel_order(
        db=db,
        user_id=current_user.id,
        order_id=order_id
    )


# ---------------- Return Order ----------------
@router.post("/return/{order_id}")
def return_order(
        order_id: int,
        request: ReturnOrderRequest,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.return_order(
        db=db,
        user_id=current_user.id,
        order_id=order_id,
        reason=request.reason
    )


# ---------------- Update Order Status (Admin) ----------------
@router.put("/status/{order_id}")
def update_order_status(
        order_id: int,
        status_data: OrderStatusUpdate,
        db: Session = Depends(get_db)
):
    return order_service.update_order_status(
        db=db,
        order_id=order_id,
        status=status_data.status
    )


# ---------------- Order Summary ----------------
@router.get("/summary")
def order_summary(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.order_summary(
        db=db,
        user_id=current_user.id
    )


# ---------------- Recent Orders ----------------
@router.get("/recent")
def recent_orders(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return order_service.recent_orders(
        db=db,
        user_id=current_user.id
    )


# ---------------- Admin: All Orders ----------------
@router.get("/admin/all")
def get_all_orders(
        db: Session = Depends(get_db)
):
    return order_service.get_all_orders(db)


# ---------------- Health Check ----------------
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "orders"
    }