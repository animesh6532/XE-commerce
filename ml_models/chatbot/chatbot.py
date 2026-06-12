# chatbot.py

import re
import sys
import logging
from typing import Dict, Any, List, Tuple, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich import box

from rag_pipeline import RAGPipeline

# Configure logger
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ShoppingAssistant:
    """
    Main interactive interface for the AI Product Recommendation & Discovery Engine.
    Handles CLI commands, parses query intent/filters, runs the RAG pipeline, 
    and presents results in a beautiful rich format.
    """

    def __init__(self):
        self.console = Console()
        self.pipeline: Optional[RAGPipeline] = None
        self.history: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        """Initializes the RAG pipeline with a status spinner."""
        self.console.print(Panel.fit(
            "[bold green]Initializing Aura AI Commerce Assistant...[/bold green]\n"
            "[dim]Loading SentenceTransformer embeddings and cache router...[/dim]",
            border_style="cyan"
        ))
        try:
            self.pipeline = RAGPipeline()
            self.console.print("[bold green]Aura is online and ready![/bold green] Type [cyan]/help[/cyan] to see available commands.\n")
        except Exception as e:
            self.console.print(f"[bold red]Initialization failed: {e}[/bold red]")
            sys.exit(1)

    def parse_query_metadata(self, query: str) -> Tuple[str, Optional[float], Optional[float]]:
        """
        Parses budget limits and rating thresholds from a natural language query.
        
        Examples:
            "Gaming mouse under 2000" -> ("Gaming mouse", 2000.0, None)
            "AC rated 4 stars and under 40000" -> ("AC", 40000.0, 4.0)
            
        Returns:
            Tuple[str, Optional[float], Optional[float]]: (cleaned_query, budget, min_rating)
        """
        budget: Optional[float] = None
        min_rating: Optional[float] = None
        cleaned_query = query

        # 1. Parse budget (e.g. "under 5000 rupees", "below 10k", "budget 15000 inr")
        price_patterns = [
            r'(?:under|below|less\s+than|max|budget\s+of|budget)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?\s*(?:rupees|inr|₹|bucks|dollars|usd|rs\.?)?',
            r'(?:price|cost)\s*(?:under|below|less\s+than|<=)\s*(?:rs\.?|inr|₹)?\s*(\d+(?:\.\d+)?)\s*(k|thousand)?\s*(?:rupees|inr|₹|bucks|dollars|usd|rs\.?)?'
        ]

        for pattern in price_patterns:
            match = re.search(pattern, cleaned_query, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                multiplier = match.group(2)
                if multiplier:
                    if multiplier.lower() == 'k' or multiplier.lower() == 'thousand':
                        value *= 1000
                budget = value
                # Remove matched filter text from query for clean semantic search
                cleaned_query = cleaned_query.replace(match.group(0), "")
                break

        # 2. Parse minimum rating (e.g. "4+ stars", "rated above 4.5", "rating 4", "rated 4.5 star")
        rating_patterns = [
            r'(?:rating|rated)\s*(?:above|>=|of)?\s*(\d+(?:\.\d+)?)\s*stars?',
            r'(?:rating|rated)\s*(?:above|>=|of)?\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:\+|-)?\s*stars?(?:\s*(?:and\s+)?above)?'
        ]

        for pattern in rating_patterns:
            match = re.search(pattern, cleaned_query, re.IGNORECASE)
            if match:
                min_rating = float(match.group(1))
                # Remove matched filter text from query
                cleaned_query = cleaned_query.replace(match.group(0), "")
                break

        # Clean double whitespaces
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        return cleaned_query, budget, min_rating

    def detect_query_type(self, query: str) -> str:
        """Detects whether the query requests a comparison, explanation, or general recommendation."""
        q_lower = query.lower()
        if any(w in q_lower for w in ["compare", "difference", "vs", "versus"]):
            return "comparison"
        elif any(w in q_lower for w in ["why", "explain", "reason", "justify"]):
            return "explanation"
        return "recommendation"

    def _display_products_table(self, products: List[Dict[str, Any]]) -> None:
        """Prints products in a beautifully formatted comparison table using rich."""
        if not products:
            self.console.print("[yellow]No products match the requested filters.[/yellow]")
            return

        table = Table(box=box.DOUBLE_EDGE, show_header=True, header_style="bold magenta", border_style="dim blue")
        table.add_column("#", style="dim", width=3)
        table.add_column("Product Name", style="bold white", width=55)
        table.add_column("Price", style="cyan", justify="right")
        table.add_column("Rating", style="green", justify="center")
        table.add_column("Reviews", style="dim cyan", justify="right")
        table.add_column("Rank Score", style="yellow", justify="center")

        for idx, p in enumerate(products, start=1):
            price_str = str(p.get("discount_price", "N/A")).replace("₹", "Rs.").strip()
            orig_price = str(p.get("actual_price", "")).replace("₹", "Rs.").strip()
            
            price_display = price_str
            if orig_price and orig_price != price_str:
                price_display += f"\n[dim strikethrough]{orig_price}[/dim strikethrough]"

            rating = f"{p['clean_rating']} ⭐" if p["clean_rating"] > 0 else "N/A"
            reviews = f"{int(p['clean_no_of_ratings']):,}"

            table.add_row(
                str(idx),
                p["name"][:90] + ("..." if len(p["name"]) > 90 else ""),
                price_display,
                rating,
                reviews,
                f"{p['ranking_score']:.2f}"
            )

        self.console.print(table)

    def _display_product_links(self, products: List[Dict[str, Any]]) -> None:
        """Displays formatted purchase links and details in a clean panel."""
        self.console.print("\n[bold magenta]🛍️ Product Details & Links:[/bold magenta]")
        for idx, p in enumerate(products, start=1):
            name = p["name"]
            price_str = str(p.get("discount_price", "N/A")).replace("₹", "Rs.").strip()
            link = p.get("link", "#")

            self.console.print(f"[bold magenta][{idx}][/bold magenta] [bold white]{name}[/bold white]")
            self.console.print(f"    [dim]Category: {p.get('main_category', 'N/A')} > {p.get('sub_category', 'N/A')} | Price: {price_str}[/dim]")
            if link and link != "#":
                self.console.print(f"    🔗 [blue underline]{link}[/blue underline]")

    def _generate_fallback_response(
        self, 
        query: str, 
        routed_dataset: str, 
        products: List[Dict[str, Any]], 
        query_type: str
    ) -> str:
        """Generates natural language shopping assistance when external LLM is not active."""
        if not products:
            return f"I searched the '{routed_dataset}' catalog, but couldn't find matches fitting your filters. Try widening your filters!"

        best = products[0]
        best_price = str(best.get("discount_price", "N/A")).replace("₹", "Rs.").strip()
        best_orig = str(best.get("actual_price", "N/A")).replace("₹", "Rs.").strip()

        if query_type == "explanation":
            return (
                f"I highly recommend the **{best['name']}** from our **{routed_dataset}** selection.\n\n"
                f"**Why this product fits your query:**\n"
                f"- **Price**: Offered at **{best_price}** (original: {best_orig}).\n"
                f"- **Quality**: Carries a strong rating of **{best['clean_rating']} ⭐** based on **{int(best['clean_no_of_ratings']):,}** reviews.\n"
                f"- **Relevance**: Has a calculated search relevance score of **{best['ranking_score']}**, meaning it is the highest quality matching product."
            )
            
        elif query_type == "comparison":
            comparison = f"I compared the top choices in **{routed_dataset}** for your query:\n\n"
            if len(products) > 1:
                cheapest = min(products, key=lambda x: x["clean_discount_price"] or float("inf"))
                most_popular = max(products, key=lambda x: x["clean_no_of_ratings"])
                highest_rated = max(products, key=lambda x: x["clean_rating"])
                
                cheap_price = str(cheapest.get("discount_price", "N/A")).replace("₹", "Rs.").strip()

                comparison += f"- 💰 **Best Budget Option**: **{cheapest['name']}** priced at **{cheap_price}**.\n"
                comparison += f"- 🔥 **Most Popular Choice**: **{most_popular['name']}** with **{int(most_popular['clean_no_of_ratings']):,}** customer ratings.\n"
                comparison += f"- ⭐ **Highest Rated Option**: **{highest_rated['name']}** carrying **{highest_rated['clean_rating']} ⭐** stars.\n\n"
                comparison += "If budget is priority, choose the **Best Budget** option. If you want the most trusted, choose the **Most Popular** option."
            else:
                comparison += f"Only one relevant product was found: **{best['name']}** priced at **{best_price}**."
            return comparison
            
        else:  # recommendation
            recs = (
                f"I discovered some great options in the **{routed_dataset}** catalog. "
                f"Applying our popularity-weighted rank score, here are the top recommendations:\n\n"
            )
            for idx, p in enumerate(products, start=1):
                price_str = str(p.get("discount_price", "N/A")).replace("₹", "Rs.").strip()
                recs += f"{idx}. **{p['name']}** — **{price_str}** ({p['clean_rating']} ⭐, {int(p['clean_no_of_ratings']):,} reviews)\n"
            
            recs += f"\n💡 **My Recommendation**: The best match is the **{best['name']}** because it offers the optimal balance between high score and rating."
            return recs

    def process_user_message(self, raw_message: str) -> None:
        """Routes, retrieves, and displays response for the user's natural language question."""
        if not raw_message.strip():
            return

        # Check for slash commands
        if raw_message.startswith("/"):
            self._handle_command(raw_message)
            return

        # 1. Parse query metadata constraints
        cleaned_query, budget, min_rating = self.parse_query_metadata(raw_message)
        query_type = self.detect_query_type(raw_message)

        # 2. Run RAG Pipeline
        with self.console.status(f"[bold magenta]Aura is searching the catalog...[/bold magenta]"):
            response = self.pipeline.query(
                user_query=cleaned_query,
                budget=budget,
                min_rating=min_rating,
                top_k=5,
                query_type=query_type
            )

        # 3. Add to history
        self.history.append({
            "raw_query": raw_message,
            "cleaned_query": cleaned_query,
            "routed_dataset": response["routed_dataset"],
            "similarity": response["routing_similarity"],
            "products_count": len(response["products"]),
            "status": response["status"]
        })

        if response["status"] == "error":
            self.console.print(Panel(
                f"[bold red]RAG Pipeline Error:[/bold red] {response.get('message', 'Unknown error')}",
                title="Error Info", border_style="red"
            ))
            return

        # 4. Present routed dataset info
        self.console.print(f"\n🗺️ [dim]Routed to catalog:[/dim] [bold cyan]{response['routed_dataset']}[/bold cyan] [dim](Confidence: {response['routing_similarity']:.2f})[/dim]")
        
        # 5. Display comparison table
        self._display_products_table(response["products"])

        # 6. Display natural language summary
        natural_response = self._generate_fallback_response(
            query=cleaned_query,
            routed_dataset=response["routed_dataset"],
            products=response["products"],
            query_type=query_type
        )
        
        self.console.print(Panel(
            natural_response,
            title="Aura AI Response Summary",
            border_style="magenta",
            box=box.ROUNDED
        ))

        # 7. Display links
        self._display_product_links(response["products"])

    def _handle_command(self, cmd_str: str) -> None:
        """Handles chatbot CLI utility slash commands."""
        parts = cmd_str.split(" ", 1)
        command = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if command == "/help":
            self.console.print(Panel(
                "[bold cyan]Available Commands:[/bold cyan]\n"
                "  [cyan]/help[/cyan] - Show this help menu\n"
                "  [cyan]/history[/cyan] - View search and routing history\n"
                "  [cyan]/datasets[/cyan] - List all available product category catalogs\n"
                "  [cyan]/route <query>[/cyan] - Test category router on a query without loading products\n"
                "  [cyan]/prompt <query>[/cyan] - Display the raw LLM prompt constructed for a query\n"
                "  [cyan]/clear[/cyan] - Clear chatbot session history\n"
                "  [cyan]/exit[/cyan] - Exit the assistant",
                title="Aura System Help", border_style="cyan"
            ))
            
        elif command == "/history":
            if not self.history:
                self.console.print("[yellow]Session history is empty.[/yellow]")
                return
            
            table = Table(title="Session Query History", box=box.ROUNDED)
            table.add_column("Raw Query", style="bold white")
            table.add_column("Routed Dataset", style="cyan")
            table.add_column("Confidence", style="green")
            table.add_column("Matches", style="yellow", justify="center")

            for h in self.history:
                table.add_row(
                    h["raw_query"],
                    h["routed_dataset"] or "N/A",
                    f"{h['similarity']:.2f}",
                    str(h["products_count"])
                )
            self.console.print(table)
            
        elif command == "/datasets":
            datasets_list = self.pipeline.router.datasets
            self.console.print(f"\n[bold cyan]Available Category Datasets ({len(datasets_list)}):[/bold cyan]")
            # Print in 3 columns
            grid = Table.grid(padding=1)
            grid.add_column(width=30)
            grid.add_column(width=30)
            grid.add_column(width=30)
            for i in range(0, len(datasets_list), 3):
                row_items = datasets_list[i:i+3]
                while len(row_items) < 3:
                    row_items.append("")
                grid.add_row(*row_items)
            self.console.print(grid)
            
        elif command == "/route":
            if not arg:
                self.console.print("[red]Usage: /route <query>[/red]")
                return
            routing = self.pipeline.router.top_k_datasets(arg, k=5)
            self.console.print(Panel(
                "\n".join([f"[{idx}] {r['dataset']} - Score: {r['similarity']}" for idx, r in enumerate(routing, 1)]),
                title=f"Routing matches for: '{arg}'", border_style="green"
            ))
            
        elif command == "/prompt":
            if not arg:
                self.console.print("[red]Usage: /prompt <query>[/red]")
                return
            cleaned_query, budget, min_rating = self.parse_query_metadata(arg)
            res = self.pipeline.query(cleaned_query, budget=budget, min_rating=min_rating, top_k=3)
            self.console.print(Panel(
                res["prompt"],
                title="Constructed LLM Prompt Context", border_style="yellow"
            ))
            
        elif command == "/clear":
            self.history.clear()
            self.console.print("[bold green]Chatbot history cleared.[/bold green]")
            
        elif command == "/exit":
            self.console.print("[bold yellow]Goodbye from Aura AI Assistant! Happy shopping![/bold yellow]")
            sys.exit(0)
            
        else:
            self.console.print(f"[bold red]Unknown command: {command}.[/bold red] Type /help to see commands.")

    def run_cli_loop(self) -> None:
        """Starts the interactive CLI chat loop."""
        self.initialize()
        
        # Welcoming message panel
        self.console.print(Panel(
            "[bold white]Welcome to Aura AI Shopping Assistant![/bold white]\n"
            "I can understand complex shopping requests, extract your budget and rating rules, "
            "semantically search 140+ categories, and recommend the best products using advanced ranking.\n\n"
            "[bold cyan]Try asking something like:[/bold cyan]\n"
            "  * 'Show me gaming mouse under 3000 rupees'\n"
            "  * 'Compare LG vs Panasonic split AC under 40000'\n"
            "  * 'Explain why Lloyd 1.5 Ton AC is good'",
            title="Aura Discovery Engine v1.0",
            border_style="magenta",
            box=box.DOUBLE
        ))

        while True:
            try:
                user_input = Prompt.ask("[bold green]You[/bold green]")
                if user_input.lower().strip() in ["exit", "quit"]:
                    self.console.print("[bold yellow]Goodbye![/bold yellow]")
                    break
                self.process_user_message(user_input)
                self.console.print()
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[bold yellow]Exiting assistant. Goodbye![/bold yellow]")
                break
            except Exception as e:
                self.console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]\n")


if __name__ == "__main__":
    # Reconfigure stdout for Windows console unicode printing
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
        
    bot = ShoppingAssistant()
    bot.run_cli_loop()