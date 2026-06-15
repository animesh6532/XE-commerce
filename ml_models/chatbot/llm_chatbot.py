# llm_chatbot.py

import httpx
import logging
from typing import Dict, Any, Optional, List
from rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


class LLMChatbot:
    """
    Combines RAGPipeline (intent classification, dataset routing, FAISS retrieval, 
    and prompt generation) with Ollama Llama3 execution.
    Provides robust, recruiter-grade responses and a smart fallback when Ollama is offline.
    """

    def __init__(self, ollama_url: str = "http://localhost:11434", model_name: str = "llama3"):
        """
        Initializes the LLM Chatbot with Ollama settings and RAG pipeline.
        """
        self.ollama_url = ollama_url
        self.model_name = model_name
        logger.info("Initializing LLMChatbot RAG Pipeline...")
        self.pipeline = RAGPipeline()
        logger.info("LLMChatbot initialized successfully.")

    def _check_ollama(self) -> bool:
        """Checks if the Ollama local service is up and running."""
        try:
            # Send simple check to Ollama health/home
            res = httpx.get(self.ollama_url, timeout=1.5)
            return res.status_code == 200
        except Exception:
            logger.debug(f"Ollama service check failed at {self.ollama_url}. Using local fallback.")
            return False

    def generate_response(self, user_query: str) -> Dict[str, Any]:
        """
        Generates an end-to-end shopping recommendation/explanation using Ollama or fallback.
        """
        import time
        from logging_utils import log_chatbot
        start_time = time.time()

        # 1. Execute RAG query to retrieve intent, routed dataset, products, and prompt
        # We also auto-detect query type (recs vs comparison vs explanation)
        q_lower = user_query.lower()
        if any(w in q_lower for w in ["compare", "difference", "vs", "versus"]):
            query_type = "comparison"
        elif any(w in q_lower for w in ["why", "explain", "reason", "justify"]):
            query_type = "explanation"
        else:
            query_type = "recommendation"

        rag_res = self.pipeline.query(user_query, query_type=query_type)
        if rag_res.get("status") == "error":
            logger.warning(f"RAG query returned error: {rag_res.get('message')}. Using graceful fallback.")
            fallback_text = "I couldn't find exact information, but I can still help you explore products."
            return {
                "status": "success",
                "response": fallback_text,
                "rag_data": {
                    "query": user_query,
                    "routed_dataset": "unknown",
                    "routing_similarity": 0.0,
                    "top_5_datasets": [],
                    "products": [],
                    "prompt": "",
                    "status": "success"
                },
                "source": "fallback"
            }

        # 2. Check if Ollama is available
        ollama_active = self._check_ollama()

        if ollama_active:
            try:
                logger.info(f"Ollama active. Sending prompt to model '{self.model_name}'...")
                response = httpx.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": rag_res["prompt"],
                        "stream": False
                    },
                    timeout=20.0
                )
                if response.status_code == 200:
                    llama_text = response.json().get("response", "").strip()
                    logger.info("Llama3 response generated successfully.")
                    
                    recommendation_time = time.time() - start_time
                    log_chatbot(user_query, rag_res.get("routed_dataset", "unknown"), recommendation_time, "ollama")
                    
                    return {
                        "status": "success",
                        "response": llama_text,
                        "rag_data": rag_res,
                        "source": "ollama"
                    }
                else:
                    logger.warning(f"Ollama returned non-200 code: {response.status_code}. Using fallback.")
            except Exception as e:
                logger.warning(f"Ollama request timed out or errored: {e}. Using fallback.")

        # 3. Fallback: Generate local recruiter-grade templates
        logger.info("Using local fallback template generator.")
        fallback_text = self._generate_local_fallback(user_query, query_type, rag_res)
        
        recommendation_time = time.time() - start_time
        log_chatbot(user_query, rag_res.get("routed_dataset", "unknown"), recommendation_time, "fallback")

        return {
            "status": "success",
            "response": fallback_text,
            "rag_data": rag_res,
            "source": "fallback"
        }

    def _generate_local_fallback(self, query: str, query_type: str, rag_res: Dict[str, Any]) -> str:
        products = rag_res.get("products", [])
        dataset = rag_res.get("routed_dataset", "unknown")

        if not products:
            return f"I searched the '{dataset}' catalog, but couldn't find matches fitting your query filters. Try widening your criteria!"

        best = products[0]
        best_price = str(best.get("discount_price", "N/A")).replace("₹", "Rs.").strip()

        if query_type == "explanation":
            return (
                f"I highly recommend the **{best['name']}** from our **{dataset}** selection.\n\n"
                f"**Why this product fits your query:**\n"
                f"- **Value**: Offered at a competitive discount price of **{best_price}** (original: {str(best.get('actual_price', 'N/A')).replace('₹', 'Rs.')}).\n"
                f"- **Quality**: Carries a strong rating of **{best['clean_rating']} ⭐** based on **{int(best['clean_no_of_ratings']):,}** customer ratings.\n"
                f"- **Relevance**: Has a calculated search relevance score of **{best['ranking_score']}**, indicating high quality and matching profile."
            )
            
        elif query_type == "comparison":
            comparison = f"I compared the top choices in the **{dataset}** catalog for your comparison query:\n\n"
            if len(products) > 1:
                cheapest = min(products, key=lambda x: x["clean_discount_price"] or float("inf"))
                most_popular = max(products, key=lambda x: x["clean_no_of_ratings"])
                highest_rated = max(products, key=lambda x: x["clean_rating"])
                
                cheap_price = str(cheapest.get("discount_price", "N/A")).replace("₹", "Rs.").strip()

                comparison += f"- 💰 **Best Budget Option**: **{cheapest['name']}** priced at **{cheap_price}**.\n"
                comparison += f"- 🔥 **Most Popular Choice**: **{most_popular['name']}** with **{int(most_popular['clean_no_of_ratings']):,}** customer ratings.\n"
                comparison += f"- ⭐ **Highest Rated Option**: **{highest_rated['name']}** carrying a customer rating of **{highest_rated['clean_rating']} ⭐**.\n\n"
                comparison += f"**Our Recommendation**: If budget is your priority, go with **{cheapest['name']}**. Otherwise, the **{most_popular['name']}** is the most trusted choice among other buyers."
            else:
                comparison += f"Only one relevant product was found for this comparison: **{best['name']}** priced at **{best_price}**."
            return comparison
            
        else:  # recommendation
            recs = (
                f"I discovered some great options in the **{dataset}** catalog. "
                f"Applying our popularity-weighted rank score, here are the top recommendations:\n\n"
            )
            for idx, p in enumerate(products, start=1):
                price_str = str(p.get("discount_price", "N/A")).replace("₹", "Rs.").strip()
                recs += f"{idx}. **{p['name']}** — **{price_str}** ({p['clean_rating']} ⭐, {int(p['clean_no_of_ratings']):,} reviews)\n"
            
            recs += f"\n💡 **My Recommendation**: The best match is **{best['name']}** because it offers the optimal balance between high score, pricing, and ratings."
            return recs


if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    bot = LLMChatbot()
    res = bot.generate_response("Best AC under 35000")
    print(f"\nResponse Source: {res['source']}")
    print(f"Routed to: {res['rag_data']['routed_dataset']}")
    print(f"Response:\n{res['response']}")
