from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship

from app.database.connection import Base


# ==========================
# User Model
# ==========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    role = Column(String(50), default="customer")

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    wishlists = relationship("Wishlist", back_populates="user")
    activities = relationship("UserActivity", back_populates="user")


# ==========================
# Product Model
# ==========================
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text)

    category = Column(String(100))
    brand = Column(String(100))

    price = Column(Float, nullable=False)

    stock = Column(Integer, default=0)

    rating = Column(Float, default=0)

    image_url = Column(String(500))

    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="product")
    carts = relationship("Cart", back_populates="product")
    wishlists = relationship("Wishlist", back_populates="product")


# ==========================
# Cart Model
# ==========================
class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)

    quantity = Column(Integer, default=1)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")


# ==========================
# Order Model
# ==========================
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    total_amount = Column(Float)

    payment_method = Column(String(100))

    status = Column(
        String(50),
        default="Pending"
    )

    shipping_address = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="orders")


# ==========================
# Review Model
# ==========================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    product_id = Column(Integer, ForeignKey("products.id"), index=True)

    rating = Column(Float)

    comment = Column(Text)

    sentiment = Column(String(50))

    is_fake = Column(Boolean, default=False)

    likes = Column(Integer, default=0)

    dislikes = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")


# ==========================
# Wishlist Model
# ==========================
class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    product_id = Column(Integer, ForeignKey("products.id"))

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wishlists")
    product = relationship("Product", back_populates="wishlists")


# ==========================
# User Activity Model
# ==========================
class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    activity_type = Column(String(100))

    product_id = Column(Integer, nullable=True)

    search_query = Column(String(255), nullable=True)

    source = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")


# ==========================
# Search History
# ==========================
class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    query = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# Chat History
# ==========================
class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer)

    query = Column(Text)

    response = Column(Text)

    source = Column(String(100))

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# Price Prediction History
# ==========================
class PricePredictionHistory(Base):
    __tablename__ = "price_prediction_history"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer)

    predicted_price = Column(Float)

    confidence_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


# ==========================
# Recommendation History
# ==========================
class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer)

    product_id = Column(Integer)

    score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)