import unittest
import sys
import uuid
from pathlib import Path
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
APP_DIR = BACKEND_DIR / "app"

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

try:
    from main import app
    from app.database.connection import SessionLocal
    from app.database.models import Product
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


class TestOrdersAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.client = TestClient(app)

            # Ensure at least one product exists in the DB
            db = SessionLocal()
            product = db.query(Product).first()
            if not product:
                product = Product(
                    name="Test Product for Order",
                    description="Test description",
                    category="Electronics",
                    brand="TestBrand",
                    price=4999.0,
                    stock=50,
                    rating=4.5,
                    is_featured=True
                )
                db.add(product)
                db.commit()
                db.refresh(product)
            cls.product_id = product.id
            db.close()

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "FastAPI app failed to import.")
        self.client = self.__class__.client
        self.product_id = self.__class__.product_id

        # Register a test user for auth headers
        self.test_email = f"order_test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_username = f"order_user_{uuid.uuid4().hex[:8]}"
        self.test_password = "orderpassword123"

        self.client.post("/api/auth/register", json={
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        })

        # Login to get token
        login_response = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_response.status_code, 200)
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_order_workflow(self):
        # 1. Add item to cart first (orders require items in cart to check out)
        add_payload = {
            "product_id": self.product_id,
            "quantity": 1
        }
        self.client.post("/api/cart/add", json=add_payload, headers=self.headers)

        # 2. Place order
        order_payload = {
            "shipping_address": "123 Test Street",
            "payment_method": "Credit Card"
        }
        response = self.client.post("/api/orders/place", json=order_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("order_id", data)
        order_id = data["order_id"]

        # 3. Get order tracking
        tracking_response = self.client.get(f"/api/orders/track/{order_id}", headers=self.headers)
        self.assertEqual(tracking_response.status_code, 200)
        self.assertEqual(tracking_response.json()["order_id"], order_id)

        # 4. Get order history
        history_response = self.client.get("/api/orders/", headers=self.headers)
        self.assertEqual(history_response.status_code, 200)
        self.assertIsInstance(history_response.json(), list)

        # 5. Cancel order
        cancel_response = self.client.put(f"/api/orders/cancel/{order_id}", headers=self.headers)
        self.assertEqual(cancel_response.status_code, 200)
        self.assertTrue(cancel_response.json()["success"])