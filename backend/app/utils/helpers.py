"""
====================================================
Xecommerce Helper Functions
====================================================
"""

from datetime import datetime
from typing import List


# =====================================================
# Success Response
# =====================================================

def success_response(
        message: str,
        data=None
):

    return {

        "success": True,

        "message": message,

        "data": data
    }


# =====================================================
# Error Response
# =====================================================

def error_response(
        message: str
):

    return {

        "success": False,

        "message": message
    }


# =====================================================
# Pagination
# =====================================================

def paginate(
        items: List,
        page: int = 1,
        limit: int = 20
):

    start = (page - 1) * limit

    end = start + limit

    return {

        "page": page,

        "limit": limit,

        "total": len(items),

        "results": items[start:end]
    }


# =====================================================
# Calculate Discount Percentage
# =====================================================

def calculate_discount_percentage(
        original_price: float,
        discounted_price: float
):

    if original_price == 0:
        return 0

    discount = (
        (original_price - discounted_price)
        / original_price
    ) * 100

    return round(discount, 2)


# =====================================================
# Calculate Cart Total
# =====================================================

def calculate_cart_total(
        cart_items
):

    total = 0

    for item in cart_items:

        total += (
            item.product.price *
            item.quantity
        )

    return round(total, 2)


# =====================================================
# Average Rating
# =====================================================

def average_rating(
        ratings
):

    if len(ratings) == 0:
        return 0

    return round(
        sum(ratings) / len(ratings),
        2
    )


# =====================================================
# AI Deal Score
# =====================================================

def calculate_deal_score(
        rating: float,
        stock: int,
        price: float
):

    score = 100

    if rating < 4:
        score -= 20

    if stock < 10:
        score -= 10

    if price > 100000:
        score -= 5

    return max(score, 0)


# =====================================================
# Format Currency
# =====================================================

def format_price(
        amount: float
):

    return f"₹{amount:,.2f}"


# =====================================================
# Generate Order Number
# =====================================================

def generate_order_number():

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    return f"ORD-{timestamp}"


# =====================================================
# Generate Invoice Number
# =====================================================

def generate_invoice_number():

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    return f"INV-{timestamp}"


# =====================================================
# Price Drop Percentage
# =====================================================

def price_drop_percentage(
        old_price: float,
        new_price: float
):

    if old_price == 0:
        return 0

    drop = (
        (old_price - new_price)
        / old_price
    ) * 100

    return round(drop, 2)


# =====================================================
# Normalize Search Query
# =====================================================

def normalize_query(
        query: str
):

    return query.strip().lower()


# =====================================================
# Validate Rating
# =====================================================

def validate_rating(
        rating: float
):

    return 0 <= rating <= 5


# =====================================================
# Low Stock Check
# =====================================================

def is_low_stock(
        stock: int
):

    return stock < 10


# =====================================================
# Health Response
# =====================================================

def health_response(
        service_name: str
):

    return {

        "status": "healthy",

        "service": service_name
    }


# =====================================================
# Model Retraining Check
# =====================================================

def retraining_required(
        drift_count: int
):

    return drift_count > 1


# =====================================================
# Timestamp
# =====================================================

def current_timestamp():

    return datetime.utcnow()


# =====================================================
# Build Recommendation Response
# =====================================================

def recommendation_response(
        products
):

    return {

        "count": len(products),

        "products": products
    }


# =====================================================
# Build Analytics Response
# =====================================================

def analytics_response(
        metrics: dict
):

    return {

        "generated_at": current_timestamp(),

        "metrics": metrics
    }


# =====================================================
# Build Chat Response
# =====================================================

def chatbot_response(
        response: str,
        source: str = "template"
):

    return {

        "response": response,

        "source": source
    }


# =====================================================
# Health Check All Services
# =====================================================

def overall_health():

    return {

        "status": "healthy",

        "project": "Xecommerce",

        "version": "1.0.0"
    }