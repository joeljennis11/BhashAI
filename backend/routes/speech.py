"""
BhashAI Speech Route
Handles Hindi speech-to-text transcription via Whisper.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional

from backend.services.speech_to_text import SpeechToTextService
from backend.models.response_models import TranscribeResponse

router = APIRouter(prefix="/api/speech", tags=["Speech"])


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form(default="hin_Deva")
):
    """
    Transcribes uploaded audio (WAV, MP3, WebM) into clean Hindi Unicode text.
    """
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        asr_service = SpeechToTextService.get_instance()
        result = asr_service.transcribe(audio_bytes, language="hi")

        return TranscribeResponse(
            text=result["text"],
            language=result["language"],
            duration_seconds=result.get("duration_seconds"),
            confidence=0.95 if result["text"] else 0.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {str(e)}")
