import os

from image_encoder import (
    ImageEncoder
)

from image_similarity import (
    ImageSimilarity
)


class ImageRecommender:

    def __init__(self):

        self.encoder = ImageEncoder()

    def recommend(
        self,
        query_image,
        image_folder
    ):

        query_embedding = (
            self.encoder.encode(
                query_image
            )
        )

        results = []

        for image_name in os.listdir(
            image_folder
        ):

            image_path = os.path.join(
                image_folder,
                image_name
            )

            try:

                embedding = (
                    self.encoder.encode(
                        image_path
                    )
                )

                score = (
                    ImageSimilarity.similarity(
                        query_embedding,
                        embedding
                    )
                )

                results.append(
                    (
                        image_name,
                        score
                    )
                )

            except Exception:

                pass

        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return results[:5]


if __name__ == "__main__":

    recommender = (
        ImageRecommender()
    )

    results = recommender.recommend(
        "query.jpg",
        "../product_images"
    )

    print(results)