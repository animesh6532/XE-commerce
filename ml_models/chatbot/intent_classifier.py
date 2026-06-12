# intent_classifier.py

import re
import logging
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from model_manager import ModelManager

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    SentenceTransformer-based Zero-shot classifier for e-commerce user intents.
    Classifies a query into one of 11 defined domains.
    """

    def __init__(self):
        """Initializes the classifier, loading model and category embeddings."""
        self.model_manager = ModelManager.get_instance()
        
        self.categories = [
            "Electronics",
            "Gaming",
            "Books",
            "Fashion",
            "Home Appliances",
            "Pets",
            "Sports",
            "Automotive",
            "Health",
            "Kitchen",
            "Beauty"
        ]

        # Use rich descriptions for each class to improve semantic matching
        self.category_descriptions = {
            "Electronics": "consumer electronics, mobile phones, computers, audio equipment, cameras, accessories, headphones, wireless earbuds, smart watch",
            "Gaming": "gaming accessories, gaming keyboards, gaming mouse, gaming laptops, video games, gaming consoles, gaming controllers",
            "Books": "books, novels, e-books, kindle, school textbooks, exam study material, reading material",
            "Fashion": "apparel, clothing, shirts, t-shirts, jeans, formal shoes, casual shoes, backpacks, bags, luggage, jewelry, watches, clothing store",
            "Home Appliances": "home appliances, air conditioners, split AC, refrigerators, washing machines, cooling, heating",
            "Pets": "pet supplies, dog supplies, dog food, cat food, dog toys, pet accessories",
            "Sports": "sports equipment, fitness accessories, gym gear, exercise, cardio, running shoes, badminton, cricket, cycling, yoga",
            "Automotive": "car accessories, motorbike parts, vehicle electronics, car care, bike parts",
            "Health": "pharmacy, diet, nutrition, personal care appliances, vitamins, wellness products",
            "Kitchen": "kitchen and dining, kitchen storage, containers, household items, grocery, snack foods, beverages",
            "Beauty": "beauty and grooming, makeup, cosmetics, skin care, luxury beauty"
        }

        self.category_texts = [self.category_descriptions[cat] for cat in self.categories]
        logger.info("Encoding category descriptions for zero-shot classification...")
        self.category_embeddings = self.model_manager.encode(self.category_texts)

    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classifies a user query into one of the 11 categories.
        
        Args:
            query (str): Natural language user search query.
            
        Returns:
            Dict[str, Any]: Dict containing "intent" and "confidence" score.
        """
        if not query.strip():
            return {"intent": "Electronics", "confidence": 1.0}

        q_lower = query.lower()
        # Extract individual words to prevent substring matches (e.g. 'ac' in 'track')
        q_words = set(re.findall(r'\b\w+\b', q_lower))

        # Rule-based boosts for common e-commerce keywords
        boosts = {cat: 0.0 for cat in self.categories}
        
        # Home Appliances
        if any(w in q_words for w in ["ac", "heater", "cooling"]) or \
           any(p in q_lower for p in ["air conditioner", "refrigerator", "fridge", "washing machine"]):
            boosts["Home Appliances"] = 0.5
            
        # Gaming
        if any(w in q_words for w in ["gaming", "keyboard", "mouse", "console", "controller"]) or \
           any(p in q_lower for p in ["pc games", "video games"]):
            boosts["Gaming"] = 0.5
            
        # Pets
        if any(w in q_words for w in ["pet", "dog", "cat", "puppy", "food"]):
            if "dog" in q_words or "cat" in q_words or "pet" in q_words:
                boosts["Pets"] = 0.5

        # Books
        if any(w in q_words for w in ["book", "novel", "textbook", "kindle"]):
            boosts["Books"] = 0.5
            
        # Beauty
        if any(w in q_words for w in ["beauty", "grooming", "makeup", "cosmetics", "skin care"]):
            boosts["Beauty"] = 0.5

        try:
            query_embedding = self.model_manager.encode([query])
            similarities = cosine_similarity(query_embedding, self.category_embeddings)[0]
            
            # Apply boosts
            for i, cat in enumerate(self.categories):
                similarities[i] += boosts[cat]

            # Use temperature scaling (T=20) to compute softmax probabilities
            # This accentuates the confidence scores for clear matches
            temperature = 20.0
            exp_sims = np.exp(similarities * temperature)
            confidences = exp_sims / np.sum(exp_sims)
            
            best_idx = np.argmax(confidences)
            predicted_intent = self.categories[best_idx]
            confidence_score = float(confidences[best_idx])
            
            logger.info(f"Query: '{query}' classified as '{predicted_intent}' with confidence: {confidence_score:.4f}")
            return {
                "intent": predicted_intent,
                "confidence": round(confidence_score, 4)
            }
        except Exception as e:
            logger.error(f"Error during intent classification for '{query}': {e}")
            # Fallback
            return {"intent": "Electronics", "confidence": 0.5}


if __name__ == "__main__":
    classifier = IntentClassifier()
    test_queries = [
        "Mechanical gaming keyboard under 5000",
        "best samsung phone under 20000",
        "wireless earbuds under 2k",
        "dog food 10kg",
        "inverter split AC",
        "casual shoes for men"
    ]
    for q in test_queries:
        print(f"Query: {q} -> {classifier.classify(q)}")
