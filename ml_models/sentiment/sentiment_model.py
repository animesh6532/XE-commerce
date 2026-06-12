import joblib

try:
    from review_cleaner import ReviewCleaner
except ImportError:
    try:
        from ml_models.sentiment.review_cleaner import ReviewCleaner
    except ImportError:
        from .review_cleaner import ReviewCleaner



from pathlib import Path

class SentimentModel:

    def __init__(self):
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
        MODEL_DIR = PROJECT_ROOT / "ml_models" / "saved_models"

        self.model = joblib.load(
            MODEL_DIR / "sentiment.pkl"
        )

        self.vectorizer = joblib.load(
            MODEL_DIR / "sentiment_vectorizer.pkl"
        )


    def predict(self, review):

        review = (
            ReviewCleaner.clean(
                review
            )
        )

        vector = (
            self.vectorizer.transform(
                [review]
            )
        )

        prediction = (
            self.model.predict(
                vector
            )[0]
        )

        return prediction


if __name__ == "__main__":

    model = SentimentModel()

    print(
        model.predict(
            "This product is amazing and very useful"
        )
    )

    print(
        model.predict(
            "Worst product ever. Waste of money"
        )
    )