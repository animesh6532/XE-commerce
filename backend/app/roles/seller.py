from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    Product,
    Order,
    Review
)

from app.notifications.email_service import EmailService
from app.notifications.push_service import PushService
from app.notifications.sms_service import SMSService

from app.monitoring.logs import app_logger


class SellerService:

    def __init__(self):

        self.email_service = EmailService()
        self.push_service = PushService()
        self.sms_service = SMSService()

    # ==================================================
    # Dashboard Summary
    # ==================================================

    def dashboard_summary(
            self,
            db: Session
    ):

        total_products = db.query(
            func.count(Product.id)
        ).scalar()

        total_orders = db.query(
            func.count(Order.id)
        ).scalar()

        total_revenue = db.query(
            func.sum(Order.total_amount)
        ).scalar()

        return {

            "total_products":
                total_products,

            "total_orders":
                total_orders,

            "total_revenue":
                total_revenue or 0
        }

    # ==================================================
    # Product Management
    # ==================================================

    def get_products(
            self,
            db: Session
    ):

        return db.query(
            Product
        ).all()

    def get_product(
            self,
            db: Session,
            product_id: int
    ):

        return db.query(
            Product
        ).filter(
            Product.id == product_id
        ).first()

    def update_stock(
            self,
            db: Session,
            product_id: int,
            stock: int
    ):

        product = db.query(
            Product
        ).filter(
            Product.id == product_id
        ).first()

        if not product:

            return {
                "success": False,
                "message": "Product not found"
            }

        product.stock = stock

        db.commit()

        return {
            "success": True,
            "message": "Stock updated"
        }

    # ==================================================
    # Inventory Status
    # ==================================================

    def inventory_status(
            self,
            db: Session
    ):

        low_stock_products = db.query(
            Product
        ).filter(
            Product.stock < 10
        ).all()

        return {

            "low_stock_products":
                low_stock_products,

            "count":
                len(low_stock_products)
        }

    # ==================================================
    # Orders
    # ==================================================

    def get_orders(
            self,
            db: Session
    ):

        return db.query(
            Order
        ).all()

    def update_order_status(
            self,
            db: Session,
            order_id: int,
            status: str
    ):

        order = db.query(
            Order
        ).filter(
            Order.id == order_id
        ).first()

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        order.status = status

        db.commit()

        return {

            "success": True,
            "message": "Order updated"
        }

    # ==================================================
    # Sales Analytics
    # ==================================================

    def sales_statistics(
            self,
            db: Session
    ):

        revenue = db.query(
            func.sum(
                Order.total_amount
            )
        ).scalar()

        total_orders = db.query(
            func.count(
                Order.id
            )
        ).scalar()

        average_order_value = 0

        if total_orders:

            average_order_value = (
                revenue / total_orders
            )

        return {

            "total_orders":
                total_orders,

            "total_revenue":
                revenue or 0,

            "average_order_value":
                round(
                    average_order_value,
                    2
                )
        }

    # ==================================================
    # Reviews
    # ==================================================

    def get_reviews(
            self,
            db: Session
    ):

        return db.query(
            Review
        ).all()

    def average_rating(
            self,
            db: Session
    ):

        avg_rating = db.query(
            func.avg(
                Review.rating
            )
        ).scalar()

        return {

            "average_rating":
                round(
                    avg_rating or 0,
                    2
                )
        }

    # ==================================================
    # Notifications
    # ==================================================

    def send_email(
            self,
            email,
            subject,
            body
    ):

        return self.email_service.send_email(
            email,
            subject,
            body
        )

    def send_push_notification(
            self,
            user_id,
            title,
            message
    ):

        return self.push_service.send_push(
            user_id,
            title,
            message
        )

    def send_sms_notification(
            self,
            phone_number,
            message
    ):

        return self.sms_service.send_sms(
            phone_number,
            message
        )

    # ==================================================
    # Product Performance
    # ==================================================

    def product_performance(
            self,
            db: Session
    ):

        featured_products = db.query(
            Product
        ).filter(
            Product.is_featured == True
        ).count()

        return {

            "featured_products":
                featured_products
        }

    # ==================================================
    # Low Stock Alerts
    # ==================================================

    def low_stock_alerts(
            self,
            db: Session
    ):

        products = db.query(
            Product
        ).filter(
            Product.stock < 5
        ).all()

        return {

            "products":
                products,

            "count":
                len(products)
        }

    # ==================================================
    # Health
    # ==================================================

    def health(self):

        return {

            "status":
                "healthy",

            "service":
                "seller"
        }