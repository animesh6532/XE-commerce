import unittest
import sys
import pandas as pd
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
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


def test_products_dataset():
    dataset = (
        Path(__file__)
        .resolve()
        .parent.parent
        / "ml_models"
        / "datasets"
        / "products.csv"
    )
    df = pd.read_csv(dataset)
    assert len(df) > 0


class TestProductsAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.client = TestClient(app)

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "FastAPI app failed to import.")
        self.client = self.__class__.client

    def test_get_products_list(self):
        response = self.client.get("/api/products/?page=1&limit=20")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("products", data)
        self.assertIn("total", data)
        self.assertIn("page", data)
        self.assertIn("limit", data)
        self.assertIsInstance(data["products"], list)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["limit"], 20)

    def test_search_products(self):
        response = self.client.get("/api/products/search/?query=keyboard")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_keyword_search_endpoint(self):
        response = self.client.post("/api/search/", json={"query": "keyboard", "page": 1, "limit": 10})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("results", data)
        self.assertIn("total", data)
        self.assertIsInstance(data["results"], list)

    def test_semantic_search_endpoint(self):
        response = self.client.post("/api/search/semantic", json={"query": "headphones", "top_k": 5})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_ai_rag_search_endpoint(self):
        response = self.client.post("/api/search/ai", json={"query": "cable", "top_k": 5})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_filter_products_api(self):
        response = self.client.get("/api/products/filter/?category=Audio&min_price=100&max_price=10000")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_featured_products(self):
        response = self.client.get("/api/products/featured/list")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_invalid_product_id(self):
        response = self.client.get("/api/products/999999")
        self.assertEqual(response.status_code, 404)