"""
BhashAI Text-to-Speech Route
Synthesizes Santali Ol Chiki text and streams audio WAV files.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from backend.models.request_models import TTSRequest
from backend.models.response_models import TTSResponse
from backend.services.santali_tts import SantaliTTSService

router = APIRouter(prefix="/api/tts", tags=["TTS"])


@router.post("", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """
    Synthesizes Santali text into natural spoken audio.
    """
    try:
        service = SantaliTTSService.get_instance()
        result = service.synthesize(text=request.text, voice_id=request.voice_id or "santali_v1")

        return TTSResponse(
            audio_url=result["audio_url"],
            duration_seconds=result["duration_seconds"],
            sample_rate=result["sample_rate"],
            channels=result["channels"],
            cached=result["cached"],
            phonetic_text=result.get("phonetic_text")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech synthesis error: {str(e)}")


@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    Streams generated audio file (MP3 or WAV) to client or Android player.
    """
    audio_path = Path("generated/audio") / filename
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found.")

    media_type = "audio/mpeg" if filename.endswith(".mp3") else "audio/wav"

    return FileResponse(
        path=str(audio_path),
        media_type=media_type,
        filename=filename
    )

