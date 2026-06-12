from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Load Dataset
df = pd.read_csv("../datasets/products.csv")

# -------------------------
# Data Cleaning
# -------------------------

# Remove ₹ and commas
df["discounted_price"] = (
    df["discounted_price"]
    .astype(str)
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
)

df["actual_price"] = (
    df["actual_price"]
    .astype(str)
    .str.replace("₹", "", regex=False)
    .str.replace(",", "", regex=False)
)

# Convert to numeric
df["discounted_price"] = pd.to_numeric(df["discounted_price"], errors="coerce")
df["actual_price"] = pd.to_numeric(df["actual_price"], errors="coerce")

# Rating count cleanup
df["rating_count"] = (
    df["rating_count"]
    .astype(str)
    .str.replace(",", "", regex=False)
)

df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# Discount %
df["discount_percentage"] = (
    df["discount_percentage"]
    .astype(str)
    .str.replace("%", "", regex=False)
)

df["discount_percentage"] = pd.to_numeric(
    df["discount_percentage"],
    errors="coerce"
)

# Remove missing values
df = df.dropna()

# -------------------------
# Features
# -------------------------

X = df[
    [
        "category",
        "discounted_price",
        "discount_percentage",
        "rating",
        "rating_count"
    ]
]

# Predict original price
y = df["actual_price"]

# -------------------------
# Preprocessing
# -------------------------

categorical_features = ["category"]

numeric_features = [
    "discounted_price",
    "discount_percentage",
    "rating",
    "rating_count"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        )
    ],
    remainder="passthrough"
)

# -------------------------
# Model
# -------------------------

model = Pipeline([
    ("preprocessor", preprocessor),
    (
        "regressor",
        RandomForestRegressor(
            n_estimators=200,
            random_state=42
        )
    )
])

# -------------------------
# Train-Test Split
# -------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Predict
preds = model.predict(X_test)

# Metrics
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"MAE: ₹{mae:.2f}")
print(f"R² Score: {r2:.4f}")

# Save Model
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = BASE_DIR / "saved_models"

MODEL_DIR.mkdir(exist_ok=True)

MODEL_PATH = MODEL_DIR / "price_predictor.pkl"

joblib.dump(model, MODEL_PATH)

print(f"Model saved at: {MODEL_PATH}")