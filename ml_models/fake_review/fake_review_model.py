import os
import joblib
import pandas as pd
import re
import string


class FakeReviewDetector:

    def __init__(self):
        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
        MODEL_DIR = PROJECT_ROOT / "ml_models" / "saved_models"

        model_path = MODEL_DIR / "fake_review.pkl"
        vectorizer_path = MODEL_DIR / "fake_review_vectorizer.pkl"

        if not model_path.exists():
            raise FileNotFoundError(
                f"fake_review.pkl not found at {model_path}. Train model first."
            )

        self.model = joblib.load(
            str(model_path)
        )

        self.vectorizer = joblib.load(
            str(vectorizer_path)
        )


    @staticmethod
    def clean_text(text):

        if pd.isna(text):
            return ""

        text = str(text).lower()

        text = re.sub(
            r"http\S+",
            "",
            text
        )

        text = re.sub(
            r"<.*?>",
            "",
            text
        )

        text = re.sub(
            r"\d+",
            "",
            text
        )

        text = text.translate(
            str.maketrans(
                "",
                "",
                string.punctuation
            )
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def predict(self, review):

        review = self.clean_text(
            review
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

        if prediction == 1:
            return "Fake Review"

        return "Genuine Review"


if __name__ == "__main__":

    detector = (
        FakeReviewDetector()
    )

    review1 = """
    Amazing product.
    Best purchase ever.
    Highly recommended.
    """

    review2 = """
    This product works well and
    I have been using it for
    6 months without issues.
    """

    print(
        detector.predict(
            review1
        )
    )

    print(
        detector.predict(
            review2
        )
    )