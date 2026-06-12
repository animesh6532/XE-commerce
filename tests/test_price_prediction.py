import joblib
from pathlib import Path

def test_price_model_exists():

    model_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "ml_models"
        / "saved_models"
        / "price_predictor.pkl"
    )

    assert model_path.exists()


def test_price_model_loads():

    model_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "ml_models"
        / "saved_models"
        / "price_predictor.pkl"
    )

    model = joblib.load(model_path)

    assert model is not None