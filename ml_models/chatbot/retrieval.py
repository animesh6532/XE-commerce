# retrieval.py

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import faiss

from embeddings import ProductEmbedder
from faiss_index import FAISSIndexManager
from query_parser import QueryParser

# Configure logger
logger = logging.getLogger(__name__)


class ProductRetriever:
    """
    Handles loading dataset, cleaning product metadata, on-demand FAISS indexing, 
    semantic search, metadata filtering (budget, category, ratings, brand), and intelligent product ranking.
    """

    def __init__(self, dataset_path: str, embedder: Optional[ProductEmbedder] = None):
        """
        Initializes the ProductRetriever for a specific dataset.
        
        Args:
            dataset_path (str): Absolute or relative path to the dataset CSV.
            embedder (Optional[ProductEmbedder]): Shared ProductEmbedder instance to avoid reloading.
        """
        self.dataset_path = Path(dataset_path)
        self.dataset_name = self.dataset_path.stem
        self.base_dir = self.dataset_path.parent.parent
        self.save_dir = self.base_dir / "saved_models"
        self.index_path = self.save_dir / f"{self.dataset_name}_index.faiss"

        self.embedder = embedder or ProductEmbedder()
        self.query_parser = QueryParser()

        logger.info(f"Loading dataset: {self.dataset_path}")
        if not self.dataset_path.exists():
            logger.error(f"Dataset file not found at: {self.dataset_path}")
            raise FileNotFoundError(f"Dataset file not found at: {self.dataset_path}")

        try:
            self.df = pd.read_csv(self.dataset_path)
        except Exception as e:
            logger.error(f"Failed to read CSV file {self.dataset_path}: {e}")
            raise

        # Normalize key column name
        if "name" not in self.df.columns:
            if "product_name" in self.df.columns:
                self.df = self.df.rename(columns={"product_name": "name"})
            else:
                logger.error("Dataset CSV must contain a 'name' or 'product_name' column.")
                raise ValueError("Dataset CSV lacks product identifier column.")

        # Clean rows with missing names and reset index to align with FAISS index row-for-row
        self.df = self.df.dropna(subset=["name"]).reset_index(drop=True)

        # Pre-clean prices, ratings and rating counts for filters and scoring
        self._pre_clean_metadata()

        # Build or load FAISS index
        self.index = self._get_or_create_index()

    def _pre_clean_metadata(self) -> None:
        """Cleans and parses columns to numerical formats for fast operations."""
        logger.debug(f"Pre-cleaning metadata for {self.dataset_name}...")

        # 1. Parse rating
        def clean_rating(val):
            if pd.isna(val):
                return 0.0
            try:
                # Handles cases like string "4.2", ratings with commas or trailing chars
                s = str(val).strip()
                return float(s)
            except ValueError:
                return 0.0

        self.df["clean_rating"] = self.df["ratings"].apply(clean_rating)

        # 2. Parse number of ratings
        def clean_no_of_ratings(val):
            if pd.isna(val):
                return 0.0
            try:
                s = str(val).replace(",", "").strip()
                return float(s)
            except ValueError:
                return 0.0

        self.df["clean_no_of_ratings"] = self.df["no_of_ratings"].apply(clean_no_of_ratings)

        # 3. Parse price (both discount and actual prices)
        def clean_price(val):
            if pd.isna(val):
                return None
            try:
                # Extract digits and decimals only (strips ₹, commas, and other symbols)
                s = str(val)
                cleaned = "".join([c for c in s if c.isdigit() or c == "."])
                return float(cleaned) if cleaned else None
            except ValueError:
                return None

        self.df["clean_discount_price"] = self.df["discount_price"].apply(clean_price)
        self.df["clean_actual_price"] = self.df["actual_price"].apply(clean_price)

    def _get_or_create_index(self) -> faiss.Index:
        """Loads index from disk or builds it dynamically if not cached."""
        if len(self.df) == 0:
            logger.warning(f"Dataset {self.dataset_name} is empty. Returning empty FAISS index.")
            return faiss.IndexFlatIP(self.embedder.dimension)

        if self.index_path.exists():
            logger.info(f"Found cached FAISS index for {self.dataset_name}. Loading...")
            try:
                return FAISSIndexManager.load_index(str(self.index_path))
            except Exception as e:
                logger.warning(f"Error loading cached FAISS index: {e}. Rebuilding index...")

        # If we need to build the index
        logger.info(f"Generating FAISS index on-the-fly for {len(self.df)} products in {self.dataset_name}...")
        
        product_texts = []
        for idx, row in self.df.iterrows():
            name = str(row["name"]).strip()
            main_cat = str(row.get("main_category", "")).strip()
            sub_cat = str(row.get("sub_category", "")).strip()

            text = f"Product: {name}."
            if main_cat and main_cat.lower() != "nan":
                text += f" Main Category: {main_cat}."
            if sub_cat and sub_cat.lower() != "nan":
                text += f" Sub-category: {sub_cat}."
            
            product_texts.append(text)

        try:
            # Generate embeddings (supports batch processing)
            embeddings = self.embedder.encode(
                product_texts, 
                batch_size=128, 
                show_progress_bar=False
            )
            # Build and save FAISS index
            index = FAISSIndexManager.build_index(embeddings)
            
            self.save_dir.mkdir(parents=True, exist_ok=True)
            FAISSIndexManager.save_index(index, str(self.index_path))
            return index
        except Exception as e:
            logger.error(f"Failed to build and save FAISS index for {self.dataset_name}: {e}")
            raise

    def search(
        self,
        query: str,
        budget: Optional[float] = None,
        min_rating: Optional[float] = None,
        sub_category: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves products matching semantic query and refines using metadata filters 
        and rating-popularity rank score.
        
        Args:
            query (str): User semantic search query.
            budget (Optional[float]): Maximum discount price budget filter.
            min_rating (Optional[float]): Minimum product rating filter (0.0 to 5.0).
            sub_category (Optional[str]): Sub-category sub-string filter.
            top_k (int): Number of top ranked products to return.
            
        Returns:
            List[Dict[str, Any]]: List of ranked product dictionaries with scores.
        """
        import time
        from logging_utils import log_retrieval
        start_time = time.time()

        if len(self.df) == 0:
            logger.warning("Empty dataset. Returning no products.")
            log_retrieval(query, self.dataset_name, 0.0, 0)
            return []

        # Parse query for constraints if not provided as argument
        parsed = self.query_parser.parse(query)
        
        if budget is None:
            budget = parsed["budget"]
        if min_rating is None:
            min_rating = parsed["min_rating"]
            
        brand = parsed["brand"]
        category = parsed["category"]

        logger.info(f"Searching {self.dataset_name} | query='{query}' | budget={budget} | min_rating={min_rating} | brand={brand} | category={category}")

        # Embed query
        query_embedding = self.embedder.encode([query])

        # Retrieve candidate items (fetch larger K to allow post-filtering)
        candidate_count = max(top_k * 15, 300)
        candidate_count = min(candidate_count, len(self.df))

        if candidate_count == 0:
            logger.warning("Empty dataset. Returning no products.")
            return []

        similarities, indices = FAISSIndexManager.similarity_search(
            self.index, 
            query_embedding, 
            k=candidate_count
        )
        similarities = similarities[0]
        indices = indices[0]

        filtered_products = []

        for sim, idx in zip(similarities, indices):
            if idx < 0 or idx >= len(self.df):
                continue
            
            row = self.df.iloc[idx]

            # 1. Apply Budget Filter (on clean discount price)
            if budget is not None:
                discount_price = row["clean_discount_price"]
                if discount_price is None or discount_price > budget:
                    continue

            # 2. Apply Rating Filter
            if min_rating is not None:
                if row["clean_rating"] < min_rating:
                    continue

            # 3. Apply Sub-category Filter
            if sub_category is not None:
                row_sub_cat = str(row.get("sub_category", "")).lower()
                if sub_category.lower() not in row_sub_cat:
                    continue

            # 4. Apply Brand Filter (from query parser)
            if brand is not None:
                name_lower = str(row["name"]).lower()
                if brand.lower() not in name_lower:
                    continue

            # 5. Apply Category Filter (from query parser)
            if category is not None:
                name_lower = str(row["name"]).lower()
                main_cat = str(row.get("main_category", "")).lower()
                sub_cat = str(row.get("sub_category", "")).lower()
                cat_lower = category.lower()
                if cat_lower not in name_lower and cat_lower not in main_cat and cat_lower not in sub_cat:
                    continue

            # 6. Calculate intelligent Ranking Score:
            # score = (rating * 0.6) + (log(no_of_ratings + 1) * 0.4)
            rating = row["clean_rating"]
            no_ratings = row["clean_no_of_ratings"]
            ranking_score = (rating * 0.6) + (np.log1p(no_ratings) * 0.4)

            filtered_products.append({
                "name": row["name"],
                "main_category": row.get("main_category", ""),
                "sub_category": row.get("sub_category", ""),
                "image": row.get("image", ""),
                "link": row.get("link", ""),
                "ratings": row.get("ratings", ""),
                "no_of_ratings": row.get("no_of_ratings", ""),
                "discount_price": row.get("discount_price", ""),
                "actual_price": row.get("actual_price", ""),
                "clean_discount_price": row["clean_discount_price"],
                "clean_actual_price": row["clean_actual_price"],
                "clean_rating": row["clean_rating"],
                "clean_no_of_ratings": row["clean_no_of_ratings"],
                "semantic_similarity": round(float(sim), 4),
                "ranking_score": round(float(ranking_score), 4)
            })

        # Sort results by the specified Ranking Score descending
        filtered_products.sort(key=lambda x: x["ranking_score"], reverse=True)

        results = filtered_products[:top_k]
        
        retrieval_time = time.time() - start_time
        log_retrieval(query, self.dataset_name, retrieval_time, len(results))

        return results


if __name__ == "__main__":
    # Test retrieval on Lloyd/LG ACs
    base_dir = Path(__file__).resolve().parent.parent
    sample_csv = base_dir / "datasets" / "chatbot_dataset" / "Air Conditioners.csv"
    
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    if sample_csv.exists():
        retriever = ProductRetriever(str(sample_csv))
        results = retriever.search("Inverter split AC under 40000 with 4 star rating", top_k=3)
        print("\nSearch results for parsed filters:")
        for r in results:
            display_price = str(r['discount_price']).replace('₹', 'Rs.').strip()
            print(f"- {r['name']} | Price: {display_price} | Rating: {r['ratings']} | Rank Score: {r['ranking_score']}")
    else:
        print(f"Sample CSV not found at: {sample_csv}")