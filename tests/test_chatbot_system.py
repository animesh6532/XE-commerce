# tests/test_chatbot_system.py

import unittest
import sys
from pathlib import Path
import numpy as np

# Dynamically add the chatbot directory to Python path
CHATBOT_DIR = Path(__file__).resolve().parent.parent / "ml_models" / "chatbot"
sys.path.append(str(CHATBOT_DIR))

try:
    from category_router import CategoryRouter
    from retrieval import ProductRetriever
    from embeddings import ProductEmbedder
    from faiss_index import FAISSIndexManager
    from prompt_templates import PromptGenerator
    from chatbot import ShoppingAssistant
    from rag_pipeline import RAGPipeline
    MODULES_IMPORTED = True
except ImportError as e:
    print(f"Import Error: {e}")
    MODULES_IMPORTED = False


class TestChatbotSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.embedder = ProductEmbedder()

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "Chatbot modules failed to import.")
        self.embedder = self.__class__.embedder

    def test_query_parser(self):
        """Tests natural language constraint extraction from user queries."""
        assistant = ShoppingAssistant()
        
        # Test budget extraction
        q1 = "gaming mouse under 3000 rupees"
        clean_q1, budget_q1, rating_q1 = assistant.parse_query_metadata(q1)
        self.assertEqual(clean_q1, "gaming mouse")
        self.assertEqual(budget_q1, 3000.0)
        self.assertIsNone(rating_q1)

        # Test budget with multiplier 'k'
        q2 = "split AC below 40k"
        clean_q2, budget_q2, rating_q2 = assistant.parse_query_metadata(q2)
        self.assertEqual(clean_q2, "split AC")
        self.assertEqual(budget_q2, 40000.0)

        # Test rating extraction
        q3 = "rated 4.5 star headphones"
        clean_q3, budget_q3, rating_q3 = assistant.parse_query_metadata(q3)
        self.assertEqual(clean_q3, "headphones")
        self.assertEqual(rating_q3, 4.5)

        # Test compound query
        q4 = "Inverter split AC under 45000 and 4+ stars"
        clean_q4, budget_q4, rating_q4 = assistant.parse_query_metadata(q4)
        self.assertEqual(clean_q4, "Inverter split AC and")
        self.assertEqual(budget_q4, 45000.0)
        self.assertEqual(rating_q4, 4.0)

    def test_intent_detection(self):
        """Tests user intent classification."""
        assistant = ShoppingAssistant()
        
        self.assertEqual(assistant.detect_query_type("compare Samsung vs LG"), "comparison")
        self.assertEqual(assistant.detect_query_type("what is the difference between X and Y"), "comparison")
        self.assertEqual(assistant.detect_query_type("explain why this model is better"), "explanation")
        self.assertEqual(assistant.detect_query_type("show me the best laptops"), "recommendation")

    def test_embeddings_generation(self):
        """Tests the SentenceTransformer wrapper."""
        texts = ["hello world", "test product description"]
        embeddings = self.embedder.encode(texts)
        self.assertEqual(embeddings.shape[0], 2)
        self.assertEqual(embeddings.shape[1], 384) # all-MiniLM-L6-v2 is 384 dimensions
        self.assertEqual(embeddings.dtype, np.float32)

    def test_faiss_indexing(self):
        """Tests FAISS index build, search, and load."""
        embeddings = np.random.rand(10, 384).astype(np.float32)
        index = FAISSIndexManager.build_index(embeddings)
        
        # Test count
        self.assertEqual(index.ntotal, 10)
        
        # Test similarity search
        queries = np.random.rand(2, 384).astype(np.float32)
        sims, indices = FAISSIndexManager.similarity_search(index, queries, k=3)
        self.assertEqual(sims.shape, (2, 3))
        self.assertEqual(indices.shape, (2, 3))

    def test_prompt_generation(self):
        """Tests formatting product data in prompts."""
        products = [
            {
                "name": "Test Product 1",
                "main_category": "electronics",
                "sub_category": "mouse",
                "discount_price": "₹1,500",
                "actual_price": "₹2,000",
                "ratings": "4.5",
                "no_of_ratings": "120",
                "link": "http://test.com/1",
                "semantic_similarity": 0.85,
                "ranking_score": 5.2
            }
        ]
        
        prompt = PromptGenerator.generate_recommendation_prompt("gaming mouse", products, budget_limit=2000.0)
        self.assertIn("Test Product 1", prompt)
        self.assertIn("Rs.1,500", prompt) # Currency symbol ₹ should be replaced with Rs.
        self.assertIn("electronics > mouse", prompt)
        self.assertIn("gaming mouse", prompt)

    def test_category_router(self):
        """Tests dataset discovery and profile caching in CategoryRouter."""
        router = CategoryRouter()
        # Verify cache was loaded
        self.assertGreater(len(router.datasets), 0)
        self.assertIn("Air Conditioners", router.datasets)
        
        # Test routing
        result = router.find_best_dataset("Air conditioner with dual inverter cooling")
        self.assertEqual(result["dataset"], "Air Conditioners")
        self.assertGreater(result["similarity"], 0.2)


if __name__ == "__main__":
    unittest.main()
