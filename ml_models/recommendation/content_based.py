import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedRecommender:

    def __init__(self, dataset_path):

        self.df = pd.read_csv(dataset_path)

        self.df["combined_features"] = (
            self.df["product_name"].fillna("")
            + " "
            + self.df["about_product"].fillna("")
            + " "
            + self.df["category"].fillna("")
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.feature_matrix = self.vectorizer.fit_transform(
            self.df["combined_features"]
        )

        self.similarity_matrix = cosine_similarity(
            self.feature_matrix
        )

    def recommend(self, product_name, top_n=5):

        idx = self.df[
            self.df["product_name"] == product_name
        ].index[0]

        scores = list(
            enumerate(
                self.similarity_matrix[idx]
            )
        )

        scores = sorted(
            scores,
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = []

        for i in scores[1:top_n+1]:

            recommendations.append(
                self.df.iloc[i[0]]["product_name"]
            )

        return recommendations


if __name__ == "__main__":

    model = ContentBasedRecommender(
        "../datasets/products.csv"
    )

    print("Model Loaded Successfully")

    sample_product = (
        model.df["product_name"]
        .iloc[0]
    )

    print("\nTesting Product:")
    print(sample_product)

    print("\nRecommendations:")

    recommendations = model.recommend(
        sample_product
    )

    for i, product in enumerate(
        recommendations,
        start=1
    ):
        print(f"{i}. {product}")