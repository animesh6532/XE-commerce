from pathlib import Path
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "saved_models" / "price_predictor.pkl"

model = joblib.load(MODEL_PATH)


def predict_price(
    category,
    discounted_price,
    discount_percentage,
    rating,
    rating_count
):
    data = pd.DataFrame({
        "category": [category],
        "discounted_price": [discounted_price],
        "discount_percentage": [discount_percentage],
        "rating": [rating],
        "rating_count": [rating_count]
    })

    prediction = model.predict(data)

    return round(float(prediction[0]), 2)


if __name__ == "__main__":

    result = predict_price(
        category="Electronics",
        discounted_price=1500,
        discount_percentage=25,
        rating=4.3,
        rating_count=2500
    )

    print(
        f"Predicted Original Price: ₹{result}"
    )