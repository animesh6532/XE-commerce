from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import (
    Order,
    Cart,
    Product
)

from app.notifications.email_service import EmailService
from app.notifications.push_service import PushService
from app.notifications.sms_service import SMSService

from app.monitoring.logs import (
    app_logger,
    error_logger
)


class OrderService:

    def __init__(self):

        self.email_service = EmailService()
        self.push_service = PushService()
        self.sms_service = SMSService()

    # =================================================
    # Place Order
    # =================================================
    def place_order(
            self,
            db: Session,
            user_id: int,
            shipping_address: str = None,
            payment_method: str = None,
            order_data = None
    ):
        if order_data is not None:
            shipping_address = order_data.shipping_address
            payment_method = order_data.payment_method

        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id
        ).all()

        if not cart_items:

            return {
                "success": False,
                "message": "Cart is empty"
            }

        total_amount = 0

        for item in cart_items:

            product = db.query(Product).filter(
                Product.id == item.product_id
            ).first()

            if product:

                total_amount += (
                    product.price * item.quantity
                )

        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            payment_method=payment_method,
            shipping_address=shipping_address,
            status="Pending",
            created_at=datetime.utcnow()
        )

        db.add(order)

        # Clear cart after order
        for item in cart_items:
            db.delete(item)

        db.commit()
        db.refresh(order)

        app_logger.info(
            f"Order {order.id} created by user {user_id}"
        )

        return {
            "success": True,
            "order_id": order.id,
            "total_amount": total_amount
        }

    # =================================================
    # Get Order By ID
    # =================================================
    def get_order(
            self,
            db: Session,
            order_id: int
    ):

        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        return order

    # =================================================
    # Get User Orders
    # =================================================
    def get_user_orders(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Order).filter(
            Order.user_id == user_id
        ).all()

    # =================================================
    # Update Order Status
    # =================================================
    def update_order_status(
            self,
            db: Session,
            order_id: int,
            status: str
    ):

        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        order.status = status

        db.commit()

        app_logger.info(
            f"Order {order_id} updated to {status}"
        )

        return {
            "success": True,
            "message": "Order status updated"
        }

    # =================================================
    # Cancel Order
    # =================================================
    def cancel_order(
            self,
            db: Session,
            order_id: int,
            user_id: int = None
    ):

        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        order.status = "Cancelled"

        db.commit()

        return {
            "success": True,
            "message": "Order cancelled"
        }

    # =================================================
    # Mark As Shipped
    # =================================================
    def mark_shipped(
            self,
            db: Session,
            order_id: int
    ):

        return self.update_order_status(
            db,
            order_id,
            "Shipped"
        )

    # =================================================
    # Mark As Delivered
    # =================================================
    def mark_delivered(
            self,
            db: Session,
            order_id: int
    ):

        return self.update_order_status(
            db,
            order_id,
            "Delivered"
        )

    # =================================================
    # Return Order
    # =================================================
    def return_order(
            self,
            db: Session,
            order_id: int,
            reason: str,
            user_id: int = None
    ):


        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        order.status = "Returned"

        db.commit()

        return {
            "success": True,
            "reason": reason,
            "message": "Return request accepted"
        }

    # =================================================
    # Revenue Summary
    # =================================================
    def revenue_summary(
            self,
            db: Session
    ):

        orders = db.query(Order).all()

        total_revenue = sum(
            order.total_amount
            for order in orders
        )

        return {
            "total_orders": len(orders),
            "total_revenue": total_revenue
        }

    # =================================================
    # Order Analytics
    # =================================================
    def order_analytics(
            self,
            db: Session
    ):

        orders = db.query(Order).all()

        delivered = len([
            o for o in orders
            if o.status == "Delivered"
        ])

        pending = len([
            o for o in orders
            if o.status == "Pending"
        ])

        cancelled = len([
            o for o in orders
            if o.status == "Cancelled"
        ])

        return {

            "total_orders": len(orders),

            "delivered_orders": delivered,

            "pending_orders": pending,

            "cancelled_orders": cancelled
        }

    # =================================================
    # Send Order Confirmation Email
    # =================================================
    def send_confirmation_email(
            self,
            email: str,
            order_id: int,
            amount: float
    ):

        return self.email_service.send_order_confirmation(
            email,
            order_id,
            amount
        )

    # =================================================
    # Shipping Notification
    # =================================================
    def send_shipping_notification(
            self,
            user_id: int,
            order_id: int,
            status: str
    ):

        return self.push_service.shipping_update(
            user_id,
            order_id,
            status
        )

    # =================================================
    # Get Order By ID (checks user ownership and raises 404/403)
    # =================================================
    def get_order_by_id(self, db: Session, user_id: int, order_id: int):
        order = self.get_order(db, order_id)
        if isinstance(order, dict) and not order.get("success", True):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Order not found")
        if order.user_id != user_id:
            from fastapi import HTTPException
            raise HTTPException(status_code=403, detail="Not authorized to view this order")
        return order

    # =================================================
    # Track Order
    # =================================================
    def track_order(self, db: Session, order_id: int):
        order = self.get_order(db, order_id)
        if isinstance(order, dict) and not order.get("success", True):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Order not found")
        return {
            "order_id": order.id,
            "status": order.status,
            "shipping_address": order.shipping_address,
            "estimated_delivery": "Within 3-5 business days"
        }

    # =================================================
    # Order Summary
    # =================================================
    def order_summary(self, db: Session, user_id: int):
        orders = self.get_user_orders(db, user_id)
        return {
            "total_orders": len(orders),
            "total_spent": sum(o.total_amount for o in orders if o.total_amount),
            "recent_status": orders[-1].status if orders else "None"
        }

    # =================================================
    # Recent Orders
    # =================================================
    def recent_orders(self, db: Session, user_id: int):
        return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(5).all()

    # =================================================
    # Get All Orders (Admin)
    # =================================================
    def get_all_orders(self, db: Session):
        return db.query(Order).all()

    # =================================================
    # Health Check
    # =================================================
    def health(self):

        return {
            "status": "healthy",
            "service": "order_service"
        }