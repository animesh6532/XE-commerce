from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import (
    UserActivity,
    Cart,
    Wishlist,
    Order
)

from app.monitoring.logs import (
    activity_logger,
    error_logger
)

from app.notifications.push_service import PushService


class ActivityService:

    def __init__(self):

        self.push_service = PushService()

    # ============================================
    # Product View Tracking
    # ============================================

    def track_product_view(
            self,
            db: Session,
            user_id: int,
            product_id: int
    ):

        activity = UserActivity(
            user_id=user_id,
            activity_type="view",
            product_id=product_id,
            created_at=datetime.utcnow()
        )

        db.add(activity)
        db.commit()

        activity_logger.info(
            f"User {user_id} viewed product {product_id}"
        )

        return {
            "success": True,
            "message": "Product view tracked"
        }

    # ============================================
    # Search Tracking
    # ============================================

    def track_search(
            self,
            db: Session,
            user_id: int,
            query: str
    ):

        activity = UserActivity(
            user_id=user_id,
            activity_type="search",
            search_query=query,
            created_at=datetime.utcnow()
        )

        db.add(activity)
        db.commit()

        activity_logger.info(
            f"User {user_id} searched '{query}'"
        )

        return {
            "success": True
        }

    # ============================================
    # Product Click Tracking
    # ============================================

    def track_click(
            self,
            db: Session,
            user_id: int,
            product_id: int,
            source: str = None
    ):

        activity = UserActivity(
            user_id=user_id,
            activity_type="click",
            product_id=product_id,
            source=source,
            created_at=datetime.utcnow()
        )

        db.add(activity)
        db.commit()

        return {
            "success": True
        }

    # ============================================
    # Cart Activity
    # ============================================

    def cart_activity(
            self,
            db: Session,
            user_id: int
    ):

        cart_items = db.query(
            Cart
        ).filter(
            Cart.user_id == user_id
        ).all()

        return {
            "cart_items": cart_items,
            "count": len(cart_items)
        }

    # ============================================
    # Wishlist Activity
    # ============================================

    def wishlist_activity(
            self,
            db: Session,
            user_id: int
    ):

        wishlist = db.query(
            Wishlist
        ).filter(
            Wishlist.user_id == user_id
        ).all()

        return {
            "wishlist_items": wishlist,
            "count": len(wishlist)
        }

    # ============================================
    # Purchase History
    # ============================================

    def purchase_history(
            self,
            db: Session,
            user_id: int
    ):

        orders = db.query(
            Order
        ).filter(
            Order.user_id == user_id
        ).all()

        return {
            "orders": orders,
            "count": len(orders)
        }

    # ============================================
    # Recently Viewed Products
    # ============================================

    def recently_viewed(
            self,
            db: Session,
            user_id: int
    ):

        activities = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "view"
        ).order_by(
            UserActivity.created_at.desc()
        ).limit(10).all()

        return {
            "recent_views": activities
        }

    # ============================================
    # Session Analytics
    # ============================================

    def session_analytics(
            self,
            db: Session,
            user_id: int
    ):

        total_activities = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id
        ).count()

        return {
            "total_activities": total_activities
        }

    # ============================================
    # User Behavior Analytics
    # ============================================

    def behavior_analytics(
            self,
            db: Session,
            user_id: int
    ):

        views = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "view"
        ).count()

        clicks = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "click"
        ).count()

        searches = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "search"
        ).count()

        return {

            "views": views,
            "clicks": clicks,
            "searches": searches
        }

    # ============================================
    # User Preferences
    # ============================================

    def user_preferences(
            self,
            db: Session,
            user_id: int
    ):

        return {
            "message":
            "Preference analysis connected to recommendation engine"
        }

    # ============================================
    # Activity Summary
    # ============================================

    def activity_summary(
            self,
            db: Session,
            user_id: int
    ):

        cart_count = db.query(
            Cart
        ).filter(
            Cart.user_id == user_id
        ).count()

        wishlist_count = db.query(
            Wishlist
        ).filter(
            Wishlist.user_id == user_id
        ).count()

        order_count = db.query(
            Order
        ).filter(
            Order.user_id == user_id
        ).count()

        return {

            "cart_items": cart_count,

            "wishlist_items": wishlist_count,

            "orders": order_count
        }

    # ============================================
    # Health Check
    # ============================================

    def health(self):

        return {

            "status": "healthy",

            "service": "activity_service"
        }