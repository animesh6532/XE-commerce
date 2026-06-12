from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Product,
    Order,
    Wishlist,
    Cart,
    Review,
    UserActivity
)

from app.notifications.email_service import EmailService
from app.notifications.push_service import PushService
from app.notifications.sms_service import SMSService

from app.monitoring.logs import app_logger


class CustomerService:

    def __init__(self):

        self.email_service = EmailService()
        self.push_service = PushService()
        self.sms_service = SMSService()

    # ===================================================
    # Profile
    # ===================================================

    def get_profile(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(User).filter(
            User.id == user_id
        ).first()

    # ===================================================
    # Orders
    # ===================================================

    def get_orders(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Order).filter(
            Order.user_id == user_id
        ).all()

    # ===================================================
    # Wishlist
    # ===================================================

    def get_wishlist(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Wishlist).filter(
            Wishlist.user_id == user_id
        ).all()

    # ===================================================
    # Cart
    # ===================================================

    def get_cart(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Cart).filter(
            Cart.user_id == user_id
        ).all()

    # ===================================================
    # Reviews
    # ===================================================

    def get_reviews(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Review).filter(
            Review.user_id == user_id
        ).all()

    # ===================================================
    # Recently Viewed Products
    # ===================================================

    def recently_viewed(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(UserActivity).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "view"
        ).all()

    # ===================================================
    # Purchase History
    # ===================================================

    def purchase_history(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Order).filter(
            Order.user_id == user_id
        ).all()

    # ===================================================
    # Favorite Categories
    # ===================================================

    def favorite_categories(
            self,
            db: Session,
            user_id: int
    ):

        activities = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id
        ).all()

        return {
            "message":
                "Category preference analysis available"
        }

    # ===================================================
    # Send Order Confirmation
    # ===================================================

    def send_order_notification(
            self,
            email,
            order_id,
            amount
    ):

        return self.email_service.send_order_confirmation(
            email,
            order_id,
            amount
        )

    # ===================================================
    # Price Drop Alert
    # ===================================================

    def price_drop_alert(
            self,
            email,
            product_name,
            old_price,
            new_price
    ):

        return self.email_service.send_price_drop_alert(
            email,
            product_name,
            old_price,
            new_price
        )

    # ===================================================
    # Push Notification
    # ===================================================

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

    # ===================================================
    # SMS Notification
    # ===================================================

    def send_sms_notification(
            self,
            phone_number,
            message
    ):

        return self.sms_service.send_sms(
            phone_number,
            message
        )

    # ===================================================
    # Recommendation Dashboard
    # ===================================================

    def recommendation_dashboard(
            self,
            user_id
    ):

        return {
            "message":
                "Recommendation engine connected"
        }

    # ===================================================
    # Deal Feed
    # ===================================================

    def personalized_deal_feed(
            self,
            user_id
    ):

        return {
            "message":
                "AI personalized deal feed available"
        }

    # ===================================================
    # Activity Summary
    # ===================================================

    def activity_summary(
            self,
            db: Session,
            user_id: int
    ):

        total_orders = db.query(Order).filter(
            Order.user_id == user_id
        ).count()

        total_reviews = db.query(Review).filter(
            Review.user_id == user_id
        ).count()

        total_wishlist = db.query(Wishlist).filter(
            Wishlist.user_id == user_id
        ).count()

        return {

            "total_orders":
                total_orders,

            "total_reviews":
                total_reviews,

            "wishlist_items":
                total_wishlist
        }

    # ===================================================
    # Health
    # ===================================================

    def health(self):

        return {

            "status":
                "healthy",

            "service":
                "customer"
        }