from sqlalchemy.orm import Session
from app.database.models import Wishlist, Product, Cart
from app.monitoring.logs import app_logger

class WishlistService:

    # ==========================================
    # Add Product To Wishlist
    # ==========================================
    def add_to_wishlist(self, db: Session, user_id: int, product_id: int):
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {
                "success": False,
                "message": "Product not found"
            }

        wishlist_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

        if wishlist_item:
            return {
                "success": True,
                "message": "Product already in wishlist"
            }

        new_item = Wishlist(user_id=user_id, product_id=product_id)
        db.add(new_item)
        db.commit()

        app_logger.info(f"User {user_id} added product {product_id} to wishlist")

        return {
            "success": True,
            "message": "Product added to wishlist"
        }

    # ==========================================
    # Remove Product From Wishlist
    # ==========================================
    def remove_from_wishlist(self, db: Session, user_id: int, product_id: int):
        wishlist_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

        if not wishlist_item:
            return {
                "success": False,
                "message": "Product not found in wishlist"
            }

        db.delete(wishlist_item)
        db.commit()

        app_logger.info(f"User {user_id} removed product {product_id} from wishlist")

        return {
            "success": True,
            "message": "Product removed from wishlist"
        }

    # ==========================================
    # Get Wishlist
    # ==========================================
    def get_wishlist(self, db: Session, user_id: int):
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
        items = []

        for item in wishlist_items:
            p = item.product
            if p:
                items.append({
                    "product_id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "category": p.category,
                    "brand": p.brand,
                    "stock": p.stock,
                    "rating": p.rating,
                    "image_url": p.image_url
                })

        return {"items": items}

    # ==========================================
    # Clear Wishlist
    # ==========================================
    def clear_wishlist(self, db: Session, user_id: int):
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
        for item in wishlist_items:
            db.delete(item)
        db.commit()

        app_logger.info(f"User {user_id} cleared wishlist")

        return {
            "success": True,
            "message": "Wishlist cleared"
        }

    # ==========================================
    # Move To Cart
    # ==========================================
    def move_to_cart(self, db: Session, user_id: int, product_id: int):
        wishlist_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

        if not wishlist_item:
            return {
                "success": False,
                "message": "Product not in wishlist"
            }

        # Check if already in cart
        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

        if cart_item:
            cart_item.quantity += 1
        else:
            cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
            db.add(cart_item)

        db.delete(wishlist_item)
        db.commit()

        app_logger.info(f"User {user_id} moved product {product_id} from wishlist to cart")

        return {
            "success": True,
            "message": "Moved from wishlist to cart"
        }

    # ==========================================
    # Save For Later
    # ==========================================
    def save_for_later(self, db: Session, user_id: int, product_id: int):
        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

        if cart_item:
            db.delete(cart_item)

        wishlist_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

        if not wishlist_item:
            wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
            db.add(wishlist_item)

        db.commit()

        app_logger.info(f"User {user_id} saved product {product_id} for later")

        return {
            "success": True,
            "message": "Product saved for later"
        }

    # ==========================================
    # AI Deal Tracking
    # ==========================================
    def deal_tracking(self, db: Session, user_id: int):
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
        deals = []

        for item in wishlist_items:
            p = item.product
            if p:
                discount_percent = 15 if p.is_featured else 5
                original_price = round(p.price * (1 + discount_percent / 100.0), 2)
                deals.append({
                    "product_id": p.id,
                    "name": p.name,
                    "current_price": p.price,
                    "original_price": original_price,
                    "discount_percent": discount_percent,
                    "message": f"Price dropped by {discount_percent}%!"
                })

        return {"deals": deals}

    # ==========================================
    # Price Drop Alerts
    # ==========================================
    def price_alerts(self, db: Session, user_id: int):
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
        alerts = []

        for item in wishlist_items:
            p = item.product
            if p and p.is_featured:
                alerts.append({
                    "product_id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "alert_type": "PRICE_DROP",
                    "message": f"Price drop alert: {p.name} is now available at {p.price}!"
                })

        return {"alerts": alerts}

    # ==========================================
    # Wishlist Recommendations
    # ==========================================
    def wishlist_recommendations(self, db: Session, user_id: int):
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
        wishlist_product_ids = {item.product_id for item in wishlist_items}
        categories = {item.product.category for item in wishlist_items if item.product and item.product.category}

        recommendations = []
        if categories:
            recommended_products = db.query(Product).filter(
                Product.category.in_(categories),
                ~Product.id.in_(wishlist_product_ids)
            ).limit(5).all()
            for p in recommended_products:
                recommendations.append({
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "category": p.category,
                    "rating": p.rating,
                    "image_url": p.image_url
                })

        return {"recommendations": recommendations}

    # ==========================================
    # Wishlist Analytics
    # ==========================================
    def wishlist_analytics(self, db: Session, user_id: int):
        wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
        total_items = len(wishlist_items)
        total_value = sum(item.product.price for item in wishlist_items if item.product)
        avg_rating = 0.0

        if total_items > 0:
            ratings = [item.product.rating for item in wishlist_items if item.product and item.product.rating]
            if ratings:
                avg_rating = round(sum(ratings) / len(ratings), 2)

        return {
            "total_items": total_items,
            "total_value": round(total_value, 2),
            "average_rating": avg_rating
        }
