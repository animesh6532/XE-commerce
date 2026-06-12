# category_router.py

import os
import pickle
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

from embeddings import ProductEmbedder
from intent_classifier import IntentClassifier

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CategoryRouter:
    """
    Routes user shopping queries to the most relevant dataset file.
    Uses zero-shot intent classification and semantic profiling.
    """

    # Intent to dataset stem names mapping
    INTENT_TO_DATASETS = {
        "Electronics": [
            "All Electronics", "Cameras", "Camera Accessories", "Headphones", "Speakers",
            "Televisions", "Home Audio and Theater", "Home Entertainment Systems",
            "Security Cameras", "Car Electronics", "All Movies and TV Shows",
            "All Music", "Blu-ray", "Film Songs", "International Music", "Indian Classical",
            "Fine Art", "Entertainment Collectibles", "Industrial and Scientific Supplies",
            "Lab and Scientific", "Test Measure and Inspect", "Sewing and Craft Supplies"
        ],
        "Gaming": [
            "Gaming Accessories", "Gaming Consoles", "PC Games", "All Video Games",
            "Video Games Deals", "Toys and Games", "Toys Gifting Store", "STEM Toys Store",
            "International Toy Store"
        ],
        "Books": [
            "All Books", "All English", "All Hindi", "Childrens Books", "Fiction Books",
            "Indian Language Books", "Kindle eBooks", "School Textbooks", "Textbooks",
            "Exam Central"
        ],
        "Fashion": [
            "Amazon Fashion", "Baby Fashion", "Backpacks", "Bags and Luggage", "Ballerinas",
            "Casual Shoes", "Clothing", "Ethnic Wear", "Fashion Sandals", "Fashion and Silver Jewellery",
            "Formal Shoes", "Gold and Diamond Jewellery", "Handbags and Clutches", "Innerwear",
            "Jeans", "Jewellery", "Kids Clothing", "Kids Fashion", "Kids Shoes", "Kids Watches",
            "Lingerie and Nightwear", "Mens Fashion", "Shirts", "Shoes", "Sportswear",
            "Suitcases and Trolley Bags", "Sunglasses", "T-shirts and Polos",
            "The Designer Boutique", "Wallets", "Watches", "Western Wear", "Womens Fashion",
            "Travel Accessories", "Travel Duffles"
        ],
        "Home Appliances": [
            "Air Conditioners", "All Appliances", "Heating and Cooling Appliances",
            "Refrigerators", "Washing Machines", "Personal Care Appliances", "Furniture",
            "Home Dcor", "Home Storage", "Home Furnishing", "Home Improvement",
            "Garden and Outdoors", "Indoor Lighting", "Bedroom Linen", "Household Supplies",
            "Janitorial and Sanitation Supplies", "Strollers and Prams"
        ],
        "Pets": [
            "All Pet Supplies", "Dog supplies"
        ],
        "Sports": [
            "All Exercise and Fitness", "All Sports Fitness and Outdoors", "Badminton",
            "Camping and Hiking", "Cardio Equipment", "Cricket", "Cycling",
            "Fitness Accessories", "Football", "Running", "Sports Collectibles",
            "Sports Shoes", "Strength Training", "Yoga"
        ],
        "Automotive": [
            "All Car and Motorbike Products", "Car Accessories", "Car Parts", "Car and Bike Care",
            "Motorbike Accessories and Parts"
        ],
        "Health": [
            "Amazon Pharmacy", "Diet and Nutrition", "Health and Personal Care",
            "Baby Bath Skin and Grooming", "Baby Products", "Diapers", "Nursing and Feeding"
        ],
        "Kitchen": [
            "Kitchen Storage and Containers", "Kitchen and Dining", "Kitchen and Home Appliances",
            "All Home and Kitchen", "Coffee Tea and Beverages", "Snack Foods", "Pantry",
            "All Grocery and Gourmet Foods"
        ],
        "Beauty": [
            "Beauty and Grooming", "Luxury Beauty", "Make-up"
        ]
    }

    def __init__(self, force_rebuild: bool = False):
        """
        Initializes the CategoryRouter, loading or building cached profiles.
        
        Args:
            force_rebuild (bool): If True, ignores cached profiles and regenerates them.
        """
        self.base_dir = Path(__file__).resolve().parent.parent
        self.dataset_dir = self.base_dir / "datasets" / "chatbot_dataset"
        self.save_dir = self.base_dir / "saved_models"
        self.cache_path = self.save_dir / "dataset_profiles.pkl"

        # Initialize the Sentence Transformer embedder
        self.embedder = ProductEmbedder()

        # Initialize Zero-Shot Intent Classifier
        self.intent_classifier = IntentClassifier()

        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.dataset_embeddings: np.ndarray = np.empty((0, self.embedder.dimension), dtype=np.float32)
        self.datasets: List[str] = []

        self._initialize_router(force_rebuild)

    def _initialize_router(self, force_rebuild: bool) -> None:
        """Loads dataset profiles and embeddings from cache, or builds them if not present."""
        if not force_rebuild and self.cache_path.exists():
            logger.info(f"Loading cached dataset profiles from: {self.cache_path}")
            try:
                with open(self.cache_path, "rb") as f:
                    cache_data = pickle.load(f)
                
                self.profiles = cache_data["profiles"]
                self.dataset_embeddings = cache_data["embeddings"]
                self.datasets = cache_data["datasets"]
                
                # Double check that cached files still exist on disk
                missing = [name for name in self.datasets if not Path(self.profiles[name]["path"]).exists()]
                if missing:
                    logger.warning(f"Some cached datasets are missing from disk: {missing}. Rebuilding cache...")
                    self.rebuild_profiles()
                else:
                    logger.info(f"Category Router loaded {len(self.datasets)} datasets successfully from cache.")
                return
            except Exception as e:
                logger.error(f"Error loading cached profiles: {e}. Rebuilding profiles...")

        self.rebuild_profiles()

    def rebuild_profiles(self) -> None:
        """Scans dataset directory, builds text profiles for each CSV, and caches them."""
        logger.info(f"Scanning datasets directory: {self.dataset_dir}")
        if not self.dataset_dir.exists():
            logger.error(f"Datasets directory not found at {self.dataset_dir}")
            raise FileNotFoundError(f"Datasets directory does not exist at {self.dataset_dir}")

        csv_files = list(self.dataset_dir.glob("*.csv"))
        logger.info(f"Discovered {len(csv_files)} CSV files.")

        profiles = {}
        datasets = []

        for file in csv_files:
            dataset_name = file.stem
            file_path = str(file)
            
            # Skip or create basic profile for empty files
            if file.stat().st_size <= 120:
                logger.debug(f"Dataset '{dataset_name}' is empty or header-only. Generating basic profile.")
                profile_text = f"Dataset: {dataset_name}. Categories: {dataset_name}."
                profiles[dataset_name] = {
                    "path": file_path,
                    "profile_text": profile_text,
                    "main_categories": [],
                    "sub_categories": []
                }
                datasets.append(dataset_name)
                continue

            try:
                # Read a sample to construct the profile quickly without loading massive CSVs
                df_sample = pd.read_csv(file, nrows=100)
                
                main_cats = []
                sub_cats = []
                sample_products = []

                if "main_category" in df_sample.columns:
                    main_cats = [str(x) for x in df_sample["main_category"].dropna().unique()]
                if "sub_category" in df_sample.columns:
                    sub_cats = [str(x) for x in df_sample["sub_category"].dropna().unique()]
                if "name" in df_sample.columns:
                    sample_products = [str(x) for x in df_sample["name"].dropna().head(5)]

                main_cats_str = ", ".join(main_cats[:5])
                sub_cats_str = ", ".join(sub_cats[:10])
                sample_products_str = "; ".join(sample_products[:3])

                # Build a rich textual description for embedding semantic matching
                profile_text = (
                    f"Dataset Name: {dataset_name}. "
                    f"Main categories: {main_cats_str}. "
                    f"Sub categories: {sub_cats_str}. "
                    f"Sample products: {sample_products_str}."
                )

                profiles[dataset_name] = {
                    "path": file_path,
                    "profile_text": profile_text,
                    "main_categories": main_cats,
                    "sub_categories": sub_cats
                }
                datasets.append(dataset_name)
                logger.debug(f"Generated profile for: {dataset_name}")
            except Exception as e:
                logger.warning(f"Error processing dataset '{dataset_name}': {e}. Fallback to basic profile.")
                profiles[dataset_name] = {
                    "path": file_path,
                    "profile_text": f"Dataset: {dataset_name}.",
                    "main_categories": [],
                    "sub_categories": []
                }
                datasets.append(dataset_name)

        self.datasets = sorted(datasets)
        self.profiles = profiles

        # Compute embeddings for all text profiles
        logger.info(f"Encoding {len(self.datasets)} dataset profiles...")
        profile_texts = [self.profiles[name]["profile_text"] for name in self.datasets]
        
        try:
            self.dataset_embeddings = self.embedder.encode(profile_texts, show_progress_bar=False)
            
            # Save to cache
            self.save_dir.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "wb") as f:
                pickle.dump({
                    "profiles": self.profiles,
                    "embeddings": self.dataset_embeddings,
                    "datasets": self.datasets
                }, f)
            logger.info(f"Dataset profiles and embeddings successfully cached at: {self.cache_path}")
        except Exception as e:
            logger.error(f"Failed to generate and cache dataset embeddings: {e}")
            raise

    def find_best_dataset(self, query: str) -> Dict[str, Any]:
        """
        Finds the most relevant dataset for a given query.
        Uses zero-shot intent classification to restrict candidate search space.
        
        Args:
            query (str): The search query.
            
        Returns:
            Dict[str, Any]: A dictionary containing 'dataset', 'path', and 'similarity'.
        """
        import time
        from logging_utils import log_router
        start_time = time.time()

        # 1. Zero-shot intent classification
        classification = self.intent_classifier.classify(query)
        intent = classification["intent"]
        confidence = classification["confidence"]

        # 2. Filter datasets by intent
        filtered_datasets = []
        if confidence >= 0.4:
            mapped_datasets = self.INTENT_TO_DATASETS.get(intent, [])
            filtered_datasets = [name for name in self.datasets if name in mapped_datasets]

        if not filtered_datasets:
            logger.info("Fallback: using all datasets due to low confidence or empty mapping.")
            filtered_datasets = self.datasets

        # 3. Perform semantic profile search among filtered list
        query_embedding = self.embedder.encode([query])
        filtered_indices = [self.datasets.index(name) for name in filtered_datasets]
        filtered_embeddings = self.dataset_embeddings[filtered_indices]

        similarities = cosine_similarity(query_embedding, filtered_embeddings)[0]
        best_idx = np.argmax(similarities)
        best_dataset = filtered_datasets[best_idx]

        search_time = time.time() - start_time
        log_router(query, best_dataset, search_time)

        return {
            "dataset": best_dataset,
            "path": self.profiles[best_dataset]["path"],
            "similarity": round(float(similarities[best_idx]), 4),
            "intent": intent,
            "confidence": confidence
        }

    def top_k_datasets(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Returns the top k matching datasets and similarity scores for the query.
        
        Args:
            query (str): The search query.
            k (int): The number of matching datasets to return. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: List of matching dataset details sorted by similarity descending.
        """
        # 1. Zero-shot intent classification
        classification = self.intent_classifier.classify(query)
        intent = classification["intent"]
        confidence = classification["confidence"]

        # 2. Filter datasets by intent
        filtered_datasets = []
        if confidence >= 0.4:
            mapped_datasets = self.INTENT_TO_DATASETS.get(intent, [])
            filtered_datasets = [name for name in self.datasets if name in mapped_datasets]

        if not filtered_datasets:
            filtered_datasets = self.datasets

        # 3. Perform semantic search
        query_embedding = self.embedder.encode([query])
        filtered_indices = [self.datasets.index(name) for name in filtered_datasets]
        filtered_embeddings = self.dataset_embeddings[filtered_indices]

        similarities = cosine_similarity(query_embedding, filtered_embeddings)[0]
        
        top_k = min(k, len(filtered_datasets))
        indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in indices:
            dataset_name = filtered_datasets[idx]
            results.append({
                "dataset": dataset_name,
                "path": self.profiles[dataset_name]["path"],
                "similarity": round(float(similarities[idx]), 4)
            })
        return results


if __name__ == "__main__":
    import sys
    # Quick CLI test harness
    router = CategoryRouter()
    print(f"\nTotal Datasets Profiled: {len(router.datasets)}")
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\nRouting query: '{query}'")
        best = router.find_best_dataset(query)
        print(f"Best Match: {best}")
    else:
        # Default test from user query
        query = "Mechanical gaming keyboard under 5000"
        print(f"\nRouting test query: '{query}'")
        best = router.find_best_dataset(query)
        print(f"Best Match: {best}")
