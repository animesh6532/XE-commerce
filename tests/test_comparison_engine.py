# tests/test_comparison_engine.py

import unittest
import sys
from pathlib import Path

# Add ml_models/chatbot to Python path
CHATBOT_DIR = Path(__file__).resolve().parent.parent / "ml_models" / "chatbot"
if str(CHATBOT_DIR) not in sys.path:
    sys.path.append(str(CHATBOT_DIR))

try:
    from comparison_engine import ComparisonEngine
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


class TestComparisonEngine(unittest.TestCase):

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "ComparisonEngine failed to import.")
        self.engine = ComparisonEngine()

    def test_entity_extraction(self):
        """Tests that brands and categories are correctly parsed from comparison queries."""
        brand_a, brand_b, category = self.engine.extract_entities("Compare Boat vs JBL Headphones")
        self.assertEqual(brand_a, "Boat")
        self.assertEqual(brand_b, "Jbl")
        self.assertEqual(category, "Headphones")

        brand_a2, brand_b2, category2 = self.engine.extract_entities("Samsung vs OnePlus")
        self.assertEqual(brand_a2, "Samsung")
        self.assertEqual(brand_b2, "Oneplus")
        self.assertIsNone(category2)

    def test_compare_products(self):
        """Tests end-to-end product comparison execution."""
        # Using real dataset query: "LG vs Panasonic AC"
        res = self.engine.compare("LG vs Panasonic AC")
        
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["brand_a"], "Lg")
        self.assertEqual(res["brand_b"], "Panasonic")
        self.assertIn("comparison", res)
        
        comp = res["comparison"]
        self.assertIn("price", comp)
        self.assertIn("ratings", comp)
        self.assertIn("pros", comp)
        self.assertIn("cons", comp)
        self.assertIn("recommendation", comp)


if __name__ == "__main__":
    unittest.main()
