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


class TestCartAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.client = TestClient(app)

            # Ensure at least one product exists in the DB
            db = SessionLocal()
            product = db.query(Product).first()
            if not product:
                product = Product(
                    name="Test Product for Cart",
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
        self.test_email = f"cart_test_{uuid.uuid4().hex[:8]}@example.com"
        self.test_username = f"cart_user_{uuid.uuid4().hex[:8]}"
        self.test_password = "cartpassword123"

        reg_payload = {
            "username": self.test_username,
            "email": self.test_email,
            "password": self.test_password
        }
        self.client.post("/api/auth/register", json=reg_payload)

        # Login to get token
        login_response = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.test_password
        })
        self.assertEqual(login_response.status_code, 200)
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_cart_operations(self):
        # 1. Get initial cart (should be empty)
        response = self.client.get("/api/cart/", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_price"], 0)
        self.assertEqual(len(data["items"]), 0)

        # 2. Add product to cart
        add_payload = {
            "product_id": self.product_id,
            "quantity": 2
        }
        response = self.client.post("/api/cart/add", json=add_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        # 3. View cart again
        response = self.client.get("/api/cart/", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["total_price"], 0)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["product_id"], self.product_id)
        self.assertEqual(data["items"][0]["quantity"], 2)

        # 4. Update quantity
        update_payload = {
            "quantity": 5
        }
        response = self.client.put(f"/api/cart/update/{self.product_id}", json=update_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        # 5. Apply coupon
        coupon_payload = {
            "code": "SAVE10"
        }
        response = self.client.post("/api/cart/apply-coupon", json=coupon_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["discount_percent"], 10)

        # 6. Checkout preview
        response = self.client.get("/api/cart/checkout-preview", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("subtotal", response.json())
        self.assertIn("total", response.json())

        # 7. Delete item
        response = self.client.delete(f"/api/cart/remove/{self.product_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])

        # 8. Clear cart
        response = self.client.delete("/api/cart/clear", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])