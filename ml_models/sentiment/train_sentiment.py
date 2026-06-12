import os
import joblib
import pandas as pd

from sklearn.model_selection import (
    train_test_split
)

from sklearn.feature_extraction.text import (
    TfidfVectorizer
)

from sklearn.linear_model import (
    LogisticRegression
)

from sklearn.metrics import (
    accuracy_score,
    classification_report
)

from review_cleaner import (
    ReviewCleaner
)

print("Loading dataset...")

DATASET_PATH = (
    "../datasets/reviews.csv"
)

df = pd.read_csv(
    DATASET_PATH
)

print(
    f"Total Reviews: {len(df)}"
)

df = df[
    ["Score", "Text"]
].dropna()

print(
    "Cleaning reviews..."
)

df["clean_text"] = (
    df["Text"]
    .apply(
        ReviewCleaner.clean
    )
)

def map_sentiment(score):

    if score <= 2:
        return "Negative"

    elif score == 3:
        return "Neutral"

    else:
        return "Positive"


df["sentiment"] = (
    df["Score"]
    .apply(
        map_sentiment
    )
)

print(
    df["sentiment"]
    .value_counts()
)

vectorizer = (
    TfidfVectorizer(
        max_features=10000,
        stop_words="english"
    )
)

X = vectorizer.fit_transform(
    df["clean_text"]
)

y = df["sentiment"]

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
)

print(
    "Training model..."
)

model = LogisticRegression(
    max_iter=1000
)

model.fit(
    X_train,
    y_train
)

predictions = (
    model.predict(
        X_test
    )
)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    f"\nAccuracy: {accuracy:.4f}"
)

print(
    "\nClassification Report:\n"
)

print(
    classification_report(
        y_test,
        predictions
    )
)

SAVE_DIR = (
    "../saved_models"
)

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)

joblib.dump(
    model,
    f"{SAVE_DIR}/sentiment.pkl"
)

joblib.dump(
    vectorizer,
    f"{SAVE_DIR}/sentiment_vectorizer.pkl"
)

print(
    "\nSentiment Model Saved Successfully!"
)