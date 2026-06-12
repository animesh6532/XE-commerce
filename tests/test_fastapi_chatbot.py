# tests/test_fastapi_chatbot.py

import unittest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend and backend/app directories to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
APP_DIR = BACKEND_DIR / "app"

if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

try:
    from main import app
    MODULES_IMPORTED = True
except ImportError as e:
    print(f"FastAPI app import error: {e}")
    MODULES_IMPORTED = False


class TestFastAPIChatbot(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.client = TestClient(app)

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "FastAPI app failed to import.")
        self.client = self.__class__.client

    def test_health_check(self):
        """Tests health check of the backend application."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "status": "success",
            "message": "Xecommerce AI Backend Running",
            "version": "1.0.0"
        })

    def test_chatbot_query_endpoint(self):
        """Tests standard query route under chatbot API."""
        payload = {
            "query": "Mechanical gaming keyboard under 5000",
            "budget": 5000.0,
            "min_rating": 4.0
        }
        response = self.client.post("/api/chatbot/query", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("response", data)
        self.assertIn("rag_data", data)
        self.assertEqual(data["rag_data"]["routed_dataset"], "Gaming Accessories")

    def test_chatbot_compare_endpoint(self):
        """Tests comparison route under chatbot API."""
        payload = {
            "query": "LG vs Panasonic AC"
        }
        response = self.client.post("/api/chatbot/compare", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["brand_a"], "Lg")
        self.assertEqual(data["brand_b"], "Panasonic")
        self.assertIn("comparison", data)
        self.assertEqual(data["dataset"], "Air Conditioners")

    def test_chatbot_recommend_endpoint(self):
        """Tests recommend discovery route under chatbot API."""
        payload = {
            "query": "wireless earbuds under 3000",
            "top_k": 3
        }
        response = self.client.post("/api/chatbot/recommend", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("response", data)

    def test_chatbot_history_endpoint(self):
        """Tests history route under chatbot API."""
        response = self.client.get("/api/chatbot/history")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("history", data)
        self.assertIsInstance(data["history"], list)

    def test_chatbot_categories_endpoint(self):
        """Tests list of categories route under chatbot API."""
        response = self.client.get("/api/chatbot/categories")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)
        self.assertGreater(len(data["categories"]), 0)


if __name__ == "__main__":
    unittest.main()
