# chatbot.py

import sys
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Ensure ml_models/chatbot and dashboard are in python path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CHATBOT_DIR = BASE_DIR / "ml_models" / "chatbot"
DASHBOARD_DIR = BASE_DIR / "dashboard"

if str(CHATBOT_DIR) not in sys.path:
    sys.path.append(str(CHATBOT_DIR))
if str(DASHBOARD_DIR) not in sys.path:
    sys.path.append(str(DASHBOARD_DIR))

try:
    from llm_chatbot import LLMChatbot
    from comparison_engine import ComparisonEngine
    from analytics_dashboard import generate_dashboard_html
except ImportError as e:
    logging.error(f"Failed to import chatbot core modules: {e}")
    # Define placeholder classes for safety if imports fail during setup
    class LLMChatbot:
        def generate_response(self, q): return {"status": "error", "message": "Import error"}
    class ComparisonEngine:
        def compare(self, q): return {"status": "error", "message": "Import error"}
    def generate_dashboard_html(): return "<h1>Dashboard unavailable</h1>"

router = APIRouter()
logger = logging.getLogger(__name__)

# Global instances (Singletons loaded once)
chatbot = LLMChatbot()
comparison_engine = ComparisonEngine(category_router=chatbot.pipeline.router)

# Thread-safe in-memory session history
history_lock = threading.Lock()
chat_history: List[Dict[str, Any]] = []


# --- Pydantic Schemas ---

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user shopping or discovery query.", example="Mechanical gaming keyboard under 5000")
    budget: Optional[float] = Field(None, description="Optional budget filter.", example=5000.0)
    min_rating: Optional[float] = Field(None, description="Optional minimum customer rating (0.0 to 5.0).", example=4.0)


class CompareRequest(BaseModel):
    query: str = Field(..., description="The query comparing brands or products.", example="Samsung vs OnePlus")


class RecommendRequest(BaseModel):
    query: str = Field(..., description="The product recommendation query.", example="best AC under 35000")
    top_k: int = Field(5, description="Number of products to return.", example=5)


# --- Helper Methods ---

def add_to_history(query: str, response: str, source: str, routed_dataset: str):
    with history_lock:
        chat_history.append({
            "query": query,
            "response": response,
            "source": source,
            "routed_dataset": routed_dataset
        })


# --- Endpoints ---

@router.post('/query')
@router.post('/chat/query')
def query_chatbot(request: QueryRequest):
    """
    Standard query endpoint running the full RAG pipeline and returning the response text, 
    matching products, and LLM source (Ollama or template fallback).
    """
    logger.info(f"FastAPI: query_chatbot called with '{request.query}'")
    try:
        res = chatbot.generate_response(request.query)
        if res["status"] == "error":
            raise HTTPException(status_code=500, detail=res.get("message", "Retrieval execution error"))
        
        # Log session history
        add_to_history(
            query=request.query,
            response=res["response"],
            source=res["source"],
            routed_dataset=res["rag_data"].get("routed_dataset", "unknown")
        )
        return res
    except Exception as e:
        logger.error(f"Error in query_chatbot API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/compare')
@router.post('/chat/compare')
def compare_products(request: CompareRequest):
    """
    Comparison endpoint matching two brands or products (e.g. Boat vs JBL) and returning 
    prices, ratings, pros, cons, and recommendations.
    """
    logger.info(f"FastAPI: compare_products called with '{request.query}'")
    try:
        res = comparison_engine.compare(request.query)
        if res["status"] == "error":
            raise HTTPException(status_code=400, detail=res.get("message", "Entity comparison failed"))
        return res
    except Exception as e:
        logger.error(f"Error in compare_products API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/recommend')
@router.post('/chat/recommend')
def recommend_products(request: RecommendRequest):
    """
    Recommendation discovery endpoint that retrieves matching product cards.
    """
    logger.info(f"FastAPI: recommend_products called with '{request.query}'")
    try:
        res = chatbot.generate_response(request.query)
        if res["status"] == "error":
            raise HTTPException(status_code=500, detail=res.get("message", "Recommendation error"))
        return res
    except Exception as e:
        logger.error(f"Error in recommend_products API: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/history')
@router.get('/chat/history')
def get_history():
    """Retrieves session chatbot interactions history."""
    with history_lock:
        return {"history": chat_history}


@router.get('/categories')
@router.get('/chat/categories')
def get_categories():
    """Retrieves all available product category datasets."""
    try:
        return {"categories": chatbot.pipeline.router.datasets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/analytics/dashboard', response_class=HTMLResponse)
def get_analytics_dashboard():
    """
    Serves the Plotly analytics dashboard as an interactive HTML page.
    """
    try:
        return generate_dashboard_html()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
