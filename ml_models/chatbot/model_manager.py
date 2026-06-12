# model_manager.py

import logging
import threading
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Thread-safe Singleton Model Manager to load and cache the SentenceTransformer model.
    Prevents reloading models across threads and multiple class instantiations.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if self._initialized:
            return
        
        with self._lock:
            if self._initialized:
                return
            
            logger.info(f"Initializing ModelManager Singleton with model: {model_name}")
            try:
                self.model = SentenceTransformer(model_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
                self._initialized = True
                logger.info(f"SentenceTransformer '{model_name}' successfully loaded once. Dimension: {self.dimension}")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer model: {e}")
                raise e

    @classmethod
    def get_instance(cls, model_name: str = "all-MiniLM-L6-v2") -> 'ModelManager':
        """
        Global access point to retrieve the Singleton instance.
        """
        if cls._instance is None:
            cls(model_name)
        return cls._instance

    def encode(
        self, 
        texts: Union[str, List[str]], 
        batch_size: int = 128, 
        show_progress_bar: bool = False
    ) -> np.ndarray:
        """
        Wrapper to encode texts using the single loaded model instance.
        """
        if isinstance(texts, str):
            texts = [texts]
            
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress_bar,
                convert_to_numpy=True
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to generate embeddings via ModelManager: {e}")
            raise e
