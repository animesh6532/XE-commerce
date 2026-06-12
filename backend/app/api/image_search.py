from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.image_search_service import ImageSearchService

router = APIRouter()

image_service = ImageSearchService()


# ---------------- Image Upload Search ----------------
@router.post("/search")
async def image_search(
        image: UploadFile = File(...)
):
    """
    Search products using uploaded image.
    """

    try:
        result = await image_service.search_by_image(image)

        return {
            "success": True,
            "results": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Similar Products ----------------
@router.post("/similar")
async def similar_products(
        image: UploadFile = File(...),
        top_k: int = 5
):
    """
    Find top K similar products.
    """

    try:

        result = await image_service.find_similar_products(
            image=image,
            top_k=top_k
        )

        return {
            "success": True,
            "top_k": top_k,
            "products": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Reverse Image Search ----------------
@router.post("/reverse")
async def reverse_image_search(
        image: UploadFile = File(...)
):
    """
    Reverse image search endpoint.
    """

    try:

        result = await image_service.reverse_search(
            image
        )

        return {
            "success": True,
            "matches": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Image Recommendations ----------------
@router.post("/recommend")
async def image_recommendation(
        image: UploadFile = File(...),
        top_k: int = 10
):
    """
    Recommend products based on uploaded image.
    """

    try:

        result = await image_service.recommend_products(
            image=image,
            top_k=top_k
        )

        return {
            "success": True,
            "recommendations": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- Health Check ----------------
@router.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "image-search"
    }