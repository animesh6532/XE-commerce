from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.services.search_service import SearchService

router = APIRouter()

search_service = SearchService()


# ---------- Pydantic Schemas ----------

class SearchRequest(BaseModel):
    query: str
    page: int = 1
    limit: int = 20


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 10


class FilterSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None


# ---------- Keyword Search ----------

@router.post("/")
def search_products(
        request: SearchRequest,
        db: Session = Depends(get_db)
):

    return search_service.keyword_search(
        db=db,
        query=request.query,
        page=request.page,
        limit=request.limit
    )


# ---------- Semantic Search ----------

@router.post("/semantic")
def semantic_search(
        request: SemanticSearchRequest
):

    return search_service.semantic_search(
        query=request.query,
        top_k=request.top_k
    )


# ---------- Autocomplete ----------

@router.get("/autocomplete")
def autocomplete(
        query: str
):

    return search_service.autocomplete(
        query=query
    )


# ---------- Search Suggestions ----------

@router.get("/suggestions")
def search_suggestions(
        query: str
):

    return search_service.search_suggestions(
        query=query
    )


# ---------- Filter Search ----------

@router.post("/filter")
def filter_search(
        request: FilterSearchRequest,
        db: Session = Depends(get_db)
):

    return search_service.filter_search(
        db=db,
        query=request.query,
        category=request.category,
        brand=request.brand,
        min_price=request.min_price,
        max_price=request.max_price,
        min_rating=request.min_rating
    )


# ---------- Category Search ----------

@router.get("/category/{category}")
def category_search(
        category: str,
        db: Session = Depends(get_db)
):

    return search_service.category_search(
        db=db,
        category=category
    )


# ---------- Trending Searches ----------

@router.get("/trending")
def trending_searches():

    return search_service.trending_searches()


# ---------- Recent Searches ----------

@router.get("/recent")
def recent_searches(
        current_user=Depends(get_current_user)
):

    return search_service.recent_searches(
        user_id=current_user.id
    )


# ---------- Save Search History ----------

@router.post("/save")
def save_search(
        query: str,
        current_user=Depends(get_current_user)
):

    return search_service.save_search(
        user_id=current_user.id,
        query=query
    )


# ---------- AI Search ----------

@router.post("/ai")
def ai_search(
        request: SemanticSearchRequest
):

    return search_service.ai_search(
        query=request.query,
        top_k=request.top_k
    )


# ---------- Similar Products ----------

@router.get("/similar/{product_id}")
def similar_products(
        product_id: int
):

    return search_service.similar_products(
        product_id
    )


# ---------- Health Check ----------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "search"
    }