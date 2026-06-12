import joblib
import pandas as pd


class DemandForecastModel:

    def __init__(self):
        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
        MODEL_DIR = PROJECT_ROOT / "ml_models" / "saved_models"

        self.model = joblib.load(
            str(MODEL_DIR / "demand_forecast.pkl")
        )


    def predict(self, days_ahead=7):

        future_days = pd.DataFrame(
            {
                "day_number": range(days_ahead)
            }
        )

        predictions = self.model.predict(
            future_days
        )

        return predictions


if __name__ == "__main__":

    model = DemandForecastModel()

    predictions = model.predict(7)

    print("\nNext 7 Days Demand Forecast:\n")

    for day, prediction in enumerate(
        predictions,
        start=1
    ):

        print(
            f"Day {day}: {int(prediction)} Orders"
        )