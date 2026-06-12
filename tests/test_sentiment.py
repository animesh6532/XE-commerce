from pathlib import Path

def test_sentiment_model_exists():

    model_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "ml_models"
        / "saved_models"
        / "sentiment.pkl"
    )

    assert model_path.exists()