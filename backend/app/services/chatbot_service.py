from datetime import datetime
from sqlalchemy.orm import Session

from app.database.models import (
    ChatHistory,
    User,
    Product,
    Order
)

from app.monitoring.logs import (
    chatbot_logger,
    error_logger
)

from app.notifications.push_service import PushService


class ChatbotService:

    def __init__(self):

        self.push_service = PushService()

    # =====================================================
    # Save Chat
    # =====================================================

    def save_chat(
            self,
            db: Session,
            user_id: int,
            query: str,
            response: str,
            source: str = "template"
    ):

        chat = ChatHistory(
            user_id=user_id,
            query=query,
            response=response,
            source=source,
            created_at=datetime.utcnow()
        )

        db.add(chat)
        db.commit()

        chatbot_logger.info(
            f"Chat saved for user {user_id}"
        )

        return chat

    # =====================================================
    # Get Chat History
    # =====================================================

    def get_chat_history(
            self,
            db: Session,
            user_id: int
    ):

        chats = db.query(
            ChatHistory
        ).filter(
            ChatHistory.user_id == user_id
        ).order_by(
            ChatHistory.created_at.desc()
        ).all()

        return chats

    # =====================================================
    # Product Recommendation Query
    # =====================================================

    def recommend_products(
            self,
            db: Session,
            category: str = None,
            limit: int = 5
    ):

        query = db.query(Product)

        if category:
            query = query.filter(
                Product.category == category
            )

        products = query.limit(limit).all()

        return products

    # =====================================================
    # Compare Products
    # =====================================================

    def compare_products(
            self,
            db: Session,
            product1_id: int,
            product2_id: int
    ):

        p1 = db.query(Product).filter(
            Product.id == product1_id
        ).first()

        p2 = db.query(Product).filter(
            Product.id == product2_id
        ).first()

        if not p1 or not p2:

            return {
                "success": False,
                "message": "Product not found"
            }

        return {

            "product_1": {
                "name": p1.name,
                "price": p1.price,
                "rating": p1.rating
            },

            "product_2": {
                "name": p2.name,
                "price": p2.price,
                "rating": p2.rating
            }
        }

    # =====================================================
    # Order Status Query
    # =====================================================

    def order_status(
            self,
            db: Session,
            order_id: int
    ):

        order = db.query(Order).filter(
            Order.id == order_id
        ).first()

        if not order:

            return {
                "success": False,
                "message": "Order not found"
            }

        return {

            "order_id": order.id,

            "status": order.status,

            "amount": order.total_amount
        }

    # =====================================================
    # Price Query
    # =====================================================

    def product_price(
            self,
            db: Session,
            product_id: int
    ):

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:

            return {
                "success": False,
                "message": "Product not found"
            }

        return {

            "name": product.name,

            "price": product.price
        }

    # =====================================================
    # Personalized Suggestions
    # =====================================================

    def personalized_suggestions(
            self,
            db: Session,
            user_id: int
    ):

        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:

            return []

        products = db.query(Product).limit(5).all()

        return products

    # =====================================================
    # Send Recommendation Notification
    # =====================================================

    def notify_user(
            self,
            user_id: int,
            product_name: str
    ):

        return self.push_service.recommendation_notification(
            user_id,
            product_name
        )

    # =====================================================
    # Generate Response
    # =====================================================

    def generate_response(
            self,
            query: str
    ):

        query = query.lower()

        if "hello" in query:

            return {
                "response":
                    "Hello! Welcome to Xecommerce AI Assistant."
            }

        elif "recommend" in query:

            return {
                "response":
                    "I can recommend products based on your interests."
            }

        elif "price" in query:

            return {
                "response":
                    "Please specify the product name."
            }

        else:

            return {
                "response":
                    "Sorry, I didn't understand your query."
            }

    # =====================================================
    # Health Check
    # =====================================================

    def health(self):

        return {

            "status": "healthy",

            "service": "chatbot_service"
        }