import shutil
import tempfile
import os
from pathlib import Path
import speech_recognition as sr
from sqlalchemy.orm import Session
from app.database.models import Product, SearchHistory
from app.services.search_service import SearchService

class VoiceSearchService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.search_service = SearchService()

    def _transcribe_upload_file(self, upload_file) -> str:
        # Save upload file to a temp file
        temp_dir = Path(tempfile.gettempdir())
        temp_path = temp_dir / upload_file.filename
        
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(upload_file.file, buffer)
            
            # Use speech_recognition to transcribe the audio file
            with sr.AudioFile(str(temp_path)) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
        finally:
            if temp_path.exists():
                os.remove(temp_path)

    def speech_to_text(self, audio):
        text = self._transcribe_upload_file(audio)
        return {"success": True, "text": text}

    def voice_search(self, db: Session, audio):
        text = self._transcribe_upload_file(audio)
        if not text:
            return {"success": False, "message": "Failed to transcribe audio or empty query"}
        results = self.search_service.keyword_search(db, text)
        return {
            "success": True,
            "query": text,
            "results": results
        }

    def text_search(self, db: Session, text: str):
        results = self.search_service.keyword_search(db, text)
        return {
            "success": True,
            "query": text,
            "results": results
        }

    def voice_recommendation(self, db: Session, user_id: int, audio):
        text = self._transcribe_upload_file(audio)
        if not text:
            return {"success": False, "message": "Failed to transcribe audio"}
        # Search semantically
        recs = self.search_service.semantic_search(text, top_k=5)
        return {
            "success": True,
            "query": text,
            "recommendations": recs
        }

    def category_search(self, audio):
        text = self._transcribe_upload_file(audio)
        if not text:
            return {"success": False, "message": "Failed to transcribe audio"}
        # Find product categories matching text
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            results = db.query(Product).filter(Product.category.ilike(f"%{text}%")).limit(5).all()
            return {"success": True, "query": text, "results": results}
        finally:
            db.close()

    def voice_command(self, text: str):
        # Interpret basic voice commands
        cmd = text.lower()
        if "cart" in cmd:
            action = "NAVIGATE_TO_CART"
        elif "checkout" in cmd:
            action = "NAVIGATE_TO_CHECKOUT"
        elif "profile" in cmd:
            action = "NAVIGATE_TO_PROFILE"
        else:
            action = "SEARCH"
        return {"success": True, "text": text, "action": action}

    def voice_history(self, user_id: int):
        # Returns voice search queries logged in history
        from app.database.connection import SessionLocal
        db = SessionLocal()
        try:
            # retrieve search histories that are likely voice queries (mocked)
            history = db.query(SearchHistory).filter(SearchHistory.user_id == user_id).limit(5).all()
            return [{"id": h.id, "query": h.query, "created_at": h.created_at} for h in history]
        finally:
            db.close()

    def trending_voice_queries(self):
        return ["wireless earphone", "split air conditioner", "running shoes"]

    def voice_assistant(self, text: str):
        # AI voice assistant response
        cmd = text.lower()
        if "hello" in cmd or "hi" in cmd:
            reply = "Hello! How can I help you find products today?"
        elif "price" in cmd:
            reply = "I can help you predict and track price drops. Ask me for price trends of any product!"
        else:
            reply = f"I heard you say '{text}'. I am searching our e-commerce catalog for matching products."
        return {"text": text, "response": reply}

    def health(self):
        return {"status": "healthy", "service": "voice_search_service"}
