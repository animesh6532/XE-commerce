import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# =====================================================
# Create Logs Directory
# =====================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# =====================================================
# Log Format
# =====================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


# =====================================================
# Main Application Logger
# =====================================================

app_logger = logging.getLogger("xecommerce")

app_logger.setLevel(logging.INFO)

app_handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)

app_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

app_logger.addHandler(app_handler)


# =====================================================
# Error Logger
# =====================================================

error_logger = logging.getLogger("errors")

error_logger.setLevel(logging.ERROR)

error_handler = RotatingFileHandler(
    LOG_DIR / "error.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)

error_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

error_logger.addHandler(error_handler)


# =====================================================
# User Activity Logger
# =====================================================

activity_logger = logging.getLogger("user_activity")

activity_logger.setLevel(logging.INFO)

activity_handler = RotatingFileHandler(
    LOG_DIR / "activity.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

activity_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

activity_logger.addHandler(activity_handler)


# =====================================================
# Search Logger
# =====================================================

search_logger = logging.getLogger("search")

search_logger.setLevel(logging.INFO)

search_handler = RotatingFileHandler(
    LOG_DIR / "search.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

search_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

search_logger.addHandler(search_handler)


# =====================================================
# Recommendation Logger
# =====================================================

recommendation_logger = logging.getLogger(
    "recommendation"
)

recommendation_logger.setLevel(
    logging.INFO
)

recommendation_handler = RotatingFileHandler(
    LOG_DIR / "recommendation.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

recommendation_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

recommendation_logger.addHandler(
    recommendation_handler
)


# =====================================================
# Chatbot Logger
# =====================================================

chatbot_logger = logging.getLogger(
    "chatbot"
)

chatbot_logger.setLevel(
    logging.INFO
)

chatbot_handler = RotatingFileHandler(
    LOG_DIR / "chatbot.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

chatbot_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

chatbot_logger.addHandler(
    chatbot_handler
)


# =====================================================
# Price Prediction Logger
# =====================================================

price_logger = logging.getLogger(
    "price_prediction"
)

price_logger.setLevel(
    logging.INFO
)

price_handler = RotatingFileHandler(
    LOG_DIR / "price_prediction.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

price_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

price_logger.addHandler(
    price_handler
)


# =====================================================
# Model Metrics Logger
# =====================================================

model_logger = logging.getLogger(
    "model_metrics"
)

model_logger.setLevel(
    logging.INFO
)

model_handler = RotatingFileHandler(
    LOG_DIR / "model_metrics.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

model_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

model_logger.addHandler(
    model_handler
)


# =====================================================
# Drift Detection Logger
# =====================================================

drift_logger = logging.getLogger(
    "drift_detection"
)

drift_logger.setLevel(
    logging.INFO
)

drift_handler = RotatingFileHandler(
    LOG_DIR / "drift_detection.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

drift_handler.setFormatter(
    logging.Formatter(LOG_FORMAT)
)

drift_logger.addHandler(
    drift_handler
)