# tests/test_query_parser.py

import unittest
import sys
from pathlib import Path

# Add ml_models/chatbot to Python path
CHATBOT_DIR = Path(__file__).resolve().parent.parent / "ml_models" / "chatbot"
if str(CHATBOT_DIR) not in sys.path:
    sys.path.append(str(CHATBOT_DIR))

try:
    from query_parser import QueryParser
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


class TestQueryParser(unittest.TestCase):

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "QueryParser failed to import.")
        self.parser = QueryParser()

    def test_budget_extraction(self):
        # Numeric extraction
        res1 = self.parser.parse("gaming mouse under 3000 rupees")
        self.assertEqual(res1["budget"], 3000.0)

        # Multiplier extraction
        res2 = self.parser.parse("split AC below 40k")
        self.assertEqual(res2["budget"], 40000.0)

        res3 = self.parser.parse("laptop max price 60 thousand")
        self.assertEqual(res3["budget"], 60000.0)

    def test_rating_extraction(self):
        res1 = self.parser.parse("rated 4.5 star headphones")
        self.assertEqual(res1["min_rating"], 4.5)

        res2 = self.parser.parse("earbuds with 4+ stars")
        self.assertEqual(res2["min_rating"], 4.0)

    def test_brand_extraction(self):
        res1 = self.parser.parse("best samsung phone")
        self.assertEqual(res1["brand"], "Samsung")

        res2 = self.parser.parse("compare Boat vs JBL headphones")
        # Matches the first found brand in popular_brands check
        self.assertIn(res2["brand"], ["Boat", "JBL"])

    def test_category_extraction(self):
        res1 = self.parser.parse("split AC under 30000")
        self.assertEqual(res1["category"], "ac")

        res2 = self.parser.parse("gaming keyboards below 5000")
        self.assertEqual(res2["category"], "keyboard")


if __name__ == "__main__":
    unittest.main()
