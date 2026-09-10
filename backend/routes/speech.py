"""
BhashAI Speech Route
Handles Hindi speech-to-text transcription via Whisper.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.speech_to_text import SpeechToTextService
from backend.models.response_models import TranscribeResponse

router = APIRouter(
    prefix="/api/speech",
    tags=["Speech"]
)


@router.post(
    "/transcribe",
    response_model=TranscribeResponse
)
async def transcribe_audio(
    file: UploadFile = File(...)
):
    """
    Transcribes uploaded audio into Hindi Devanagari text.
    """

    try:
        audio_bytes = await file.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded audio file is empty."
            )

        asr_service = SpeechToTextService.get_instance(
            model_size="small"
        )

        result = asr_service.transcribe(
            audio_bytes,
            language="hi"
        )

        text = result.get("text", "").strip()

        return TranscribeResponse(
            text=text,
            language="hin_Deva",
            duration_seconds=result.get(
                "duration_seconds"
            ),
            confidence=0.95 if text else 0.0
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Speech recognition error: {str(e)}"
        )