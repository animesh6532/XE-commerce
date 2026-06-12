# embeddings.py

import logging
from typing import List, Union
import numpy as np
from model_manager import ModelManager

# Configure logger
logger = logging.getLogger(__name__)


class ProductEmbedder:
    """
    Handles semantic embedding generation for products and categories 
    using Sentence Transformers via the ModelManager Singleton.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the ProductEmbedder, using the shared model manager instance.
        
        Args:
            model_name (str): The model name on Hugging Face hub. Defaults to 'all-MiniLM-L6-v2'.
        """
        logger.info(f"Initializing ProductEmbedder with model reference: {model_name}")
        try:
            self.model_manager = ModelManager.get_instance(model_name)
            self.dimension = self.model_manager.dimension
            logger.info("ProductEmbedder linked to ModelManager successfully.")
        except Exception as e:
            logger.error(f"Error initializing ProductEmbedder: {e}")
            raise

    def encode(
        self, 
        texts: Union[str, List[str]], 
        batch_size: int = 128, 
        show_progress_bar: bool = False
    ) -> np.ndarray:
        """
        Generates embeddings for the given text or list of texts.
        
        Args:
            texts (Union[str, List[str]]): The text or list of texts to embed.
            batch_size (int): Batch size for processing. Defaults to 128.
            show_progress_bar: Whether to show progress. Defaults to False.
            
        Returns:
            np.ndarray: A 2D numpy array of shape (num_texts, embedding_dimension).
        """
        return self.model_manager.encode(
            texts=texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar
        )
