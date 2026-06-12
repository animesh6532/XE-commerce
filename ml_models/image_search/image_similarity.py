from sklearn.metrics.pairwise import (
    cosine_similarity
)


class ImageSimilarity:

    @staticmethod
    def similarity(
        emb1,
        emb2
    ):

        score = cosine_similarity(
            emb1,
            emb2
        )

        return float(
            score[0][0]
        )