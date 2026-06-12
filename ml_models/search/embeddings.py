import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingModel:

    _model = None

    @classmethod
    def get_model(cls):

        if cls._model is None:

            logger.info(
                "Loading all-MiniLM-L6-v2..."
            )

            cls._model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

        return cls._model

    @classmethod
    def encode(
        cls,
        texts
    ):

        model = cls.get_model()

        return model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )


if __name__ == "__main__":

    text = [
        "wireless headphones",
        "gaming laptop"
    ]

    vectors = EmbeddingModel.encode(
        text
    )

    print(
        vectors.shape
    )