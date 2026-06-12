# prompt_templates.py

import logging
from typing import List, Dict, Any, Optional

from prompts import (
    SYSTEM_PROMPT,
    RECOMMENDATION_PROMPT_TEMPLATE,
    COMPARISON_PROMPT_TEMPLATE,
    EXPLANATION_PROMPT_TEMPLATE,
    SEARCH_PROMPT_TEMPLATE
)

# Configure logger
logger = logging.getLogger(__name__)


class PromptGenerator:
    """
    Formats retrieved product data and metadata into structured context strings,
    and interpolates them into prompt templates to generate LLM-ready prompts.
    """

    @staticmethod
    def _format_products_context(products: List[Dict[str, Any]]) -> str:
        """
        Converts list of product dicts into a structured text string.
        
        Args:
            products (List[Dict[str, Any]]): List of product dictionaries.
            
        Returns:
            str: Structured text block representation of the products.
        """
        if not products:
            return "No products match the requested filters."

        formatted_lines = []
        for idx, product in enumerate(products, start=1):
            name = product.get("name", "Unknown Product")
            main_cat = product.get("main_category", "N/A")
            sub_cat = product.get("sub_category", "N/A")
            disc_price = product.get("discount_price", "N/A")
            act_price = product.get("actual_price", "N/A")
            rating = product.get("ratings", "N/A")
            no_ratings = product.get("no_of_ratings", "0")
            link = product.get("link", "#")
            sim_score = product.get("semantic_similarity", "N/A")
            rank_score = product.get("ranking_score", "N/A")

            # Clean prices for context display (ensures no print crash symbols)
            disp_disc = str(disc_price).replace("₹", "Rs.").strip()
            disp_act = str(act_price).replace("₹", "Rs.").strip()

            item_text = (
                f"[{idx}] Product Name: {name}\n"
                f"    Category: {main_cat} > {sub_cat}\n"
                f"    Price: {disp_disc} (Original: {disp_act})\n"
                f"    Rating: {rating}/5.0 ({no_ratings} reviews)\n"
                f"    URL: {link}\n"
                f"    Semantic Similarity: {sim_score}\n"
                f"    Relevance Rank Score: {rank_score}"
            )
            formatted_lines.append(item_text)

        return "\n\n".join(formatted_lines)

    @classmethod
    def generate_recommendation_prompt(
        cls, 
        query: str, 
        products: List[Dict[str, Any]], 
        budget_limit: Optional[float] = None
    ) -> str:
        """Generates a prompt for recommending a list of items."""
        context = cls._format_products_context(products)
        budget_str = f"Max Rs. {budget_limit:,.2f}" if budget_limit else "No budget constraint"
        
        return RECOMMENDATION_PROMPT_TEMPLATE.strip().format(
            system_prompt=SYSTEM_PROMPT.strip(),
            query=query,
            budget_info=budget_str,
            retrieved_context=context
        )

    @classmethod
    def generate_comparison_prompt(cls, query: str, products: List[Dict[str, Any]]) -> str:
        """Generates a prompt for side-by-side product comparison."""
        context = cls._format_products_context(products)
        return COMPARISON_PROMPT_TEMPLATE.strip().format(
            system_prompt=SYSTEM_PROMPT.strip(),
            query=query,
            retrieved_context=context
        )

    @classmethod
    def generate_explanation_prompt(cls, query: str, product: Dict[str, Any]) -> str:
        """Generates a prompt explaining why a specific product is a good match."""
        context = cls._format_products_context([product])
        return EXPLANATION_PROMPT_TEMPLATE.strip().format(
            system_prompt=SYSTEM_PROMPT.strip(),
            query=query,
            product_details=context
        )

    @classmethod
    def generate_search_prompt(cls, query: str, products: List[Dict[str, Any]]) -> str:
        """Generates a summary search description prompt."""
        context = cls._format_products_context(products)
        return SEARCH_PROMPT_TEMPLATE.strip().format(
            system_prompt=SYSTEM_PROMPT.strip(),
            query=query,
            retrieved_context=context
        )
