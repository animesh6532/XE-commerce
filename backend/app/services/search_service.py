from sqlalchemy.orm import Session
from sqlalchemy import or_
from pathlib import Path
import sys

# Ensure ml_models is in Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ML_MODELS_DIR = PROJECT_ROOT / "ml_models"
if str(ML_MODELS_DIR) not in sys.path:
    sys.path.append(str(ML_MODELS_DIR))

from search.semantic_search import SemanticSearch
from app.database.models import Product, SearchHistory

class SearchService:
    def __init__(self):
        dataset_path = PROJECT_ROOT / "ml_models" / "datasets" / "products.csv"
        index_path = PROJECT_ROOT / "ml_models" / "saved_models" / "products.faiss"
        # Instantiate SemanticSearch engine
        self.search_engine = SemanticSearch(str(dataset_path), str(index_path))

    def keyword_search(self, db: Session, query: str, page: int = 1, limit: int = 20):
        offset = (page - 1) * limit
        filter_cond = or_(
            Product.name.ilike(f"%{query}%"),
            Product.brand.ilike(f"%{query}%"),
            Product.category.ilike(f"%{query}%"),
            Product.description.ilike(f"%{query}%")
        )
        total = db.query(Product).filter(filter_cond).count()
        results = db.query(Product).filter(filter_cond).offset(offset).limit(limit).all()
        return {
            "results": results,
            "total": total,
            "page": page,
            "limit": limit
        }

    def semantic_search(self, query: str, top_k: int = 10):
        # SemanticSearch.search returns list of dicts from the products.csv
        # Let's map recommended product names back to DB objects to keep schema unified
        raw_recs = self.search_engine.search(query, top_k=top_k)
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            names = [item["product_name"] for item in raw_recs if "product_name" in item]
            if not names:
                names = [item["name"] for item in raw_recs if "name" in item]
            db_products = db.query(Product).filter(Product.name.in_(names)).all()
            # Sort products in order of names
            prod_map = {p.name: p for p in db_products}
            ordered = [prod_map[name] for name in names if name in prod_map]
            return ordered or db.query(Product).limit(top_k).all()
        finally:
            db.close()

    def autocomplete(self, query: str):
        # Basic auto-complete query using product name keywords
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            results = db.query(Product.name).filter(Product.name.ilike(f"%{query}%")).limit(5).all()
            return [name[0] for name in results]
        finally:
            db.close()

    def search_suggestions(self, query: str):
        return self.autocomplete(query)

    def filter_search(
        self,
        db: Session,
        query: str = None,
        category: str = None,
        brand: str = None,
        min_price: float = None,
        max_price: float = None,
        min_rating: float = None
    ):
        db_query = db.query(Product)
        if query:
            db_query = db_query.filter(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                    Product.category.ilike(f"%{query}%")
                )
            )
        if category:
            db_query = db_query.filter(Product.category == category)
        if brand:
            db_query = db_query.filter(Product.brand == brand)
        if min_price is not None:
            db_query = db_query.filter(Product.price >= min_price)
        if max_price is not None:
            db_query = db_query.filter(Product.price <= max_price)
        if min_rating is not None:
            db_query = db_query.filter(Product.rating >= min_rating)
        return db_query.all()

    def category_search(self, db: Session, category: str):
        return db.query(Product).filter(Product.category == category).all()

    def trending_searches(self):
        # returns top queries from SearchHistory
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            from sqlalchemy import func
            trending = db.query(
                SearchHistory.query,
                func.count(SearchHistory.id).label("cnt")
            ).group_by(SearchHistory.query).order_by(desc("cnt")).limit(5).all()
            return [t[0] for t in trending] or ["electronics", "laptops", "AC"]
        except Exception:
            return ["electronics", "laptops", "AC"]
        finally:
            db.close()

    def recent_searches(self, user_id: int):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            history = db.query(SearchHistory).filter(SearchHistory.user_id == user_id).order_by(SearchHistory.created_at.desc()).limit(10).all()
            return [h.query for h in history]
        finally:
            db.close()

    def save_search(self, user_id: int, query: str):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            h = SearchHistory(user_id=user_id, query=query)
            db.add(h)
            db.commit()
            return {"success": True, "message": "Search saved"}
        finally:
            db.close()

    def ai_search(self, query: str, top_k: int = 10):
        try:
            from ml_models.chatbot.rag_pipeline import RAGPipeline
        except ImportError:
            try:
                from chatbot.rag_pipeline import RAGPipeline
            except ImportError:
                import sys
                CHATBOT_DIR = PROJECT_ROOT / "ml_models" / "chatbot"
                if str(CHATBOT_DIR) not in sys.path:
                    sys.path.append(str(CHATBOT_DIR))
                from rag_pipeline import RAGPipeline

        try:
            pipeline = RAGPipeline()
            rag_res = pipeline.query(query, top_k=top_k)
            raw_recs = rag_res.get("products", [])
        except Exception:
            raw_recs = []

        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            names = []
            for item in raw_recs:
                if "product_name" in item:
                    names.append(item["product_name"])
                elif "name" in item:
                    names.append(item["name"])
            
            if names:
                db_products = db.query(Product).filter(Product.name.in_(names)).all()
                prod_map = {p.name: p for p in db_products}
                ordered = [prod_map[name] for name in names if name in prod_map]
                if ordered:
                    return ordered
            
            # Fallback to semantic search
            return self.semantic_search(query, top_k)
        finally:
            db.close()

    def similar_products(self, product_id: int):
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                return []
            # Query similar products by category
            return db.query(Product).filter(Product.category == product.category, Product.id != product_id).limit(5).all()
        finally:
            db.close()

    def health(self):
        return {"status": "healthy", "service": "search_service"}

from sqlalchemy import desc
