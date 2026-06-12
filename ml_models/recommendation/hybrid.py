from content_based import ContentBasedRecommender
from collaborative import CollaborativeFiltering

class HybridRecommender:

    def __init__(self, dataset_path):

        self.content = ContentBasedRecommender(
            dataset_path
        )

        self.collaborative = CollaborativeFiltering(
            dataset_path
        )

    def recommend(
        self,
        user_id,
        product_name
    ):

        content_results = (
            self.content.recommend(
                product_name
            )
        )

        collaborative_results = (
            self.collaborative.recommend(
                user_id
            )
        )

        combined = list(
            set(
                content_results +
                collaborative_results
            )
        )

        return combined[:10]


if __name__ == "__main__":

    import pandas as pd

    df = pd.read_csv(
        "../datasets/products.csv"
    )

    model = HybridRecommender(
        "../datasets/products.csv"
    )

    user_id = df["user_id"].iloc[0]

    product_name = (
        df["product_name"]
        .iloc[0]
    )

    results = model.recommend(
        user_id,
        product_name
    )

    print(results)