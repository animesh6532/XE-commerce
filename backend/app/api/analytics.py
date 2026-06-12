from fastapi import APIRouter
from app.services.analytics_service import AnalyticsService

router = APIRouter()

analytics_service = AnalyticsService()


# ---------------- Dashboard Overview ----------------
@router.get("/dashboard")
def dashboard_overview():
    return analytics_service.dashboard_overview()


# ---------------- Sales Analytics ----------------
@router.get("/sales")
def sales_analytics():
    return analytics_service.sales_analytics()


# ---------------- Revenue Analytics ----------------
@router.get("/revenue")
def revenue_analytics():
    return analytics_service.revenue_analytics()


# ---------------- Monthly Sales ----------------
@router.get("/monthly-sales")
def monthly_sales():
    return analytics_service.monthly_sales()


# ---------------- Top Selling Products ----------------
@router.get("/top-products")
def top_products(limit: int = 10):
    return analytics_service.top_products(limit)


# ---------------- Category Analytics ----------------
@router.get("/categories")
def category_analytics():
    return analytics_service.category_analytics()


# ---------------- User Analytics ----------------
@router.get("/users")
def user_analytics():
    return analytics_service.user_analytics()


# ---------------- Customer Activity ----------------
@router.get("/customer-activity")
def customer_activity():
    return analytics_service.customer_activity()


# ---------------- Order Analytics ----------------
@router.get("/orders")
def order_analytics():
    return analytics_service.order_analytics()


# ---------------- Review Analytics ----------------
@router.get("/reviews")
def review_analytics():
    return analytics_service.review_analytics()


# ---------------- Sentiment Analysis Statistics ----------------
@router.get("/sentiment")
def sentiment_statistics():
    return analytics_service.sentiment_statistics()


# ---------------- Fake Review Statistics ----------------
@router.get("/fake-reviews")
def fake_review_statistics():
    return analytics_service.fake_review_statistics()


# ---------------- Recommendation Analytics ----------------
@router.get("/recommendations")
def recommendation_analytics():
    return analytics_service.recommendation_analytics()


# ---------------- AI Model Metrics ----------------
@router.get("/model-performance")
def model_performance():
    return analytics_service.model_performance()


# ---------------- Inventory Analytics ----------------
@router.get("/inventory")
def inventory_analytics():
    return analytics_service.inventory_analytics()


# ---------------- Demand Forecast Analytics ----------------
@router.get("/demand-forecast")
def demand_forecast():
    return analytics_service.demand_forecast()


# ---------------- Price Prediction Analytics ----------------
@router.get("/price-prediction")
def price_prediction():
    return analytics_service.price_prediction()


# ---------------- Complete Report ----------------
@router.get("/report")
def complete_report():
    return analytics_service.complete_report()