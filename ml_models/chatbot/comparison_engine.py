# comparison_engine.py

import re
import logging
from typing import Dict, Any, Tuple, Optional, List
from category_router import CategoryRouter
from retrieval import ProductRetriever

logger = logging.getLogger(__name__)


class ComparisonEngine:
    """
    Compares two brands/products dynamically based on dataset metadata.
    Extracts compared entities, queries the relevant dataset, and returns a detailed comparison.
    """

    def __init__(self, category_router: Optional[CategoryRouter] = None):
        self.router = category_router or CategoryRouter()
        self.retriever_cache: Dict[str, ProductRetriever] = {}

    def extract_entities(self, query: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Extracts two brands/products and their category from comparison queries.
        Supports patterns like "Samsung vs OnePlus", "LG vs Panasonic AC", "Boat vs JBL Headphones".
        
        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]: (brand_a, brand_b, category)
        """
        # Patterns like: "Compare A vs B", "A vs B AC", "Compare A versus B Headphones"
        q_clean = re.sub(r'\bcompare\b', '', query, flags=re.IGNORECASE).strip()
        
        # Split by vs / versus
        split_patterns = [r'\bvs\b', r'\bversus\b', r'\band\b']
        for pattern in split_patterns:
            parts = re.split(pattern, q_clean, flags=re.IGNORECASE)
            if len(parts) >= 2:
                brand_a = parts[0].strip()
                rest = parts[1].strip()
                
                # Try to extract category from rest (e.g. "JBL Headphones" -> brand: "JBL", category: "Headphones")
                # We can check if any popular category names are at the end of 'rest' or 'brand_a'
                category = None
                brand_b = rest
                
                # Check if there is a category word in the query
                for cat in ["ac", "air conditioner", "headphones", "earbuds", "phone", "mobile", "laptop", "mouse", "keyboard", "tv", "television", "refrigerator"]:
                    if cat in rest.lower():
                        category = cat
                        # Strip category from brand_b
                        brand_b = re.sub(r'\b' + re.escape(cat) + r's?\b', '', rest, flags=re.IGNORECASE).strip()
                        break
                    elif cat in brand_a.lower():
                        category = cat
                        brand_a = re.sub(r'\b' + re.escape(cat) + r's?\b', '', brand_a, flags=re.IGNORECASE).strip()
                        break

                # Capitalize first letters for clean names
                brand_a = brand_a.title()
                brand_b = brand_b.title()
                category_name = category.title() if category else None
                return brand_a, brand_b, category_name

        return None, None, None

    def compare(self, query: str) -> Dict[str, Any]:
        """
        Orchestrates entity extraction, retrieval, and metadata comparison.
        """
        brand_a, brand_b, category = self.extract_entities(query)
        if not brand_a or not brand_b:
            # Fallback parsing
            return {
                "status": "error",
                "message": "Could not identify two entities to compare in the query.",
                "brand_a": None,
                "brand_b": None,
                "category": None,
                "comparison": None
            }

        # Route to best dataset
        routing_query = f"{brand_a} vs {brand_b} {category or ''}".strip()
        routing_result = self.router.find_best_dataset(routing_query)
        dataset_name = routing_result["dataset"]
        dataset_path = routing_result["path"]

        logger.info(f"Comparison query '{query}' routed to dataset: {dataset_name}")

        # Instantiate retriever
        if dataset_name not in self.retriever_cache:
            self.retriever_cache[dataset_name] = ProductRetriever(
                dataset_path=dataset_path,
                embedder=self.router.embedder
            )
        retriever = self.retriever_cache[dataset_name]

        # Query separately for each brand
        search_a = retriever.search(f"{brand_a} {category or ''}", top_k=3)
        search_b = retriever.search(f"{brand_b} {category or ''}", top_k=3)

        if not search_a and not search_b:
            return {
                "status": "error",
                "message": f"No products found for either {brand_a} or {brand_b} in the {dataset_name} catalog.",
                "brand_a": brand_a,
                "brand_b": brand_b,
                "category": category,
                "comparison": None
            }

        prod_a = search_a[0] if search_a else None
        prod_b = search_b[0] if search_b else None

        # Build comparison details
        comparison = self._generate_comparison_details(prod_a, prod_b, brand_a, brand_b)

        return {
            "status": "success",
            "brand_a": brand_a,
            "brand_b": brand_b,
            "category": category,
            "dataset": dataset_name,
            "product_a": prod_a,
            "product_b": prod_b,
            "comparison": comparison
        }

    def _generate_comparison_details(self, prod_a: Optional[Dict[str, Any]], prod_b: Optional[Dict[str, Any]], brand_a: str, brand_b: str) -> Dict[str, Any]:
        details = {
            "price": "N/A",
            "ratings": "N/A",
            "review_count": "N/A",
            "pros": {brand_a: [], brand_b: []},
            "cons": {brand_a: [], brand_b: []},
            "recommendation": "No recommendation could be generated."
        }

        if not prod_a and prod_b:
            details["recommendation"] = f"Only {brand_b} has matching products. We recommend: {prod_b['name']}."
            return details
        if not prod_b and prod_a:
            details["recommendation"] = f"Only {brand_a} has matching products. We recommend: {prod_a['name']}."
            return details

        # Both exist
        price_a = prod_a.get("clean_discount_price")
        price_b = prod_b.get("clean_discount_price")
        rating_a = prod_a.get("clean_rating", 0.0)
        rating_b = prod_b.get("clean_rating", 0.0)
        reviews_a = prod_a.get("clean_no_of_ratings", 0.0)
        reviews_b = prod_b.get("clean_no_of_ratings", 0.0)

        # Price Comparison Text
        price_str_a = f"Rs. {price_a:,.2f}" if price_a else "N/A"
        price_str_b = f"Rs. {price_b:,.2f}" if price_b else "N/A"
        details["price"] = f"{brand_a} is priced at {price_str_a} vs {brand_b} at {price_str_b}."

        # Ratings Comparison Text
        details["ratings"] = f"{brand_a} has a customer rating of {rating_a} ⭐ vs {brand_b} with {rating_b} ⭐."

        # Review Count Comparison Text
        details["review_count"] = f"{brand_a} has {int(reviews_a):,} ratings vs {brand_b} with {int(reviews_b):,} ratings."

        # Generate Pros and Cons
        # Pros A
        if price_a and price_b and price_a < price_b:
            details["pros"][brand_a].append("More cost-effective / budget friendly choice")
            details["cons"][brand_b].append("Higher purchase price")
        elif price_b and price_a and price_b < price_a:
            details["pros"][brand_b].append("More cost-effective / budget friendly choice")
            details["cons"][brand_a].append("Higher purchase price")

        if rating_a > rating_b:
            details["pros"][brand_a].append(f"Higher overall customer satisfaction rating ({rating_a} vs {rating_b} stars)")
            details["cons"][brand_b].append("Slightly lower customer rating than competitor")
        elif rating_b > rating_a:
            details["pros"][brand_b].append(f"Higher overall customer satisfaction rating ({rating_b} vs {rating_a} stars)")
            details["cons"][brand_a].append("Slightly lower customer rating than competitor")

        if reviews_a > reviews_b * 1.5:
            details["pros"][brand_a].append("Significantly higher volume of customer feedback, implying larger market share")
            details["cons"][brand_b].append("Fewer user reviews, suggesting lesser adoption or newer release")
        elif reviews_b > reviews_a * 1.5:
            details["pros"][brand_b].append("Significantly higher volume of customer feedback, implying larger market share")
            details["cons"][brand_a].append("Fewer user reviews, suggesting lesser adoption or newer release")

        # Fallbacks for pros/cons if empty
        if not details["pros"][brand_a]:
            details["pros"][brand_a].append("Solid performance options")
        if not details["pros"][brand_b]:
            details["pros"][brand_b].append("Capable competitive specs")
        if not details["cons"][brand_a]:
            details["cons"][brand_a].append("None significant")
        if not details["cons"][brand_b]:
            details["cons"][brand_b].append("None significant")

        # Recommendation logic
        score_a = prod_a.get("ranking_score", 0.0)
        score_b = prod_b.get("ranking_score", 0.0)

        if score_a > score_b:
            reason = f"it offers a superior balance of customer ratings ({rating_a} ⭐) and reviews ({int(reviews_a):,})"
            if price_a and price_b and price_a < price_b:
                reason += f" at a more affordable price point ({price_str_a})"
            details["recommendation"] = f"Based on historical data and consumer satisfaction metrics, we recommend the **{prod_a['name']}** because {reason}."
        else:
            reason = f"it offers a superior balance of customer ratings ({rating_b} ⭐) and reviews ({int(reviews_b):,})"
            if price_b and price_a and price_b < price_a:
                reason += f" at a more affordable price point ({price_str_b})"
            details["recommendation"] = f"Based on historical data and consumer satisfaction metrics, we recommend the **{prod_b['name']}** because {reason}."

        return details


if __name__ == "__main__":
    engine = ComparisonEngine()
    test_queries = [
        "Compare Boat vs JBL Headphones",
        "LG vs Panasonic AC",
        "Samsung vs OnePlus"
    ]
    for q in test_queries:
        res = engine.compare(q)
        print(f"\nQuery: {q}")
        if res["status"] == "success":
            print(f"Dataset routed: {res['dataset']}")
            print(f"Product A: {res['product_a']['name']} | Price: {res['product_a']['discount_price']}")
            print(f"Product B: {res['product_b']['name']} | Price: {res['product_b']['discount_price']}")
            print(f"Comparison: {res['comparison']}")
        else:
            print(f"Error: {res['message']}")
