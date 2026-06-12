from app.database.connection import SessionLocal
from app.database.models import (
    User,
    Product,
    Review,
    Cart,
    Wishlist,
    Order,
    UserActivity
)
from app.utils.password import hash_password

db = SessionLocal()


def seed_database():

    # =====================================
    # Users
    # =====================================

    admin = User(
        username="admin",
        email="admin@xecommerce.com",
        password=hash_password("admin123"),
        role="admin"
    )

    seller = User(
        username="seller",
        email="seller@xecommerce.com",
        password=hash_password("seller123"),
        role="seller"
    )

    customer = User(
        username="customer",
        email="customer@xecommerce.com",
        password=hash_password("customer123"),
        role="customer"
    )

    db.add_all([admin, seller, customer])
    db.commit()

    # =====================================
    # Products
    # =====================================

    products = [

        Product(
            name="iPhone 15",
            description="Apple iPhone 15 128GB",
            category="Smartphone",
            brand="Apple",
            price=79999,
            stock=25,
            rating=4.8,
            image_url="iphone15.jpg",
            is_featured=True
        ),

        Product(
            name="Samsung Galaxy S24",
            description="Samsung flagship phone",
            category="Smartphone",
            brand="Samsung",
            price=74999,
            stock=30,
            rating=4.7,
            image_url="s24.jpg",
            is_featured=True
        ),

        Product(
            name="Boat Rockerz 550",
            description="Wireless Headphones",
            category="Headphones",
            brand="Boat",
            price=1999,
            stock=100,
            rating=4.5
        ),

        Product(
            name="Dell Inspiron 15",
            description="Core i7 Laptop",
            category="Laptop",
            brand="Dell",
            price=69999,
            stock=15,
            rating=4.6
        ),

        Product(
            name="Sony Bravia 55",
            description="4K Smart TV",
            category="Television",
            brand="Sony",
            price=59999,
            stock=20,
            rating=4.7
        )

    ]

    db.add_all(products)
    db.commit()

    # =====================================
    # Reviews
    # =====================================

    review1 = Review(
        user_id=3,
        product_id=1,
        rating=5,
        comment="Excellent phone!",
        sentiment="positive",
        is_fake=False
    )

    review2 = Review(
        user_id=3,
        product_id=3,
        rating=4,
        comment="Good sound quality",
        sentiment="positive",
        is_fake=False
    )

    db.add_all([review1, review2])
    db.commit()

    # =====================================
    # Cart
    # =====================================

    cart_item = Cart(
        user_id=3,
        product_id=1,
        quantity=1
    )

    db.add(cart_item)
    db.commit()

    # =====================================
    # Wishlist
    # =====================================

    wishlist_item = Wishlist(
        user_id=3,
        product_id=2
    )

    db.add(wishlist_item)
    db.commit()

    # =====================================
    # Orders
    # =====================================

    order = Order(
        user_id=3,
        total_amount=79999,
        payment_method="UPI",
        shipping_address="Kolkata, India",
        status="Delivered"
    )

    db.add(order)
    db.commit()

    # =====================================
    # User Activity
    # =====================================

    activity1 = UserActivity(
        user_id=3,
        activity_type="view",
        product_id=1
    )

    activity2 = UserActivity(
        user_id=3,
        activity_type="search",
        search_query="iPhone 15"
    )

    db.add_all([activity1, activity2])
    db.commit()

    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()