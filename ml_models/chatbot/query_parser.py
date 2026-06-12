# query_parser.py

import re
import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)


class QueryParser:
    """
    Parses and extracts structured metadata constraints (budget, rating, brand, category) 
    from a natural language search query.
    """

    def __init__(self):
        # A list of common brands in our e-commerce databases
        self.popular_brands = [
            "Samsung", "OnePlus", "Apple", "LG", "Panasonic", "Boat", "JBL", "Lloyd", 
            "Sony", "HP", "Dell", "Lenovo", "Xiaomi", "Realme", "Whirlpool", "Godrej", 
            "Philips", "Logitech", "Redgear", "Cosmic Byte", "Zebronics", "Portronics", 
            "Redragon", "Amkette", "Archer Tech Lab", "Saco", "Asus", "Acer", "Urban Tribe", 
            "Carbonado", "Lloyd", "Carrier", "Daikin", "Voltas", "Blue Star", "Hitachi"
        ]

        # Common categories in our databases
        self.popular_categories = [
            "phone", "mobile", "AC", "air conditioner", "laptop", "computer", "keyboard", 
            "mouse", "earbuds", "headphones", "speaker", "television", "TV", "refrigerator", 
            "washing machine", "backpack", "bag", "luggage", "shoes", "sandals", "watch", 
            "book", "novel", "tablet", "camera"
        ]

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parses constraints from the query.
        
        Args:
            query (str): The search query.
            
        Returns:
            Dict[str, Any]: Extracted metadata values.
        """
        if not query.strip():
            return {
                "brand": None,
                "budget": None,
                "min_rating": None,
                "max_price": None,
                "category": None
            }

        q_lower = query.lower()

        # 1. Extract budget / max price
        budget = self._extract_budget(query)
        max_price = budget  # Typically, budget is the maximum price

        # 2. Extract minimum rating
        min_rating = self._extract_rating(query)

        # 3. Extract brand (case-insensitive dictionary matching)
        brand = self._extract_brand(query)

        # 4. Extract category
        category = self._extract_category(query)

        parsed_data = {
            "brand": brand,
            "budget": budget,
            "min_rating": min_rating,
            "max_price": max_price,
            "category": category
        }

        logger.info(f"Query parsed: '{query}' -> {parsed_data}")
        return parsed_data

    def _extract_budget(self, query: str) -> Optional[float]:
        # Refined price patterns to match different phrasing variations
        price_patterns = [
            r'(?:under|below|less\s+than|max|budget\s+of|budget|under\s+rs\.?|below\s+rs\.?)\s*(?:price|cost)?\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?',
            r'(?:price|cost)\s*(?:under|below|less\s+than|max|<=)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?',
            r'\b(?:under|below|max|budget)\b\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?'
        ]

        for pattern in price_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                multiplier = match.group(2)
                if multiplier:
                    multiplier_lower = multiplier.lower()
                    if multiplier_lower == 'k':
                        value *= 1000
                    elif multiplier_lower == 'thousand':
                        value *= 1000
                return value
        return None

    def _extract_rating(self, query: str) -> Optional[float]:
        rating_patterns = [
            r'(?:rating|rated|stars?)\s*(?:above|of|>=|>\s*)?(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:stars?|out\s+of\s+5)?',
            r'(\d+(?:\.\d+)?)\s*(?:\+|-)?\s*stars?(?:\s*(?:and\s+)?above)?'
        ]

        for pattern in rating_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                val = float(match.group(1))
                # Validate rating is realistic (0 to 5)
                if 0.0 <= val <= 5.0:
                    return val
                elif val > 5.0 and val <= 10.0:
                    return val / 2.0  # Scale down if rated out of 10
        return None

    def _extract_brand(self, query: str) -> Optional[str]:
        q_lower = query.lower()
        for b in self.popular_brands:
            pattern = r'\b' + re.escape(b.lower()) + r'\b'
            if re.search(pattern, q_lower):
                return b
        return None

    def _extract_category(self, query: str) -> Optional[str]:
        q_lower = query.lower()
        for c in self.popular_categories:
            pattern = r'\b' + re.escape(c.lower()) + r's?\b'
            if re.search(pattern, q_lower):
                return c.lower()
        return None


if __name__ == "__main__":
    parser = QueryParser()
    test_queries = [
        "best samsung phone under 20000 with rating above 4",
        "LG vs Panasonic AC under 40k",
        "wireless earbuds below 1500 and 4.5 stars",
        "redgear keyboard for gaming",
        "dog food under 2000"
    ]
    for q in test_queries:
        print(f"Query: {q} -> {parser.parse(q)}")
