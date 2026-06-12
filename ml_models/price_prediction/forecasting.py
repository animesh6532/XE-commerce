from pathlib import Path

import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt
import joblib

# -----------------------------
# Load Dataset
# -----------------------------

DATASET_PATH = "price_history.csv"

df = pd.read_csv(DATASET_PATH)

# Prophet expects:
# ds -> date
# y -> target value

df = df.rename(columns={
    "date": "ds",
    "price": "y"
})

# -----------------------------
# Train Forecast Model
# -----------------------------

model = Prophet(
    yearly_seasonality=True,
    weekly_seasonality=False,
    daily_seasonality=False
)

model.fit(df)

BASE_DIR = Path(__file__).resolve().parent

FORECAST_MODEL_PATH = (
    BASE_DIR /
    "saved_models" /
    "forecasting_model.pkl"
)

FORECAST_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(
    model,
    FORECAST_MODEL_PATH
)

print(f"Forecasting model saved successfully at: {FORECAST_MODEL_PATH}")

# -----------------------------
# Predict Future Prices
# -----------------------------

future = model.make_future_dataframe(
    periods=30,
    freq="D"
)

forecast = model.predict(future)

# -----------------------------
# Show Predictions
# -----------------------------

print("\nNext 30 Day Forecast:\n")

print(
    forecast[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].tail(30)
)

# -----------------------------
# Save Forecast CSV
# -----------------------------

forecast.to_csv(
    "future_price_forecast.csv",
    index=False
)

print(
    "\nForecast saved to future_price_forecast.csv"
)

# -----------------------------
# Visualization
# -----------------------------

fig1 = model.plot(forecast)

plt.title(
    "Future Product Price Forecast"
)

plt.xlabel("Date")

plt.ylabel("Predicted Price")

plt.show()

# -----------------------------
# Components Plot
# -----------------------------

fig2 = model.plot_components(
    forecast
)

plt.show()