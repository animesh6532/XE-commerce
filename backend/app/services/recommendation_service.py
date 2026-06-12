from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.models import (
    Product,
    UserActivity,
    Wishlist,
    RecommendationHistory
)

from app.monitoring.logs import recommendation_logger
from app.notifications.push_service import PushService


class RecommendationService:

    def __init__(self):

        self.push_service = PushService()

    # =================================================
    # Personalized Recommendations
    # =================================================
    def personalized_recommendations(
            self,
            db: Session,
            user_id: int,
            limit: int = 10,
            top_k: int = None
    ):
        limit = top_k or limit
        activities = db.query(
            UserActivity
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_type == "view"
        ).all()

        viewed_product_ids = [
            activity.product_id
            for activity in activities
            if activity.product_id
        ]

        categories = []

        for product_id in viewed_product_ids:

            product = db.query(Product).filter(
                Product.id == product_id
            ).first()

            if product:
                categories.append(product.category)

        if categories:

            recommended_products = db.query(
                Product
            ).filter(
                Product.category.in_(categories)
            ).limit(limit).all()

        else:

            recommended_products = db.query(
                Product
            ).order_by(
                desc(Product.rating)
            ).limit(limit).all()

        recommendation_logger.info(
            f"Recommendations generated for user {user_id}"
        )

        return recommended_products

    # =================================================
    # Similar Products
    # =================================================
    def similar_products(
            self,
            db: Session,
            product_id: int,
            limit: int = 5,
            top_k: int = None
    ):
        limit = top_k or limit
        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            return []

        return db.query(Product).filter(
            Product.category == product.category,
            Product.id != product_id
        ).limit(limit).all()

    # =================================================
    # Category Recommendations
    # =================================================
    def category_recommendations(
            self,
            category: str,
            db: Session = None,
            limit: int = 10,
            top_k: int = None
    ):
        limit = top_k or limit
        close_session = False
        if db is None:
            from app.database.connection import SessionLocal
            db = SessionLocal()
            close_session = True
        try:
            return db.query(Product).filter(
                Product.category == category
            ).order_by(
                desc(Product.rating)
            ).limit(limit).all()
        finally:
            if close_session:
                db.close()

    # =================================================
    # Budget Recommendations
    # =================================================
    def budget_recommendations(
            self,
            category: str,
            budget: float,
            db: Session = None,
            limit: int = 10,
            top_k: int = None
    ):
        limit = top_k or limit
        close_session = False
        if db is None:
            from app.database.connection import SessionLocal
            db = SessionLocal()
            close_session = True
        try:
            return db.query(Product).filter(
                Product.category == category,
                Product.price <= budget
            ).order_by(
                desc(Product.rating)
            ).limit(limit).all()
        finally:
            if close_session:
                db.close()

    # =================================================
    # Top Rated Products
    # =================================================
    def top_rated_products(
            self,
            db: Session,
            limit: int = 10
    ):

        return db.query(Product).order_by(
            desc(Product.rating)
        ).limit(limit).all()

    # =================================================
    # Recently Viewed Recommendations
    # =================================================
    def recently_viewed_recommendations(
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
            desc(UserActivity.created_at)
        ).limit(10).all()

        return activities

    # =================================================
    # Wishlist Recommendations
    # =================================================
    def wishlist_recommendations(
            self,
            db: Session,
            user_id: int
    ):

        wishlist_items = db.query(
            Wishlist
        ).filter(
            Wishlist.user_id == user_id
        ).all()

        product_ids = [
            item.product_id
            for item in wishlist_items
        ]

        recommendations = []

        for pid in product_ids:

            recommendations.extend(
                self.similar_products(
                    db,
                    pid
                )
            )

        return recommendations

    # =================================================
    # Save Recommendation History
    # =================================================
    def save_recommendation_history(
            self,
            db: Session,
            user_id: int,
            product_id: int,
            score: float
    ):

        history = RecommendationHistory(
            user_id=user_id,
            product_id=product_id,
            score=score
        )

        db.add(history)
        db.commit()

        return {
            "success": True
        }

    # =================================================
    # Deal Score
    # =================================================
    def deal_score(
            self,
            product: Product
    ):

        score = 100

        if product.rating < 4:
            score -= 20

        if product.stock < 5:
            score -= 10

        return max(score, 0)

    # =================================================
    # Notify User
    # =================================================
    def notify_user(
            self,
            user_id: int,
            product_name: str
    ):

        return self.push_service.recommendation_notification(
            user_id,
            product_name
        )

    # =================================================
    # Recommendation Analytics
    # =================================================
    def analytics(
            self,
            db: Session
    ):

        total_recommendations = db.query(
            RecommendationHistory
        ).count()

        average_score = db.query(
            RecommendationHistory
        ).all()

        avg = 0

        if average_score:

            avg = sum(
                r.score
                for r in average_score
            ) / len(average_score)

        return {

            "total_recommendations":
                total_recommendations,

            "average_score":
                round(avg, 2)
        }

    # =================================================
    # Content-Based Filtering Recommendations
    # =================================================
    def content_based(self, user_id: int, top_k: int = 10):
        from app.database.connection import SessionLocal
        from app.database.models import Product, UserActivity
        from ml_models.recommendation.content_based import ContentBasedRecommender
        from pathlib import Path

        db = SessionLocal()
        try:
            dataset_path = Path(__file__).resolve().parent.parent.parent.parent / "ml_models" / "datasets" / "products.csv"
            recommender = ContentBasedRecommender(str(dataset_path))

            last_view = db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == "view"
            ).order_by(desc(UserActivity.created_at)).first()

            if last_view and last_view.product_id:
                product = db.query(Product).filter(Product.id == last_view.product_id).first()
                if product and product.name in recommender.df["product_name"].values:
                    recs = recommender.recommend(product.name, top_n=top_k)
                    return db.query(Product).filter(Product.name.in_(recs)).all()

            # Fallback to general rating-based
            return db.query(Product).order_by(desc(Product.rating)).limit(top_k).all()
        except Exception as e:
            recommendation_logger.error(f"Content-based recommendation error: {e}")
            return db.query(Product).order_by(desc(Product.rating)).limit(top_k).all()
        finally:
            db.close()

    # =================================================
    # Collaborative Filtering Recommendations
    # =================================================
    def collaborative(self, user_id: int, top_k: int = 10):
        from app.database.connection import SessionLocal
        from app.database.models import Product
        from ml_models.recommendation.collaborative import CollaborativeFiltering
        from pathlib import Path

        db = SessionLocal()
        try:
            dataset_path = Path(__file__).resolve().parent.parent.parent.parent / "ml_models" / "datasets" / "products.csv"
            recommender = CollaborativeFiltering(str(dataset_path))
            if user_id in recommender.df["user_id"].values:
                recs = recommender.recommend(user_id)
                return db.query(Product).filter(Product.name.in_(recs)).limit(top_k).all()
            return db.query(Product).order_by(desc(Product.rating)).limit(top_k).all()
        except Exception as e:
            recommendation_logger.error(f"Collaborative recommendation error: {e}")
            return db.query(Product).order_by(desc(Product.rating)).limit(top_k).all()
        finally:
            db.close()

    # =================================================
    # Hybrid Recommendations
    # =================================================
    def hybrid(self, user_id: int, top_k: int = 10):
        from app.database.connection import SessionLocal
        from app.database.models import Product, UserActivity
        from ml_models.recommendation.hybrid import HybridRecommender
        from pathlib import Path

        db = SessionLocal()
        try:
            dataset_path = Path(__file__).resolve().parent.parent.parent.parent / "ml_models" / "datasets" / "products.csv"
            recommender = HybridRecommender(str(dataset_path))

            last_view = db.query(UserActivity).filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == "view"
            ).order_by(desc(UserActivity.created_at)).first()

            product_name = ""
            if last_view and last_view.product_id:
                prod = db.query(Product).filter(Product.id == last_view.product_id).first()
                if prod:
                    product_name = prod.name

            if not product_name:
                prod = db.query(Product).first()
                if prod:
                    product_name = prod.name

            if product_name and product_name in recommender.content.df["product_name"].values:
                recs = recommender.recommend(user_id, product_name)
                return db.query(Product).filter(Product.name.in_(recs)).limit(top_k).all()
            return db.query(Product).order_by(desc(Product.rating)).limit(top_k).all()
        except Exception as e:
            recommendation_logger.error(f"Hybrid recommendation error: {e}")
            return db.query(Product).order_by(desc(Product.rating)).limit(top_k).all()
        finally:
            db.close()

    # =================================================
    # Explain Recommendation
    # =================================================
    def explain_recommendation(self, product_id: int):
        from ml_models.recommendation.explainability import RecommendationExplainer
        return {
            "product_id": product_id,
            "explanation": RecommendationExplainer.explain()
        }

    # =================================================
    # Trending Products
    # =================================================
    def trending_products(self):
        from app.database.connection import SessionLocal
        from app.database.models import Product
        db = SessionLocal()
        try:
            return db.query(Product).order_by(desc(Product.rating)).limit(10).all()
        finally:
            db.close()

    # =================================================
    # Recently Viewed Products Wrapper
    # =================================================
    def recently_viewed(self, db: Session, user_id: int):
        return self.recently_viewed_recommendations(db, user_id)

    # =================================================
    # Best Deals
    # =================================================
    def best_deals(self):
        from app.database.connection import SessionLocal
        from app.database.models import Product
        db = SessionLocal()
        try:
            return db.query(Product).filter(Product.is_featured == True).limit(10).all()
        finally:
            db.close()

    # =================================================
    # Personalized Deal Feed
    # =================================================
    def personalized_deal_feed(self, db: Session, user_id: int):
        recs = self.personalized_recommendations(db, user_id)
        deals = [r for r in recs if r.is_featured]
        return deals if deals else recs[:5]

    # =================================================
    # Compare Products
    # =================================================
    def compare_products(self, product1: int, product2: int):
        from app.database.connection import SessionLocal
        from app.database.models import Product
        db = SessionLocal()
        try:
            p1 = db.query(Product).filter(Product.id == product1).first()
            p2 = db.query(Product).filter(Product.id == product2).first()
            if not p1 or not p2:
                return {"success": False, "message": "One or both products not found"}
            return {
                "product1": {
                    "id": p1.id,
                    "name": p1.name,
                    "price": p1.price,
                    "rating": p1.rating
                },
                "product2": {
                    "id": p2.id,
                    "name": p2.name,
                    "price": p2.price,
                    "rating": p2.rating
                },
                "comparison": {
                    "price_difference": round(p1.price - p2.price, 2),
                    "rating_difference": round(p1.rating - p2.rating, 2)
                }
            }
        finally:
            db.close()

    # =================================================
    # Health Check
    # =================================================
    def health(self):

        return {

            "status":
                "healthy",

            "service":
                "recommendation_service"
        }