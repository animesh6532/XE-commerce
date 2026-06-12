import os
import joblib
import pandas as pd

from sklearn.ensemble import (
    RandomForestRegressor
)

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("\nLoading Orders Dataset...")

DATASET_PATH = (
    "../datasets/orders.csv"
)

df = pd.read_csv(
    DATASET_PATH
)

print(
    f"Total Orders: {len(df)}"
)

# ------------------------------------
# Convert Date
# ------------------------------------

df["order_purchase_timestamp"] = pd.to_datetime(
    df["order_purchase_timestamp"]
)

# ------------------------------------
# Daily Order Count
# ------------------------------------

daily_orders = (
    df.groupby(
        df["order_purchase_timestamp"].dt.date
    )
    .size()
    .reset_index(
        name="orders"
    )
)

daily_orders.columns = [
    "date",
    "orders"
]

daily_orders = (
    daily_orders.sort_values(
        "date"
    )
)

daily_orders.reset_index(
    drop=True,
    inplace=True
)

# ------------------------------------
# Feature Engineering
# ------------------------------------

daily_orders["day_number"] = (
    daily_orders.index
)

daily_orders["day_of_week"] = pd.to_datetime(
    daily_orders["date"]
).dt.dayofweek

daily_orders["month"] = pd.to_datetime(
    daily_orders["date"]
).dt.month

daily_orders["week_of_year"] = pd.to_datetime(
    daily_orders["date"]
).dt.isocalendar().week.astype(int)

# ------------------------------------
# Features
# ------------------------------------

X = daily_orders[
    [
        "day_number",
        "day_of_week",
        "month",
        "week_of_year"
    ]
]

y = daily_orders[
    "orders"
]

# ------------------------------------
# Train/Test Split
# ------------------------------------

split_index = int(
    len(daily_orders) * 0.8
)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

print(
    f"\nTraining Records: {len(X_train)}"
)

print(
    f"Testing Records: {len(X_test)}"
)

# ------------------------------------
# Model
# ------------------------------------

print(
    "\nTraining Random Forest..."
)

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

# ------------------------------------
# Evaluation
# ------------------------------------

predictions = model.predict(
    X_test
)

mae = mean_absolute_error(
    y_test,
    predictions
)

mse = mean_squared_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)

print(
    f"\nMAE : {mae:.2f}"
)

print(
    f"MSE : {mse:.2f}"
)

print(
    f"R²  : {r2:.4f}"
)

# ------------------------------------
# Save Model
# ------------------------------------

SAVE_DIR = (
    "../saved_models"
)

os.makedirs(
    SAVE_DIR,
    exist_ok=True
)

joblib.dump(
    model,
    f"{SAVE_DIR}/demand_forecast.pkl"
)

print(
    "\nDemand Forecast Model Saved Successfully!"
)

print(
    f"Location: {SAVE_DIR}/demand_forecast.pkl"
)

# ------------------------------------
# Future Forecast
# ------------------------------------

print(
    "\nNext 7 Days Forecast:\n"
)

last_day = (
    daily_orders["day_number"]
    .max()
)

future_rows = []

for i in range(1, 8):

    future_date = (
        pd.to_datetime(
            daily_orders["date"].max()
        )
        + pd.Timedelta(days=i)
    )

    future_rows.append(
        {
            "day_number": last_day + i,
            "day_of_week": future_date.dayofweek,
            "month": future_date.month,
            "week_of_year": future_date.isocalendar().week
        }
    )

future_df = pd.DataFrame(
    future_rows
)

future_predictions = (
    model.predict(
        future_df
    )
)

for day, prediction in enumerate(
    future_predictions,
    start=1
):

    print(
        f"Day {day}: {int(prediction)} Orders"
    )

print(
    "\nDemand Forecasting Training Completed Successfully!"
)