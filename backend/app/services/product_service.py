from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.models import Product

from app.monitoring.logs import (
    app_logger,
    error_logger
)

from app.notifications.push_service import PushService


class ProductService:

    def __init__(self):

        self.push_service = PushService()

    # ==========================================
    # Create Product
    # ==========================================
    def create_product(
            self,
            db: Session,
<<<<<<< HEAD
            product_data = None,
            product = None,
            user = None
    ):
        data = product or product_data
        db_product = Product(
            name=data.name,
            description=data.description,
            category=data.category,
            brand=data.brand,
            price=data.price,
            stock=data.stock,
            image_url=data.image_url
        )

        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        app_logger.info(
            f"Product created: {db_product.name}"
        )

        return db_product
=======
            product_data
    ):

        product = Product(
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            brand=product_data.brand,
            price=product_data.price,
            stock=product_data.stock,
            image_url=product_data.image_url
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        app_logger.info(
            f"Product created: {product.name}"
        )

        return product
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a

    # ==========================================
    # Get Product By ID
    # ==========================================
    def get_product(
            self,
            db: Session,
            product_id: int
    ):

        return db.query(Product).filter(
            Product.id == product_id
        ).first()

    # ==========================================
    # Get All Products
    # ==========================================
    def get_all_products(
            self,
            db: Session
    ):

        return db.query(Product).all()

    # ==========================================
    # Update Product
    # ==========================================
    def update_product(
            self,
            db: Session,
            product_id: int,
<<<<<<< HEAD
            data = None,
            product = None,
            user = None
    ):
        update_data = product or data
        db_product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not db_product:
=======
            data
    ):

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a

            return {
                "success": False,
                "message": "Product not found"
            }

<<<<<<< HEAD
        for key, value in update_data.dict(
                exclude_unset=True
        ).items():

            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)

        app_logger.info(
            f"Product updated: {db_product.id}"
        )

        return db_product
=======
        for key, value in data.dict(
                exclude_unset=True
        ).items():

            setattr(product, key, value)

        db.commit()
        db.refresh(product)

        app_logger.info(
            f"Product updated: {product.id}"
        )

        return product
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a

    # ==========================================
    # Delete Product
    # ==========================================
    def delete_product(
            self,
            db: Session,
<<<<<<< HEAD
            product_id: int,
            user = None
    ):

        db_product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not db_product:
=======
            product_id: int
    ):

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a

            return {
                "success": False,
                "message": "Product not found"
            }

<<<<<<< HEAD
        db.delete(db_product)
