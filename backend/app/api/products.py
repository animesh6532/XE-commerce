from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.schemas import ProductCreate, ProductUpdate
from app.middleware.auth import get_current_user
from app.services.product_service import ProductService

router = APIRouter()

product_service = ProductService()


# ---------------- Health Check ----------------
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "products"
    }


# ---------------- Get All Products ----------------
@router.get("/")
def get_products(
        page: int = 1,
        limit: int = 20,
        db: Session = Depends(get_db)
):
    return product_service.get_products(
        db=db,
        page=page,
        limit=limit
    )


# ---------------- Get Product By ID ----------------
@router.get("/{product_id}")
def get_product(
        product_id: int,
        db: Session = Depends(get_db)
):
    return product_service.get_product_by_id(
        db=db,
        product_id=product_id
    )


# ---------------- Search Products ----------------
@router.get("/search/")
def search_products(
        query: str,
        db: Session = Depends(get_db)
):
    return product_service.search_products(
        db=db,
        query=query
    )


# ---------------- Filter Products ----------------
@router.get("/filter/")
def filter_products(
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[float] = None,
        brand: Optional[str] = None,
        db: Session = Depends(get_db)
):
    return product_service.filter_products(
        db=db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        brand=brand
    )


# ---------------- Category Products ----------------
@router.get("/category/{category_name}")
def category_products(
        category_name: str,
        db: Session = Depends(get_db)
):
    return product_service.category_products(
        db=db,
        category_name=category_name
    )


# ---------------- Create Product ----------------
@router.post("/")
def create_product(
        product: ProductCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return product_service.create_product(
        db=db,
        product=product,
        user=current_user
    )


# ---------------- Update Product ----------------
@router.put("/{product_id}")
def update_product(
        product_id: int,
        product: ProductUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return product_service.update_product(
        db=db,
        product_id=product_id,
        product=product,
        user=current_user
    )


# ---------------- Delete Product ----------------
@router.delete("/{product_id}")
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return product_service.delete_product(
        db=db,
        product_id=product_id,
        user=current_user
    )


# ---------------- Featured Products ----------------
@router.get("/featured/list")
def featured_products(
        db: Session = Depends(get_db)
):
    return product_service.featured_products(db)


# ---------------- Trending Products ----------------
@router.get("/trending/list")
def trending_products(
        db: Session = Depends(get_db)
):
    return product_service.trending_products(db)


# ---------------- Deal Products ----------------
@router.get("/deals/list")
def deal_products(
        db: Session = Depends(get_db)
):
    return product_service.deal_products(db)


# ---------------- Similar Products ----------------
@router.get("/similar/{product_id}")
def similar_products(
        product_id: int,
        db: Session = Depends(get_db)
):
    return product_service.similar_products(
        db=db,
        product_id=product_id
    )


# ---------------- Product Statistics ----------------
@router.get("/stats/overview")
def product_statistics(
        db: Session = Depends(get_db)
):
    return product_service.product_statistics(db)


# ---------------- Inventory Status ----------------
@router.get("/inventory/status")
def inventory_status(
        db: Session = Depends(get_db)
):
    return product_service.inventory_status(db)

