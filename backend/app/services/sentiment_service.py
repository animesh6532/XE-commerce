from sqlalchemy.orm import Session
from pathlib import Path
import sys

# Ensure ml_models is in Python path for importing
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ML_MODELS_DIR = PROJECT_ROOT / "ml_models"
if str(ML_MODELS_DIR) not in sys.path:
    sys.path.append(str(ML_MODELS_DIR))

from sentiment.sentiment_model import SentimentModel
from app.database.models import Review, Product

class SentimentService:
    def __init__(self):
        # We load SentimentModel inside __init__. Note that sentiment_model.py imports and loads saved models, 
        # but to prevent path errors we can define the model load path dynamically in the model definition later.
        self.model = SentimentModel()

    def analyze_sentiment(self, text: str):
        sentiment = self.model.predict(text)
        return {"text": text, "sentiment": sentiment}

    def batch_sentiment_analysis(self, reviews: list):
        results = []
        for r in reviews:
            results.append({"text": r, "sentiment": self.model.predict(r)})
        return {"results": results}

    def product_sentiment(self, db: Session, product_id: int):
        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        if not reviews:
            return {"product_id": product_id, "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0}}
        pos = len([r for r in reviews if r.sentiment == "positive"])
        neg = len([r for r in reviews if r.sentiment == "negative"])
        neu = len([r for r in reviews if r.sentiment not in ["positive", "negative"]])
        return {
            "product_id": product_id,
            "sentiment_distribution": {
                "positive": pos,
                "negative": neg,
                "neutral": neu
            }
        }

    def review_sentiment(self, db: Session, review_id: int):
        review = db.query(Review).filter(Review.id == review_id).first()
        if not review:
            return {"success": False, "message": "Review not found"}
        if not review.sentiment:
            review.sentiment = self.model.predict(review.comment)
            db.commit()
        return {"review_id": review_id, "sentiment": review.sentiment}

    def sentiment_history(self, db: Session, user_id: int):
        reviews = db.query(Review).filter(Review.user_id == user_id).all()
        return [{"review_id": r.id, "comment": r.comment, "sentiment": r.sentiment} for r in reviews]

    def positive_reviews(self, db: Session, product_id: int):
        return db.query(Review).filter(Review.product_id == product_id, Review.sentiment == "positive").all()

    def negative_reviews(self, db: Session, product_id: int):
        return db.query(Review).filter(Review.product_id == product_id, Review.sentiment == "negative").all()

    def neutral_reviews(self, db: Session, product_id: int):
        return db.query(Review).filter(
            Review.product_id == product_id
        ).filter(Review.sentiment.notin_(["positive", "negative"])).all()

    def sentiment_statistics(self):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            total = db.query(Review).count()
            pos = db.query(Review).filter(Review.sentiment == "positive").count()
            neg = db.query(Review).filter(Review.sentiment == "negative").count()
            neu = total - (pos + neg)
            return {
                "total_analyzed": total,
                "positive_percentage": round((pos / total * 100) if total else 0.0, 2),
                "negative_percentage": round((neg / total * 100) if total else 0.0, 2),
                "neutral_percentage": round((neu / total * 100) if total else 0.0, 2)
            }
        finally:
            db.close()

    def product_insights(self, db: Session, product_id: int):
        reviews = db.query(Review).filter(Review.product_id == product_id).all()
        if not reviews:
            return {"insights": "No reviews found for this product."}
        pos_reviews = [r.comment for r in reviews if r.sentiment == "positive"]
        neg_reviews = [r.comment for r in reviews if r.sentiment == "negative"]
        return {
            "insights": f"Product has {len(pos_reviews)} positive feedbacks and {len(neg_reviews)} negative feedbacks.",
            "top_positive_keywords": ["good", "quality"] if pos_reviews else [],
            "top_negative_keywords": ["price", "defect"] if neg_reviews else []
        }

    def trending_opinions(self):
        # returns top positive product names
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            products = db.query(Product).order_by(Product.rating.desc()).limit(3).all()
            return [{"product_name": p.name, "rating": p.rating, "opinion": "Highly positive reviews"} for p in products]
        finally:
            db.close()

    def dashboard_data(self):
        return self.sentiment_statistics()

    def health(self):
        return {"status": "healthy", "service": "sentiment_service"}
