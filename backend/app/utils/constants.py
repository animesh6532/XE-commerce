"""
=========================================================
Xecommerce Constants
=========================================================
"""

# =====================================================
# USER ROLES
# =====================================================

ADMIN_ROLE = "admin"
SELLER_ROLE = "seller"
CUSTOMER_ROLE = "customer"


# =====================================================
# ORDER STATUS
# =====================================================

ORDER_PENDING = "Pending"
ORDER_PROCESSING = "Processing"
ORDER_SHIPPED = "Shipped"
ORDER_DELIVERED = "Delivered"
ORDER_CANCELLED = "Cancelled"
ORDER_RETURNED = "Returned"


# =====================================================
# PAYMENT METHODS
# =====================================================

PAYMENT_COD = "Cash On Delivery"
PAYMENT_UPI = "UPI"
PAYMENT_CARD = "Card"
PAYMENT_NET_BANKING = "Net Banking"


# =====================================================
# SENTIMENT LABELS
# =====================================================

POSITIVE_SENTIMENT = "positive"
NEGATIVE_SENTIMENT = "negative"
NEUTRAL_SENTIMENT = "neutral"


# =====================================================
# USER ACTIVITY TYPES
# =====================================================

ACTIVITY_VIEW = "view"
ACTIVITY_CLICK = "click"
ACTIVITY_SEARCH = "search"
ACTIVITY_CART = "cart"
ACTIVITY_WISHLIST = "wishlist"
ACTIVITY_PURCHASE = "purchase"


# =====================================================
# CHATBOT SOURCES
# =====================================================

CHATBOT_TEMPLATE = "template"
CHATBOT_OLLAMA = "ollama"
CHATBOT_OPENAI = "openai"


# =====================================================
# MODEL STATUS
# =====================================================

MODEL_NORMAL = "NORMAL"
MODEL_RETRAIN_REQUIRED = "RETRAIN_REQUIRED"


# =====================================================
# REVIEW STATUS
# =====================================================

REAL_REVIEW = False
FAKE_REVIEW = True


# =====================================================
# PRODUCT STOCK
# =====================================================

LOW_STOCK_THRESHOLD = 10
CRITICAL_STOCK_THRESHOLD = 5


# =====================================================
# RECOMMENDATION
# =====================================================

DEFAULT_TOP_K = 10
DEFAULT_SIMILAR_PRODUCTS = 5


# =====================================================
# SEARCH
# =====================================================

DEFAULT_SEARCH_LIMIT = 20


# =====================================================
# PAGINATION
# =====================================================

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 20


# =====================================================
# JWT SETTINGS
# =====================================================

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"


# =====================================================
# RATE LIMITING
# =====================================================

MAX_REQUESTS = 100
WINDOW_SECONDS = 60


# =====================================================
# COUPON CODES
# =====================================================

COUPONS = {
    "SAVE10": 10,
    "SAVE20": 20,
    "SAVE30": 30
}


# =====================================================
# NOTIFICATION TYPES
# =====================================================

EMAIL_NOTIFICATION = "email"
SMS_NOTIFICATION = "sms"
PUSH_NOTIFICATION = "push"


# =====================================================
# FILE PATHS
# =====================================================

RECOMMENDER_MODEL_PATH = (
    "ml_models/saved_models/recommender.pkl"
)

SENTIMENT_MODEL_PATH = (
    "ml_models/saved_models/sentiment.pkl"
)

FAKE_REVIEW_MODEL_PATH = (
    "ml_models/saved_models/fake_review.pkl"
)

PRICE_MODEL_PATH = (
    "ml_models/saved_models/price_predictor.pkl"
)

DEMAND_MODEL_PATH = (
    "ml_models/saved_models/demand_forecast.pkl"
)

CHATBOT_INDEX_PATH = (
    "ml_models/saved_models/chatbot_index.pkl"
)


# =====================================================
# LOG FILES
# =====================================================

APP_LOG = "logs/app.log"
ERROR_LOG = "logs/error.log"
ACTIVITY_LOG = "logs/activity.log"
CHATBOT_LOG = "logs/chatbot.log"
SEARCH_LOG = "logs/search.log"
MODEL_METRICS_LOG = "logs/model_metrics.log"
DRIFT_LOG = "logs/drift_detection.log"


# =====================================================
# HEALTH STATUS
# =====================================================

HEALTHY = "healthy"
UNHEALTHY = "unhealthy"


# =====================================================
# API PREFIXES
# =====================================================

AUTH_API = "/api/auth"
PRODUCT_API = "/api/products"
CART_API = "/api/cart"
ORDER_API = "/api/orders"
REVIEW_API = "/api/reviews"
WISHLIST_API = "/api/wishlist"
RECOMMENDATION_API = "/api/recommendations"
CHATBOT_API = "/api/chatbot"
ANALYTICS_API = "/api/analytics"
SEARCH_API = "/api/search"
VOICE_SEARCH_API = "/api/voice-search"
IMAGE_SEARCH_API = "/api/image-search"
PRICE_PREDICTION_API = "/api/price-prediction"
USER_ACTIVITY_API = "/api/user-activity"


# =====================================================
# AI FEATURES
# =====================================================

AI_DEAL_SCORE = "AI Deal Score"
FAKE_REVIEW_DETECTION = "Fake Review Detection"
PRICE_PREDICTION_ENGINE = "Price Prediction Engine"
SMART_WISHLIST = "Smart Wishlist"
BUDGET_PLANNER = "Budget Planner"
AI_PRODUCT_COMPARISON = "AI Product Comparison"
AI_SHOPPING_ASSISTANT = "AI Shopping Assistant"
PERSONALIZED_DEAL_FEED = "Personalized Deal Feed"
PRICE_ALERTS = "Price Alerts"
BEST_DEAL_FINDER = "Best Deal Finder"