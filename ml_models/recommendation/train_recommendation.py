import joblib
from pathlib import Path

from content_based import ContentBasedRecommender

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET = BASE_DIR / "datasets" / "products.csv"

MODEL_PATH = (
    BASE_DIR /
    "saved_models" /
    "recommender.pkl"
)

model = ContentBasedRecommender(
    DATASET
)

joblib.dump(
    model,
    MODEL_PATH
)

print("Recommendation Model Saved Successfully!")
print(f"Saved at: {MODEL_PATH}")