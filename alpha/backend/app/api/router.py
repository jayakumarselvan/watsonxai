from fastapi import APIRouter
from app.api.audio import audio_summarizer


api_router = APIRouter()
api_router.include_router(audio_summarizer.router, prefix="/api/audio")
