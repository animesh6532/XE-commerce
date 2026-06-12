from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    User,
    Product,
    Order,
    Review,
    UserActivity
)

from app.monitoring.logs import app_logger
from app.monitoring.model_metrics import ModelMetrics
from app.monitoring.drift_detection import DriftDetector

from app.notifications.email_service import EmailService
from app.notifications.push_service import PushService
from app.notifications.sms_service import SMSService


class AdminService:

    def __init__(self):

        self.email_service = EmailService()
        self.push_service = PushService()
        self.sms_service = SMSService()

        self.metrics = ModelMetrics()
        self.drift_detector = DriftDetector()

    # =================================================
    # Dashboard Summary
    # =================================================
    def dashboard_summary(
            self,
            db: Session
    ):

        total_users = db.query(
            func.count(User.id)
        ).scalar()

        total_products = db.query(
            func.count(Product.id)
        ).scalar()

        total_orders = db.query(
            func.count(Order.id)
        ).scalar()

        revenue = db.query(
            func.sum(Order.total_amount)
        ).scalar()

        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "revenue": revenue or 0
        }

    # =================================================
    # User Management
    # =================================================
    def get_all_users(
            self,
            db: Session
    ):

        return db.query(User).all()

    def deactivate_user(
            self,
            db: Session,
            user_id: int
    ):

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            return {
                "success": False,
                "message": "User not found"
            }

        user.is_active = False

        db.commit()

        return {
            "success": True,
            "message": "User deactivated"
        }

    # =================================================
    # Product Management
    # =================================================
    def get_all_products(
            self,
            db: Session
    ):

        return db.query(Product).all()

    # =================================================
    # Order Management
    # =================================================
    def get_all_orders(
            self,
            db: Session
    ):

        return db.query(Order).all()

    # =================================================
    # Review Monitoring
    # =================================================
    def get_all_reviews(
            self,
            db: Session
    ):

        return db.query(Review).all()

    # =================================================
    # Activity Monitoring
    # =================================================
    def get_user_activities(
            self,
            db: Session
    ):

        return db.query(
            UserActivity
        ).all()

    # =================================================
    # Revenue Analytics
    # =================================================
    def revenue_statistics(
            self,
            db: Session
    ):

        revenue = db.query(
            func.sum(Order.total_amount)
        ).scalar()

        orders = db.query(
            func.count(Order.id)
        ).scalar()

        return {
            "revenue": revenue or 0,
            "orders": orders
        }

    # =================================================
    # AI Metrics
    # =================================================
    def model_metrics(self):

        return {
            "message":
                "AI metrics available via monitoring/model_metrics.py"
        }

    # =================================================
    # Drift Detection
    # =================================================
    def drift_status(self):

        return {
            "message":
                "Drift status available via drift_detection.py"
        }

    # =================================================
    # Admin Alert Email
    # =================================================
    def send_admin_email(
            self,
            message
    ):

        return self.email_service.send_admin_alert(
            message
        )

    # =================================================
    # Admin Push Notification
    # =================================================
    def send_admin_push(
            self,
            message
    ):

        return self.push_service.admin_alert(
            message
        )

    # =================================================
    # Admin SMS
    # =================================================
    def send_admin_sms(
            self,
            phone_number,
            message
    ):

        return self.sms_service.admin_alert(
            phone_number,
            message
        )

    # =================================================
    # System Health
    # =================================================
    def health(self):

        return {
            "status": "healthy",
            "service": "admin"
        }