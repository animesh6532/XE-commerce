from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import get_db
from app.middleware.auth import get_current_user
from app.services.voice_search_service import VoiceSearchService

router = APIRouter()

voice_service = VoiceSearchService()


# ---------- Schemas ----------

class VoiceTextRequest(BaseModel):
    text: str


# ---------- Speech to Text ----------

@router.post("/speech-to-text")
async def speech_to_text(
        audio: UploadFile = File(...)
):

    try:
        return voice_service.speech_to_text(
            audio
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------- Voice Product Search ----------

@router.post("/search")
async def voice_search(
        audio: UploadFile = File(...),
        db: Session = Depends(get_db)
):

    try:

        return voice_service.voice_search(
            db=db,
            audio=audio
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------- Search By Text ----------

@router.post("/text-search")
def text_search(
        request: VoiceTextRequest,
        db: Session = Depends(get_db)
):

    return voice_service.text_search(
        db=db,
        text=request.text
    )


# ---------- Voice Recommendations ----------

@router.post("/recommend")
async def voice_recommendation(
        audio: UploadFile = File(...),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):

    return voice_service.voice_recommendation(
        db=db,
        user_id=current_user.id,
        audio=audio
    )


# ---------- Category Search ----------

@router.post("/category")
async def category_search(
        audio: UploadFile = File(...)
):

    return voice_service.category_search(
        audio
    )


# ---------- Voice Commands ----------

@router.post("/command")
def voice_command(
        request: VoiceTextRequest
):

    return voice_service.voice_command(
        request.text
    )


# ---------- Search History ----------

@router.get("/history")
def voice_history(
        current_user=Depends(get_current_user)
):

    return voice_service.voice_history(
        current_user.id
    )


# ---------- Trending Queries ----------

@router.get("/trending")
def trending_voice_queries():

    return voice_service.trending_voice_queries()


# ---------- AI Assistant ----------

@router.post("/assistant")
def voice_assistant(
        request: VoiceTextRequest
):

    return voice_service.voice_assistant(
        request.text
    )


# ---------- Health Check ----------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "voice_search"
    }