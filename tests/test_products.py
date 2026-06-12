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
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_search_products(self):
        response = self.client.get("/api/products/search/?query=keyboard")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_featured_products(self):
        response = self.client.get("/api/products/featured/list")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_invalid_product_id(self):
        response = self.client.get("/api/products/999999")
        self.assertEqual(response.status_code, 404)