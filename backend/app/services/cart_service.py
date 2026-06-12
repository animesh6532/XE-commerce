from sqlalchemy.orm import Session, joinedload
from app.database.models import Cart, Product, Wishlist
from app.monitoring.logs import app_logger


class CartService:

    # ============================================
    # Add Product To Cart
    # ============================================
    def add_to_cart(
            self,
            db: Session,
            user_id: int,
            product_id: int = None,
            quantity: int = 1,
            cart_data = None
    ):
        if cart_data is not None:
            product_id = cart_data.product_id
            quantity = cart_data.quantity

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            return {
                "success": False,
                "message": "Product not found"
            }

        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

        if cart_item:
            cart_item.quantity += quantity

        else:
            cart_item = Cart(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)

        db.commit()

        app_logger.info(
            f"User {user_id} added product {product_id} to cart"
        )

        return {
            "success": True,
            "message": "Product added to cart"
        }

    # ============================================
    # View Cart (Optimized using joinedload to prevent N+1 queries)
    # ============================================
    def get_cart(
            self,
            db: Session,
            user_id: int
    ):

        cart_items = db.query(Cart).options(
            joinedload(Cart.product)
        ).filter(
            Cart.user_id == user_id
        ).all()

        total = 0

        items = []

        for item in cart_items:

            product = item.product
            if product:
                subtotal = product.price * item.quantity

                total += subtotal

                items.append({
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "quantity": item.quantity,
                    "subtotal": subtotal
                })

        return {
            "items": items,
            "total_price": total
        }

    # ============================================
    # Update Quantity
    # ============================================
    def update_quantity(
            self,
            db: Session,
            user_id: int,
            product_id: int,
            quantity: int
    ):

        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

        if not cart_item:

            return {
                "success": False,
                "message": "Cart item not found"
            }

        cart_item.quantity = quantity

        db.commit()

        return {
            "success": True,
            "message": "Quantity updated"
        }

    # ============================================
    # Remove Item
    # ============================================
    def remove_item(
            self,
            db: Session,
            user_id: int,
            product_id: int
    ):

        cart_item = db.query(Cart).filter(
            Cart.user_id == user_id,
            Cart.product_id == product_id
        ).first()

        if not cart_item:

            return {
                "success": False,
                "message": "Item not found"
            }

        db.delete(cart_item)

        db.commit()

        return {
            "success": True,
            "message": "Item removed"
        }

    # ============================================
    # Clear Cart
    # ============================================
    def clear_cart(
            self,
            db: Session,
            user_id: int
    ):

        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id
        ).all()

        for item in cart_items:
            db.delete(item)

        db.commit()

        return {
            "success": True,
            "message": "Cart cleared"
        }

    # ============================================
    # Cart Count
    # ============================================
    def cart_count(
            self,
            db: Session,
            user_id: int
    ):

        count = db.query(Cart).filter(
            Cart.user_id == user_id
        ).count()

        return {
            "cart_count": count
        }

    # ============================================
    # Apply Coupon
    # ============================================
    def apply_coupon(
            self,
            db: Session,
            user_id: int,
            coupon_code: str,
            total_price: float = None
    ):
        if total_price is None:
            cart = self.get_cart(db, user_id)
            total_price = cart.get("total_price", 0.0)

        discounts = {
            "SAVE10": 10,
            "SAVE20": 20
        }

        if coupon_code not in discounts:

            return {
                "success": False,
                "message": "Invalid coupon"
            }

        discount = discounts[coupon_code]

        final_price = total_price * (
                1 - discount / 100
        )

        return {

            "success": True,

            "discount_percent": discount,

            "final_price": round(
                final_price,
                2
            )
        }

    # ============================================
    # Remove from Cart (Alias/Wrapper)
    # ============================================
    def remove_from_cart(self, db: Session, user_id: int, product_id: int):
        return self.remove_item(db, user_id, product_id)

    # ============================================
    # Save for Later
    # ============================================
    def save_for_later(self, db: Session, user_id: int, product_id: int):
        return self.move_to_wishlist(db, user_id, product_id)

    # ============================================
    # Move to Wishlist
    # ============================================
    def move_to_wishlist(self, db: Session, user_id: int, product_id: int):
        cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).first()
        if cart_item:
            db.delete(cart_item)
        wishlist_item = db.query(Wishlist).filter(Wishlist.user_id == user_id, Wishlist.product_id == product_id).first()
        if not wishlist_item:
            wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
            db.add(wishlist_item)
        db.commit()
        return {
            "success": True,
            "message": "Product moved to wishlist successfully"
        }

    # ============================================
    # Checkout Preview
    # ============================================
    def checkout_preview(self, db: Session, user_id: int):
        cart = self.get_cart(db, user_id)
        subtotal = cart.get("total_price", 0.0)
        shipping = 0.0 if subtotal > 500 else 40.0
        tax = round(subtotal * 0.18, 2)
        total = round(subtotal + shipping + tax, 2)
        return {
            "items": cart.get("items", []),
            "subtotal": subtotal,
            "shipping_weight": 1.5,
            "shipping": shipping,
            "tax": tax,
            "total": total
        }

    # ============================================
    # Wishlist To Cart
    # ============================================
    def wishlist_to_cart(
            self,
            db: Session,
            user_id: int,
            product_id: int
    ):

        wishlist_item = db.query(Wishlist).filter(
            Wishlist.user_id == user_id,
            Wishlist.product_id == product_id
        ).first()

        if not wishlist_item:

            return {
                "success": False,
                "message": "Product not in wishlist"
            }

        self.add_to_cart(
            db,
            user_id,
            product_id,
            1
        )

        db.delete(wishlist_item)

        db.commit()

        return {
            "success": True,
            "message": "Moved from wishlist to cart"
        }

    # ============================================
    # Cart Analytics
    # ============================================
    def cart_summary(
            self,
            db: Session,
            user_id: int
    ):

        cart_items = db.query(Cart).filter(
            Cart.user_id == user_id
        ).all()

        total_items = sum(
            item.quantity
            for item in cart_items
        )

        return {

            "total_unique_products":
                len(cart_items),

            "total_items":
                total_items
        }

    # ============================================
    # Health Check
    # ============================================
    def health(self):

        return {

            "status":
                "healthy",

            "service":
                "cart_service"
        }