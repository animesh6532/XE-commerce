import os
import faiss
import joblib
import pandas as pd
import numpy as np

try:
    from ml_models.search.embeddings import EmbeddingModel
except ImportError:
    try:
        from search.embeddings import EmbeddingModel
    except ImportError:
        try:
            from .embeddings import EmbeddingModel
        except ImportError:
            from embeddings import EmbeddingModel



class SemanticSearch:

    def __init__(
        self,
        dataset_path,
        index_path=None
    ):

        self.dataset_path = dataset_path

        self.index_path = index_path

        self.df = pd.read_csv(
            dataset_path
        )

        self.text_column = self.detect_text_column()

        if (
            index_path
            and
            os.path.exists(index_path)
        ):

            self.index = faiss.read_index(
                index_path
            )

        else:

            self.build_index()

    def detect_text_column(self):

        candidates = [

            "name",
            "product_name",
            "title",
            "Text",
            "text_",
            "Summary"

        ]

        for col in candidates:

            if col in self.df.columns:

                return col

        raise ValueError(
            "No text column found."
        )

    def build_index(self):

        texts = (
            self.df[
                self.text_column
            ]
            .fillna("")
            .astype(str)
            .tolist()
        )

        embeddings = (
            EmbeddingModel.encode(
                texts
            )
        )

        dimension = (
            embeddings.shape[1]
        )

        self.index = (
            faiss.IndexFlatIP(
                dimension
            )
        )

        self.index.add(
            embeddings.astype(
                np.float32
            )
        )

        if self.index_path:

            os.makedirs(
                os.path.dirname(
                    self.index_path
                ),
                exist_ok=True
            )

            faiss.write_index(
                self.index,
                self.index_path
            )

            joblib.dump(
                self.text_column,
                self.index_path + ".meta"
            )

    def search(
        self,
        query,
        top_k=5
    ):

        query_vector = (
            EmbeddingModel.encode(
                [query]
            )
        )

        scores, indices = (
            self.index.search(
                query_vector.astype(
                    np.float32
                ),
                top_k
            )
        )

        results = []

        for idx, score in zip(
            indices[0],
            scores[0]
        ):

            row = (
                self.df.iloc[idx]
                .to_dict()
            )

            row[
                "similarity"
            ] = round(
                float(score),
                4
            )

            results.append(
                row
            )

        return results


if __name__ == "__main__":

    search_engine = (
        SemanticSearch(
            "../datasets/products.csv",
            "../saved_models/products.faiss"
        )
    )

    results = (
        search_engine.search(
            "wireless headphones",
            top_k=5
        )
    )

    print(
        "\nTop Results:\n"
    )

    for item in results:

        print(
            item
        )