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
        import datetime
        start_date = datetime.date.today()
        future_rows = []

        for i in range(days_ahead):
            future_date = start_date + datetime.timedelta(days=i)
            future_rows.append({
                "day_number": 1000 + i, # dummy index corresponding to future
                "day_of_week": future_date.weekday(),
                "month": future_date.month,
                "week_of_year": int(future_date.isocalendar()[1])
            })

        future_df = pd.DataFrame(future_rows)
        predictions = self.model.predict(future_df)
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