# tests/test_intent_classifier.py

import unittest
import sys
from pathlib import Path

# Add ml_models/chatbot to Python path
CHATBOT_DIR = Path(__file__).resolve().parent.parent / "ml_models" / "chatbot"
if str(CHATBOT_DIR) not in sys.path:
    sys.path.append(str(CHATBOT_DIR))

try:
    from intent_classifier import IntentClassifier
    MODULES_IMPORTED = True
except ImportError:
    MODULES_IMPORTED = False


class TestIntentClassifier(unittest.TestCase):

    def setUp(self):
        self.assertTrue(MODULES_IMPORTED, "IntentClassifier failed to import.")
        self.classifier = IntentClassifier()

    def test_intent_classification(self):
        """Tests that queries route to the correct high-level intents."""
        test_cases = [
            ("Mechanical gaming keyboard under 5000", "Gaming"),
            ("best samsung phone under 20000", "Electronics"),
            ("refrigerator with double door split cooling", "Home Appliances"),
            ("dog food and puppy chew toys", "Pets"),
            ("running shoes for track and fitness", "Sports"),
            ("ac split inverter 1.5 ton", "Home Appliances"),
            ("car shampoo and wax care", "Automotive"),
            ("organic snacks and green tea", "Kitchen")
        ]

        for query, expected_intent in test_cases:
            result = self.classifier.classify(query)
            self.assertEqual(result["intent"], expected_intent, f"Failed for query: '{query}'")
            self.assertIn("confidence", result)
            self.assertGreaterEqual(result["confidence"], 0.0)
            self.assertLessEqual(result["confidence"], 1.0)


if __name__ == "__main__":
    unittest.main()