=======
        db.delete(product)
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a
        db.commit()

        app_logger.info(
            f"Product deleted: {product_id}"
        )

        return {
            "success": True,
            "message": "Product deleted"
        }

    # ==========================================
    # Search Products
    # ==========================================
    def search_products(
            self,
            db: Session,
<<<<<<< HEAD
            keyword: str = None,
            query: str = None
    ):
        term = query or keyword or ""
        return db.query(Product).filter(

            or_(
                Product.name.ilike(f"%{term}%"),
                Product.brand.ilike(f"%{term}%"),
                Product.category.ilike(f"%{term}%")
=======
            keyword: str
    ):

        return db.query(Product).filter(

            or_(
                Product.name.ilike(f"%{keyword}%"),
                Product.brand.ilike(f"%{keyword}%"),
                Product.category.ilike(f"%{keyword}%")
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a
            )

        ).all()

    # ==========================================
    # Products By Category
    # ==========================================
    def get_by_category(
            self,
            db: Session,
            category: str
    ):

        return db.query(Product).filter(
            Product.category == category
        ).all()

    # ==========================================
    # Products By Brand
    # ==========================================
    def get_by_brand(
            self,
            db: Session,
            brand: str
    ):

        return db.query(Product).filter(
            Product.brand == brand
        ).all()

    # ==========================================
    # Featured Products
    # ==========================================
    def featured_products(
            self,
            db: Session
    ):

        return db.query(Product).filter(
            Product.is_featured == True
        ).all()

    # ==========================================
    # Update Stock
    # ==========================================
    def update_stock(
            self,
            db: Session,
            product_id: int,
            quantity: int
    ):

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:

            return {
                "success": False
            }

        product.stock = quantity

        db.commit()

        if quantity < 5:

            self.push_service.admin_alert(
                f"Low stock alert for {product.name}"
            )

        return {
            "success": True
        }

    # ==========================================
    # Update Price
    # ==========================================
    def update_price(
            self,
            db: Session,
            product_id: int,
            new_price: float
    ):

        product = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:

            return {
                "success": False
            }

        product.price = new_price

        db.commit()

        return {
            "success": True
        }

    # ==========================================
    # Product Analytics
    # ==========================================
    def analytics(
            self,
            db: Session
    ):

        total_products = db.query(
            Product
        ).count()

        featured_products = db.query(
            Product
        ).filter(
            Product.is_featured == True
        ).count()

        low_stock_products = db.query(
            Product
        ).filter(
            Product.stock < 10
        ).count()

        return {

            "total_products":
                total_products,

            "featured_products":
                featured_products,

            "low_stock_products":
                low_stock_products
        }

    # ==========================================
    # Top Rated Products
    # ==========================================
    def top_rated_products(
            self,
            db: Session,
            limit=10
    ):

        return db.query(Product).order_by(
            Product.rating.desc()
        ).limit(limit).all()

    # ==========================================
    # Price Range Filter
    # ==========================================
    def price_range(
            self,
            db: Session,
            min_price: float,
            max_price: float
    ):

        return db.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ).all()

    # ==========================================
<<<<<<< HEAD
    # Get Products (Paginated)
    # ==========================================
    def get_products(self, db: Session, page: int = 1, limit: int = 20):
        offset = (page - 1) * limit
        return db.query(Product).offset(offset).limit(limit).all()

    # ==========================================
    # Get Product By ID (with 404 validation)
    # ==========================================
    def get_product_by_id(self, db: Session, product_id: int):
        product = self.get_product(db, product_id)
        if not product:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    # ==========================================
    # Filter Products
    # ==========================================
    def filter_products(
        self,
        db: Session,
        category: str = None,
        min_price: float = None,
        max_price: float = None,
        min_rating: float = None,
        brand: str = None
    ):
        query = db.query(Product)
        if category:
            query = query.filter(Product.category == category)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if min_rating is not None:
            query = query.filter(Product.rating >= min_rating)
        if brand:
            query = query.filter(Product.brand == brand)
        return query.all()

    # ==========================================
    # Category Products
    # ==========================================
    def category_products(self, db: Session, category_name: str):
        return self.get_by_category(db, category_name)

    # ==========================================
    # Trending Products
    # ==========================================
    def trending_products(self, db: Session):
        return db.query(Product).order_by(Product.rating.desc()).limit(10).all()

    # ==========================================
    # Deal Products
    # ==========================================
    def deal_products(self, db: Session):
        return db.query(Product).filter(Product.is_featured == True).all()

    # ==========================================
    # Similar Products
    # ==========================================
    def similar_products(self, db: Session, product_id: int):
        product = self.get_product(db, product_id)
        if not product:
            return []
        return db.query(Product).filter(
            Product.category == product.category,
            Product.id != product_id
        ).limit(5).all()

    # ==========================================
    # Product Statistics
    # ==========================================
    def product_statistics(self, db: Session):
        return self.analytics(db)

    # ==========================================
    # Inventory Status
    # ==========================================
    def inventory_status(self, db: Session):
        low_stock = db.query(Product).filter(Product.stock < 10).all()
        return {
            "low_stock_count": len(low_stock),
            "low_stock_items": [{"id": p.id, "name": p.name, "stock": p.stock} for p in low_stock]
        }

    # ==========================================
=======
>>>>>>> 26211b0cb847c49c214e53509294b37fff238a9a
    # Health Check
    # ==========================================
    def health(self):

        return {

            "status":
                "healthy",

            "service":
                "product_service"
        }