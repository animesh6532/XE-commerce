from pathlib import Path

def test_recommender_exists():

    model_path = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "ml_models"
        / "saved_models"
        / "recommender.pkl"
    )

    assert model_path.exists()