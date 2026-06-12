# rag_pipeline.py

import logging
from typing import List, Dict, Any, Optional

from category_router import CategoryRouter
from retrieval import ProductRetriever
from prompt_templates import PromptGenerator
from embeddings import ProductEmbedder

# Configure logger
logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Orchestrates the entire Retrieval-Augmented Generation flow:
    Routing -> Retrieving -> Filtering -> Ranking -> Prompt Generation.
    """

    def __init__(self, force_rebuild_router: bool = False):
        """Initializes the RAG Pipeline by loading the router and embedding model."""
        logger.info("Initializing RAG Pipeline...")
        try:
            # Router loads dataset profile embeddings
            self.router = CategoryRouter(force_rebuild=force_rebuild_router)
            # Share the same embedder instance across router and retrievers for memory efficiency
            self.embedder = self.router.embedder
            # Memory cache of loaded retrievers so we don't reload CSVs on every query
            self.retriever_cache: Dict[str, ProductRetriever] = {}
            logger.info("RAG Pipeline successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize RAG Pipeline: {e}")
            raise

    def query(
        self,
        user_query: str,
        budget: Optional[float] = None,
        min_rating: Optional[float] = None,
        sub_category: Optional[str] = None,
        top_k: int = 5,
        query_type: str = "recommendation"
    ) -> Dict[str, Any]:
        """
        Executes the full RAG pipeline for a user query.
        
        Args:
            user_query (str): The search or discovery query from the user.
            budget (Optional[float]): Optional budget limit.
            min_rating (Optional[float]): Optional minimum product rating filter.
            sub_category (Optional[str]): Optional sub-category string match filter.
            top_k (int): Number of final ranked recommendations to return. Defaults to 5.
            query_type (str): Type of prompt to generate: 'recommendation', 'comparison', 'explanation', or 'search'.
            
        Returns:
            Dict[str, Any]: Structured results containing routed dataset, ranked products, and generated prompt.
        """
        logger.info(f"Processing query: '{user_query}' | type: {query_type} | filters: budget={budget}, rating={min_rating}, sub_category={sub_category}")
        
        try:
            # 1. Dataset Routing
            routing_result = self.router.find_best_dataset(user_query)
            best_dataset = routing_result["dataset"]
            dataset_path = routing_result["path"]
            similarity = routing_result["similarity"]
            
            top_datasets = self.router.top_k_datasets(user_query, k=5)
            
            logger.info(f"Query routed to dataset '{best_dataset}' with confidence score: {similarity}")
            
            # 2. Retriever Loading (Cached in memory)
            if best_dataset not in self.retriever_cache:
                logger.info(f"Instantiating new ProductRetriever for {best_dataset}...")
                self.retriever_cache[best_dataset] = ProductRetriever(
                    dataset_path=dataset_path, 
                    embedder=self.embedder
                )
            
            retriever = self.retriever_cache[best_dataset]

            # 3. Product Retrieval & Filtering & Ranking
            ranked_products = retriever.search(
                query=user_query,
                budget=budget,
                min_rating=min_rating,
                sub_category=sub_category,
                top_k=top_k
            )
            
            logger.info(f"Retrieved and ranked {len(ranked_products)} matching products.")

            # 4. Prompt Generation
            generated_prompt = ""
            if query_type == "recommendation":
                generated_prompt = PromptGenerator.generate_recommendation_prompt(
                    query=user_query, 
                    products=ranked_products, 
                    budget_limit=budget
                )
            elif query_type == "comparison":
                generated_prompt = PromptGenerator.generate_comparison_prompt(
                    query=user_query, 
                    products=ranked_products
                )
            elif query_type == "explanation":
                # For explanation query, explain the single best match
                best_product = ranked_products[0] if ranked_products else {}
                generated_prompt = PromptGenerator.generate_explanation_prompt(
                    query=user_query, 
                    product=best_product
                )
            elif query_type == "search":
                generated_prompt = PromptGenerator.generate_search_prompt(
                    query=user_query, 
                    products=ranked_products
                )
            else:
                logger.warning(f"Unknown query_type '{query_type}', defaulting to recommendation prompt.")
                generated_prompt = PromptGenerator.generate_recommendation_prompt(
                    query=user_query, 
                    products=ranked_products, 
                    budget_limit=budget
                )

            return {
                "query": user_query,
                "routed_dataset": best_dataset,
                "routing_similarity": similarity,
                "top_5_datasets": top_datasets,
                "products": ranked_products,
                "prompt": generated_prompt,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Error executing RAG Pipeline query: {e}", exc_info=True)
            return {
                "query": user_query,
                "routed_dataset": None,
                "routing_similarity": 0.0,
                "top_5_datasets": [],
                "products": [],
                "prompt": "",
                "status": "error",
                "message": str(e)
            }


if __name__ == "__main__":
    import sys
    # Reconfigure stdout for unicode handling on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # Simple test harness
    pipeline = RAGPipeline()
    res = pipeline.query("Mechanical gaming keyboards under 5000", budget=5000.0, top_k=2)
    
    print("\n--- Routed Category ---")
    print(f"Dataset: {res['routed_dataset']} (Confidence: {res['routing_similarity']})")
    
    print("\n--- Ranked Recommendation Products ---")
    for p in res["products"]:
        disp_price = str(p['discount_price']).replace('₹', 'Rs.').strip()
        print(f"* {p['name']} | Price: {disp_price} | Relevance score: {p['ranking_score']}")
        
    print("\n--- Generated LLM Prompt Context ---")
    print(res["prompt"][:500] + "\n... [TRUNCATED] ...")
