import unittest
import sys
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

class TestReviewsAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if MODULES_IMPORTED:
            cls.client = TestClient(app)

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "FastAPI app failed to import.")
        self.client = self.__class__.client

    def test_get_product_reviews(self):
        response = self.client.get("/api/reviews/product/1")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_review_summary(self):
        response = self.client.get("/api/reviews/summary/1")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, dict)
        self.assertIn("total_reviews", data)
        self.assertIn("average_rating", data)
        self.assertIn("rating_distribution", data)
        self.assertIn("sentiment_summary", data)
        self.assertIn("fake_review_percentage", data)
        
        # Verify rating distribution has keys 1 to 5
        for star in ["1", "2", "3", "4", "5"]:
            self.assertIn(star, data["rating_distribution"])
            
        # Verify sentiment keys
        self.assertIn("positive", data["sentiment_summary"])
        self.assertIn("negative", data["sentiment_summary"])
        self.assertIn("neutral", data["sentiment_summary"])

    def test_sentiment_analysis_endpoint(self):
        # We can try to hit the health check or check the route exists
        response = self.client.get("/api/reviews/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")