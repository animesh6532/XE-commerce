from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import (
    Review,
    Product
)

from app.monitoring.logs import (
    app_logger,
    error_logger
)

from app.notifications.push_service import PushService


class ReviewService:

    def __init__(self):

        self.push_service = PushService()

    # ==========================================
    # Add Review
    # ==========================================
    def add_review(
            self,
            db: Session,
            user_id: int,
            product_id: int = None,
            rating: float = None,
            comment: str = None,
            sentiment: str = "neutral",
            is_fake: bool = False,
            review = None
    ):
        if review is not None:
            product_id = review.product_id
            rating = review.rating
            comment = review.comment

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:

            return {
                "success": False,
                "message": "Product not found"
            }

        review_obj = Review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            comment=comment,
            sentiment=sentiment,
            is_fake=is_fake
        )

        db.add(review_obj)
        db.commit()
        db.refresh(review_obj)

        self.update_product_rating(
            db,
            product_id
        )

        app_logger.info(
            f"Review added by user {user_id}"
        )

        return review_obj

    # ==========================================
    # Update Review
    # ==========================================
    def update_review(
            self,
            db: Session,
            review_id: int,
            rating: float = None,
            comment: str = None,
            user_id: int = None,
            review = None
    ):
        if review is not None:
            rating = review.rating
            comment = review.comment

        db_review = db.query(Review).filter(
            Review.id == review_id
        ).first()

        if not db_review:

            return {
                "success": False,
                "message": "Review not found"
            }

        if rating is not None:
            db_review.rating = rating

        if comment is not None:
            db_review.comment = comment

        db.commit()

        self.update_product_rating(
            db,
            db_review.product_id
        )

        return {
            "success": True,
            "message": "Review updated"
        }

    # ==========================================
    # Delete Review
    # ==========================================
    def delete_review(
            self,
            db: Session,
            review_id: int,
            user_id: int = None
    ):

        db_review = db.query(Review).filter(
            Review.id == review_id
        ).first()

        if not db_review:

            return {
                "success": False,
                "message": "Review not found"
            }

        product_id = db_review.product_id

        db.delete(db_review)
        db.commit()

        self.update_product_rating(
            db,
            product_id
        )

        return {
            "success": True,
            "message": "Review deleted"
        }

    # ==========================================
    # Get Product Reviews
    # ==========================================
    def get_product_reviews(
            self,
            db: Session,
            product_id: int
    ):

        return db.query(Review).filter(
            Review.product_id == product_id
        ).all()

    # ==========================================
    # Get User Reviews
    # ==========================================
    def get_user_reviews(
            self,
            db: Session,
            user_id: int
    ):

        return db.query(Review).filter(
            Review.user_id == user_id
        ).all()

    # ==========================================
    # Average Rating
    # ==========================================
    def average_rating(
            self,
            db: Session,
            product_id: int
    ):

        avg_rating = db.query(
            func.avg(Review.rating)
        ).filter(
            Review.product_id == product_id
        ).scalar()

        return round(avg_rating or 0, 2)

    # ==========================================
    # Update Product Rating
    # ==========================================
    def update_product_rating(
            self,
            db: Session,
            product_id: int
    ):

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if product:

            product.rating = self.average_rating(
                db,
                product_id
            )

            db.commit()

    # ==========================================
    # Like Review
    # ==========================================
    def like_review(
            self,
            db: Session,
            review_id: int,
            user_id: int = None
    ):

        review = db.query(Review).filter(
            Review.id == review_id
        ).first()

        if not review:

            return {
                "success": False
            }

        review.likes += 1

        db.commit()

        return {
            "success": True,
            "likes": review.likes
        }

    # ==========================================
    # Dislike Review
    # ==========================================
    def dislike_review(
            self,
            db: Session,
            review_id: int,
            user_id: int = None
    ):

        review = db.query(Review).filter(
            Review.id == review_id
        ).first()

        if not review:

            return {
                "success": False
            }

        review.dislikes += 1

        db.commit()

        return {
            "success": True,
            "dislikes": review.dislikes
        }

    # ==========================================
    # Fake Reviews
    # ==========================================
    def fake_reviews(
            self,
            db: Session
    ):

        return db.query(Review).filter(
            Review.is_fake == True
        ).all()

    # ==========================================
    # Positive Reviews
    # ==========================================
    def positive_reviews(
            self,
            db: Session
    ):

        return db.query(Review).filter(
            Review.sentiment == "positive"
        ).all()

    # ==========================================
    # Negative Reviews
    # ==========================================
    def negative_reviews(
            self,
            db: Session
    ):

        return db.query(Review).filter(
            Review.sentiment == "negative"
        ).all()

    # ==========================================
    # Review Analytics
    # ==========================================
    def analytics(
            self,
            db: Session
    ):

        total_reviews = db.query(
            Review
        ).count()

        fake_reviews = db.query(
            Review
        ).filter(
            Review.is_fake == True
        ).count()

        positive_reviews = db.query(
            Review
        ).filter(
            Review.sentiment == "positive"
        ).count()

        return {

            "total_reviews":
                total_reviews,

            "fake_reviews":
                fake_reviews,

            "positive_reviews":
                positive_reviews
        }

    # ==========================================
    # Get Review By ID (with 404 validation)
    # ==========================================
    def get_review_by_id(self, db: Session, review_id: int):
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Review not found")
        return review

    # ==========================================
    # Sentiment Analysis (runs sentiment model and updates DB)
    # ==========================================
    def sentiment_analysis(self, review_id: int):
        from ml_models.sentiment.sentiment_model import SentimentModel
        model = SentimentModel()
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                return {"success": False, "message": "Review not found"}
            sentiment_label = model.predict(review.comment)
            review.sentiment = sentiment_label
            db.commit()
            return {"success": True, "sentiment": sentiment_label}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    # ==========================================
    # Detect Fake Review (runs fake review model and updates DB)
    # ==========================================
    def detect_fake_review(self, review_id: int):
        from ml_models.fake_review.fake_review_model import FakeReviewDetector
        detector = FakeReviewDetector()
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            review = db.query(Review).filter(Review.id == review_id).first()
            if not review:
                return {"success": False, "message": "Review not found"}
            result = detector.predict(review.comment)
            review.is_fake = (result == "Fake Review")
            db.commit()
            return {"success": True, "is_fake": review.is_fake, "label": result}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            db.close()

    # ==========================================
    # Review Summary (computes average and sentiment splits)
    # ==========================================
    def review_summary(self, product_id: int):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            reviews = db.query(Review).filter(Review.product_id == product_id).all()
            if not reviews:
                return {
                    "total_reviews": 0,
                    "average_rating": 0.0,
                    "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                    "sentiment_summary": {"positive": 0, "negative": 0, "neutral": 0},
                    "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                    "fake_review_percentage": 0.0
                }
            ratings = [r.rating for r in reviews if r.rating is not None]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
            
            rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for r in ratings:
                star = int(round(r))
                if star in rating_dist:
                    rating_dist[star] += 1
                    
            pos = len([r for r in reviews if str(r.sentiment).lower() == "positive"])
            neg = len([r for r in reviews if str(r.sentiment).lower() == "negative"])
            neu = len([r for r in reviews if str(r.sentiment).lower() not in ["positive", "negative"]])
            
            fake_count = len([r for r in reviews if r.is_fake])
            fake_percentage = (fake_count / len(reviews)) * 100.0 if reviews else 0.0
            
            return {
                "total_reviews": len(reviews),
                "average_rating": round(avg_rating, 2),
                "rating_distribution": rating_dist,
                "sentiment_summary": {
                    "positive": pos,
                    "negative": neg,
                    "neutral": neu
                },
                "sentiment_distribution": {
                    "positive": pos,
                    "negative": neg,
                    "neutral": neu
                },
                "fake_review_percentage": round(fake_percentage, 2)
            }
        finally:
            db.close()

    # ==========================================
    # Top Reviews
    # ==========================================
    def top_reviews(self, product_id: int):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            return db.query(Review).filter(
                Review.product_id == product_id
            ).order_by(Review.likes.desc(), Review.rating.desc()).limit(5).all()
        finally:
            db.close()

    # ==========================================
    # Verify Purchase
    # ==========================================
    def verify_purchase(self, db: Session, user_id: int, product_id: int):
        # Fallback: Since orders are saved with only total amounts, return verified if the user has any orders
        from app.database.models import Order
        user_orders = db.query(Order).filter(Order.user_id == user_id).first()
        return {
            "verified": user_orders is not None,
            "message": "Purchase verified via user order history" if user_orders else "No orders found for this user"
        }

    # ==========================================
    # Health Check
    # ==========================================
    def health(self):

        return {

            "status":
                "healthy",

            "service":
                "review_service"
        }