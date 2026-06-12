import pandas as pd

class CollaborativeFiltering:

    def __init__(self, dataset_path):

        self.df = pd.read_csv(dataset_path)

    def recommend(self, user_id):

        user_data = self.df[
            self.df["user_id"] == user_id
        ]

        liked_categories = (
            user_data["category"]
            .value_counts()
            .index
        )

        recommendations = self.df[
            self.df["category"].isin(
                liked_categories
            )
        ]

        return (
            recommendations["product_name"]
            .head(5)
            .tolist()
        )


if __name__ == "__main__":

    model = CollaborativeFiltering(
        "../datasets/products.csv"
    )

    sample_user = (
        model.df["user_id"]
        .iloc[0]
    )

    print("Testing User:")
    print(sample_user)

    print(
        model.recommend(
            sample_user
        )
    )