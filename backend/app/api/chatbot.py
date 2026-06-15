# chatbot.py

import sys
import logging
import threading
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd

# Import database connection and models
from app.database.connection import get_db
from app.database.models import Product

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


def clean_nan(obj: Any) -> Any:
    """
    Recursively converts nan, inf, and -inf values to 0.0.
    Converts numpy and pandas structures to standard Python counterparts.
    """
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(x) for x in obj]
    elif isinstance(obj, tuple):
        return tuple(clean_nan(x) for x in obj)
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, str):
        return obj
    elif obj is None:
        return None
    elif isinstance(obj, (np.floating, np.integer)):
        val = obj.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return 0.0
        return val
    elif pd.isna(obj):
        return 0.0
    return obj


def map_products_to_db(products: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    """
    Looks up matching products in SQLite database by name, updating their IDs
    and storefront link attributes.
    """
    mapped = []
    for p in products:
        name = p.get("name")
        if not name:
            mapped.append(p)
            continue
        
        # 1. Try exact match (case insensitive)
        db_prod = db.query(Product).filter(Product.name.ilike(name)).first()
        
        # 2. Try substring match if not found
        if not db_prod:
            db_prod = db.query(Product).filter(Product.name.ilike(f"%{name}%")).first()
            
        # 3. Try match of first 3 words of the name if not found
        if not db_prod:
            words = name.split()
            if len(words) > 2:
                short_name = " ".join(words[:3])
                db_prod = db.query(Product).filter(Product.name.ilike(f"%{short_name}%")).first()
                
        # 4. Fallback to first word if not found
        if not db_prod:
            words = name.split()
            if words:
                db_prod = db.query(Product).filter(Product.name.ilike(f"%{words[0]}%")).first()

        if db_prod:
            p["id"] = db_prod.id
            p["link"] = f"/product/{db_prod.id}"
        else:
            p["id"] = None
            p["link"] = "#"
        mapped.append(p)
    return mapped


# --- Endpoints ---

@router.post('/query')
@router.post('/chat/query')
def query_chatbot(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Standard query endpoint running the full RAG pipeline and returning the response text, 
    matching products, and LLM source (Ollama or template fallback).
    """
    logger.info(f"FastAPI: query_chatbot called with '{request.query}'")
    try:
        res = chatbot.generate_response(request.query)
        if res.get("status") == "error":
            # Graceful fallback for retrieval failure
            res = {
                "status": "success",
                "response": "I couldn't find exact information, but I can still help you explore products.",
                "rag_data": {
                    "query": request.query,
                    "routed_dataset": "unknown",
                    "routing_similarity": 0.0,
                    "top_5_datasets": [],
                    "products": [],
                    "prompt": "",
                    "status": "success"
                },
                "source": "fallback"
            }
        else:
            if "rag_data" in res and "products" in res["rag_data"]:
                res["rag_data"]["products"] = map_products_to_db(res["rag_data"]["products"], db)
        
        # Log session history
        add_to_history(
            query=request.query,
            response=res["response"],
            source=res["source"],
            routed_dataset=res["rag_data"].get("routed_dataset", "unknown") if res.get("rag_data") else "unknown"
        )

        # Log details: user query, retrieved documents, similarity scores, final response
        products = res.get("rag_data", {}).get("products", []) if res.get("rag_data") else []
        sim_scores = [p.get("semantic_similarity") for p in products]
        logger.info(f"Chatbot User Query: {request.query}")
        logger.info(f"Retrieved Documents: {products}")
        logger.info(f"Similarity Scores: {sim_scores}")
        logger.info(f"Final Response: {res.get('response')}")

        return clean_nan(res)
    except Exception as e:
        logger.error(f"Error in query_chatbot API: {e}", exc_info=True)
        fallback_res = {
            "status": "success",
            "response": "AI Assistant is temporarily unavailable.",
            "rag_data": {
                "query": request.query,
                "routed_dataset": "unknown",
                "routing_similarity": 0.0,
                "top_5_datasets": [],
                "products": [],
                "prompt": "",
                "status": "success"
            },
            "source": "fallback"
        }
        return clean_nan(fallback_res)


@router.post('/compare')
@router.post('/chat/compare')
def compare_products(request: CompareRequest, db: Session = Depends(get_db)):
    """
    Comparison endpoint matching two brands or products (e.g. Boat vs JBL) and returning 
    prices, ratings, pros, cons, and recommendations.
    """
    logger.info(f"FastAPI: compare_products called with '{request.query}'")
    try:
        res = comparison_engine.compare(request.query)
        if res.get("status") == "error":
            fallback_text = "I couldn't find exact information, but I can still help you explore products."
            res = {
                "status": "success",
                "brand_a": "Brand",
                "brand_b": "Brand",
                "category": "Category",
                "dataset": "unknown",
                "product_a": None,
                "product_b": None,
                "comparison": {
                    "price": "N/A",
                    "ratings": "N/A",
                    "review_count": "N/A",
                    "pros": {"Brand": []},
                    "cons": {"Brand": []},
                    "recommendation": fallback_text
                }
            }
        else:
            if res.get("product_a"):
                mapped_a = map_products_to_db([res["product_a"]], db)
                res["product_a"] = mapped_a[0]
            if res.get("product_b"):
                mapped_b = map_products_to_db([res["product_b"]], db)
                res["product_b"] = mapped_b[0]

        # Log details
        logger.info(f"Compare User Query: {request.query}")
        logger.info(f"Product A: {res.get('product_a')}")
        logger.info(f"Product B: {res.get('product_b')}")
        logger.info(f"Final Recommendation: {res.get('comparison', {}).get('recommendation')}")

        return clean_nan(res)
    except Exception as e:
        logger.error(f"Error in compare_products API: {e}", exc_info=True)
        fallback_text = "AI Assistant is temporarily unavailable."
        fallback_res = {
            "status": "success",
            "brand_a": "Brand",
            "brand_b": "Brand",
            "category": "Category",
            "dataset": "unknown",
            "product_a": None,
            "product_b": None,
            "comparison": {
                "price": "N/A",
                "ratings": "N/A",
                "review_count": "N/A",
                "pros": {"Brand": []},
                "cons": {"Brand": []},
                "recommendation": fallback_text
            }
        }
        return clean_nan(fallback_res)


@router.post('/recommend')
@router.post('/chat/recommend')
def recommend_products(request: RecommendRequest, db: Session = Depends(get_db)):
    """
    Recommendation discovery endpoint that retrieves matching product cards.
    """
    logger.info(f"FastAPI: recommend_products called with '{request.query}'")
    try:
        res = chatbot.generate_response(request.query)
        if res.get("status") == "error":
            res = {
                "status": "success",
                "response": "I couldn't find exact information, but I can still help you explore products.",
                "rag_data": {
                    "query": request.query,
                    "routed_dataset": "unknown",
                    "routing_similarity": 0.0,
                    "top_5_datasets": [],
                    "products": [],
                    "prompt": "",
                    "status": "success"
                },
                "source": "fallback"
            }
        else:
            if "rag_data" in res and "products" in res["rag_data"]:
                res["rag_data"]["products"] = map_products_to_db(res["rag_data"]["products"], db)

        # Log details
        products = res.get("rag_data", {}).get("products", []) if res.get("rag_data") else []
        sim_scores = [p.get("semantic_similarity") for p in products]
        logger.info(f"Recommend User Query: {request.query}")
        logger.info(f"Retrieved Documents: {products}")
        logger.info(f"Similarity Scores: {sim_scores}")
        logger.info(f"Final Response: {res.get('response')}")

        return clean_nan(res)
    except Exception as e:
        logger.error(f"Error in recommend_products API: {e}", exc_info=True)
        fallback_res = {
            "status": "success",
            "response": "AI Assistant is temporarily unavailable.",
            "rag_data": {
                "query": request.query,
                "routed_dataset": "unknown",
                "routing_similarity": 0.0,
                "top_5_datasets": [],
                "products": [],
                "prompt": "",
                "status": "success"
            },
            "source": "fallback"
        }
        return clean_nan(fallback_res)



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
