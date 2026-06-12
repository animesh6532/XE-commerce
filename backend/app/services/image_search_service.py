import shutil
import tempfile
import os
from pathlib import Path
import numpy as np
from PIL import Image

from app.database.models import Product

# Ensure ml_models/image_search is in python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
import sys
if str(PROJECT_ROOT / "ml_models" / "image_search") not in sys.path:
    sys.path.append(str(PROJECT_ROOT / "ml_models" / "image_search"))

from image_encoder import ImageEncoder

class ImageSearchService:
    def __init__(self):
        # We load ImageEncoder dynamically to prevent torchvision loading blocking start
        self.encoder = None

    def _get_encoder(self):
        if self.encoder is None:
            self.encoder = ImageEncoder()
        return self.encoder

    def _process_image_upload(self, upload_file) -> str:
        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / upload_file.filename
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(temp_path)

    async def search_by_image(self, image):
        temp_file = self._process_image_upload(image)
        try:
            encoder = self._get_encoder()
            query_emb = encoder.encode(temp_file)
            
            # Fetch products from database
            from app.database.connection import SessionLocal
            db = SessionLocal()
            try:
                products = db.query(Product).limit(5).all()
                results = []
                for p in products:
                    # Compute mock visual similarity based on rating/price for demo
                    mock_sim = float(0.85 + (p.rating / 50.0))
                    results.append({
                        "id": p.id,
                        "name": p.name,
                        "price": p.price,
                        "rating": p.rating,
                        "similarity": round(mock_sim, 4)
                    })
                results.sort(key=lambda x: x["similarity"], reverse=True)
                return results
            finally:
                db.close()
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    async def find_similar_products(self, image, top_k: int = 5):
        res = await self.search_by_image(image)
        return res[:top_k]

    async def reverse_search(self, image):
        res = await self.search_by_image(image)
        return [{"match_name": item["name"], "score": item["similarity"]} for item in res]

    async def recommend_products(self, image, top_k: int = 10):
        res = await self.search_by_image(image)
        return res[:top_k]

    def health(self):
        return {"status": "healthy", "service": "image_search_service"}
