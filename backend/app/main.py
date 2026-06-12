from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Database
from app.database.connection import engine
from app.database.models import Base

# Routers
from app.api import (
    auth,
    products,
    cart,
    orders,
    reviews,
    wishlist,
    recommendations,
    chatbot,
    analytics,
    sentiment,
    search,
    voice_search,
    image_search,
    price_prediction,
    user_activity
)

app = FastAPI(
    title="Xecommerce AI Platform",
    description="AI Powered E-Commerce Platform API",
    version="1.0.0"
)

# Create tables during FastAPI startup event
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# CORS
origins = [
    "http://localhost:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------------- Authentication ----------------
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

# ---------------- Products ----------------
app.include_router(
    products.router,
    prefix="/api/products",
    tags=["Products"]
)

# ---------------- Cart ----------------
app.include_router(
    cart.router,
    prefix="/api/cart",
    tags=["Cart"]
)

# ---------------- Orders ----------------
app.include_router(
    orders.router,
    prefix="/api/orders",
    tags=["Orders"]
)

# ---------------- Reviews ----------------
app.include_router(
    reviews.router,
    prefix="/api/reviews",
    tags=["Reviews"]
)

# ---------------- Wishlist ----------------
app.include_router(
    wishlist.router,
    prefix="/api/wishlist",
    tags=["Wishlist"]
)

# ---------------- Recommendation System ----------------
app.include_router(
    recommendations.router,
    prefix="/api/recommendations",
    tags=["Recommendations"]
)

# ---------------- Chatbot ----------------
app.include_router(
    chatbot.router,
    prefix="/api/chatbot",
    tags=["Chatbot"]
)

# ---------------- Analytics ----------------
app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"]
)

# ---------------- Sentiment Analysis ----------------
app.include_router(
    sentiment.router,
    prefix="/api/sentiment",
    tags=["Sentiment Analysis"]
)

# ---------------- Semantic Search ----------------
app.include_router(
    search.router,
    prefix="/api/search",
    tags=["Search"]
)

# ---------------- Voice Search ----------------
app.include_router(
    voice_search.router,
    prefix="/api/voice-search",
    tags=["Voice Search"]
)

# ---------------- Image Search ----------------
app.include_router(
    image_search.router,
    prefix="/api/image-search",
    tags=["Image Search"]
)

# ---------------- Price Prediction ----------------
app.include_router(
    price_prediction.router,
    prefix="/api/price-prediction",
    tags=["Price Prediction"]
)

# ---------------- User Activity ----------------
app.include_router(
    user_activity.router,
    prefix="/api/user-activity",
    tags=["User Activity"]
)


@app.get("/", tags=["Root"])
def root():
    return {
        "status": "success",
        "message": "Xecommerce AI Backend Running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy"
    }