import os
import re
import string
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
    classification_report,
    confusion_matrix
)


DATASET_PATH = (
    "../datasets/fake_review.csv"
)

SAVE_DIR = (
    "../saved_models"
)

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)


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


print(
    "\nLoading Dataset..."
)

df = pd.read_csv(
    DATASET_PATH
)

print(
    f"Total Records: {len(df)}"
)

required_columns = [
    "text_",
    "label"
]

for column in required_columns:

    if column not in df.columns:

        raise ValueError(
            f"Missing Column: {column}"
        )

print(
    "\nCleaning Reviews..."
)

df["clean_text"] = (
    df["text_"]
    .apply(clean_text)
)

print(
    "\nLabel Distribution:"
)

print(
    df["label"]
    .value_counts()
)

label_mapping = {
    "CG": 1,
    "OR": 0
}

df["target"] = (
    df["label"]
    .map(label_mapping)
)

X = (
    df["clean_text"]
)

y = (
    df["target"]
)

print(
    "\nCreating TF-IDF Features..."
)

vectorizer = (
    TfidfVectorizer(
        max_features=15000,
        stop_words="english"
    )
)

X = (
    vectorizer.fit_transform(
        X
    )
)

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
)

print(
    "\nTraining Logistic Regression..."
)

model = (
    LogisticRegression(
        max_iter=1000
    )
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

accuracy = (
    accuracy_score(
        y_test,
        predictions
    )
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

print(
    "\nConfusion Matrix:\n"
)

print(
    confusion_matrix(
        y_test,
        predictions
    )
)

joblib.dump(
    model,
    f"{SAVE_DIR}/fake_review.pkl"
)

joblib.dump(
    vectorizer,
    f"{SAVE_DIR}/fake_review_vectorizer.pkl"
)

print(
    "\nModel Saved Successfully!"
)

print(
    f"\nSaved:"
)

print(
    f"{SAVE_DIR}/fake_review.pkl"
)

print(
    f"{SAVE_DIR}/fake_review_vectorizer.pkl"
)