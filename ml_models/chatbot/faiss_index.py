# faiss_index.py

import logging
import os
from typing import Tuple
import faiss
import numpy as np

# Configure logger
logger = logging.getLogger(__name__)


class FAISSIndexManager:
    """
    Manages building, saving, loading, and searching FAISS indices.
    Normalizes embeddings before indexing to perform Cosine Similarity search 
    using Inner Product index (`IndexFlatIP`).
    """

    @staticmethod
    def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
        """
        Builds a FAISS IndexFlatIP (Inner Product) index with L2-normalized embeddings.
        
        Args:
            embeddings (np.ndarray): 2D numpy array of shape (num_products, embedding_dimension).
            
        Returns:
            faiss.IndexFlatIP: The built FAISS index.
        """
        if len(embeddings) == 0:
            logger.error("Cannot build FAISS index for empty embeddings array.")
            raise ValueError("Embeddings array must not be empty.")

        dimension = embeddings.shape[1]
        logger.info(f"Building FAISS IndexFlatIP index with dimension {dimension}...")

        try:
            # Copy and normalize vectors in place for Cosine Similarity
            normalized_embeddings = embeddings.astype(np.float32).copy()
            faiss.normalize_L2(normalized_embeddings)

            # Create the index
            index = faiss.IndexFlatIP(dimension)
            index.add(normalized_embeddings)
            
            logger.info(f"Successfully built FAISS index with {index.ntotal} vectors.")
            return index
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            raise

    @staticmethod
    def save_index(index: faiss.Index, filepath: str) -> None:
        """
        Saves a FAISS index to the local filesystem.
        
        Args:
            index (faiss.Index): The FAISS index to save.
            filepath (str): The destination path.
        """
        try:
            directory = os.path.dirname(filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            faiss.write_index(index, filepath)
            logger.info(f"Saved FAISS index to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index to {filepath}: {e}")
            raise

    @staticmethod
    def load_index(filepath: str) -> faiss.Index:
        """
        Loads a FAISS index from the local filesystem.
        
        Args:
            filepath (str): Path to the saved FAISS index.
            
        Returns:
            faiss.Index: The loaded FAISS index.
        """
        if not os.path.exists(filepath):
            logger.error(f"FAISS index file not found at: {filepath}")
            raise FileNotFoundError(f"FAISS index file not found at: {filepath}")

        try:
            index = faiss.read_index(filepath)
            logger.info(f"Loaded FAISS index from {filepath} (total vectors: {index.ntotal}).")
            return index
        except Exception as e:
            logger.error(f"Failed to load FAISS index from {filepath}: {e}")
            raise

    @staticmethod
    def similarity_search(
        index: faiss.Index, 
        query_embeddings: np.ndarray, 
        k: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Performs Inner Product search on normalized query vectors (returns Cosine Similarity).
        
        Args:
            index (faiss.Index): The loaded FAISS index.
            query_embeddings (np.ndarray): 2D numpy array of query embeddings.
            k (int): Number of top results to retrieve. Defaults to 5.
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: (similarities, indices)
                - similarities: float similarity scores (1.0 = identical).
                - indices: indices of the matching vectors in the index.
        """
        try:
            # Copy and normalize query vectors for Cosine Similarity
            normalized_queries = query_embeddings.astype(np.float32).copy()
            faiss.normalize_L2(normalized_queries)

            similarities, indices = index.search(normalized_queries, k)
            return similarities, indices
        except Exception as e:
            logger.error(f"Error during FAISS similarity search: {e}")
            raise


if __name__ == "__main__":
    import numpy as np

    print("Testing FAISS Index...")

    embeddings = np.random.rand(
        100,
        384
    ).astype(np.float32)

    index = FAISSIndexManager.build_index(
        embeddings
    )

    print(
        f"Index Created Successfully!"
    )

    print(
        f"Total Vectors: {index.ntotal}"
    )

    query = np.random.rand(
        1,
        384
    ).astype(np.float32)

    similarities, indices = (
        FAISSIndexManager.similarity_search(
            index,
            query,
            k=5
        )
    )

    print("\nTop Matches:")

    print(indices)

    print(similarities)
