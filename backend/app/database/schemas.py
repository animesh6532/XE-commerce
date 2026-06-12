from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# =====================================================
# AUTH SCHEMAS
# =====================================================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


# =====================================================
# PRODUCT SCHEMAS
# =====================================================

class ProductCreate(BaseModel):
    name: str
    description: str
    category: str
    brand: str
    price: float
    stock: int
    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    brand: str
    price: float
    stock: int
    rating: float

    class Config:
        from_attributes = True


# =====================================================
# CART SCHEMAS
# =====================================================

class CartCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartUpdate(BaseModel):
    quantity: int


class CouponRequest(BaseModel):
    code: str


# =====================================================
# ORDER SCHEMAS
# =====================================================

class OrderCreate(BaseModel):
    shipping_address: str
    payment_method: str


class OrderStatusUpdate(BaseModel):
    status: str


class ReturnOrderRequest(BaseModel):
    reason: str


# =====================================================
# REVIEW SCHEMAS
# =====================================================

class ReviewCreate(BaseModel):
    product_id: int
    rating: float
    comment: str


class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None


# =====================================================
# WISHLIST SCHEMAS
# =====================================================

class WishlistRequest(BaseModel):
    product_id: int


# =====================================================
# RECOMMENDATION SCHEMAS
# =====================================================

class RecommendationRequest(BaseModel):
    user_id: int
    top_k: int = 10


class SimilarProductRequest(BaseModel):
    product_id: int
    top_k: int = 10


class BudgetRecommendationRequest(BaseModel):
    category: str
    budget: float
    top_k: int = 10


# =====================================================
# SENTIMENT SCHEMAS
# =====================================================

class SentimentRequest(BaseModel):
    text: str


class BatchSentimentRequest(BaseModel):
    reviews: List[str]


# =====================================================
# SEARCH SCHEMAS
# =====================================================

class SearchRequest(BaseModel):
    query: str
    page: int = 1
    limit: int = 20


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 10


# =====================================================
# PRICE PREDICTION SCHEMAS
# =====================================================

class PricePredictionRequest(BaseModel):
    product_id: int


class BulkPredictionRequest(BaseModel):
    product_ids: List[int]


class PriceComparisonRequest(BaseModel):
    product_ids: List[int]


# =====================================================
# CHATBOT SCHEMAS
# =====================================================

class QueryRequest(BaseModel):
    query: str
    budget: Optional[float] = None
    min_rating: Optional[float] = None


class CompareRequest(BaseModel):
    query: str


class RecommendRequest(BaseModel):
    query: str
    top_k: int = 5


# =====================================================
# USER ACTIVITY SCHEMAS
# =====================================================

class ProductViewRequest(BaseModel):
    product_id: int


class SearchActivityRequest(BaseModel):
    query: str


class ClickActivityRequest(BaseModel):
    product_id: int
    source: Optional[str] = None


# =====================================================
# VOICE SEARCH SCHEMAS
# =====================================================

class VoiceTextRequest(BaseModel):
    text: str


# =====================================================
# ANALYTICS SCHEMAS
# =====================================================

class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_revenue: float


# =====================================================
# RESPONSE MESSAGE
# =====================================================

class MessageResponse(BaseModel):
    success: bool
    message: str


# =====================================================
# PAGINATION
# =====================================================

class Pagination(BaseModel):
    page: int
    limit: int
    total: int


# =====================================================
# HEALTH CHECK
# =====================================================

class HealthResponse(BaseModel):
    status: str
    service: str