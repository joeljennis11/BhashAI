"""
BhashAI Translation Route
Handles context-aware Hindi -> Santali Ol Chiki translation and voice-to-voice translation.
"""

import time
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List

from backend.models.request_models import TranslationRequest
from backend.models.response_models import TranslationResponse, VoiceTranslationResponse
from backend.services.translation_service import TranslationService
from backend.services.speech_to_text import SpeechToTextService
from backend.services.santali_tts import SantaliTTSService
from backend.services.context_manager import ConversationContextManager

router = APIRouter(prefix="/api/translate", tags=["Translation"])


@router.post("", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translates Hindi text to Santali (Ol Chiki) with pedagogical context awareness.
    """
    try:
        service = TranslationService.get_instance()
        result = service.translate(
            text=request.text,
            src_lang=request.source_language,
            tgt_lang=request.target_language,
            context=request.context,
            lesson_topic=request.lesson_topic
        )

        # Optional TTS synthesis url if target is Santali
        audio_url = None
        phonetic_text = None
        if result["translation"] and request.target_language == "sat_Olck":
            try:
                tts = SantaliTTSService.get_instance()
                audio_res = tts.synthesize(result["translation"])
                audio_url = audio_res.get("audio_url")
                phonetic_text = audio_res.get("phonetic_text")
            except Exception:
                pass

        return TranslationResponse(
            translation=result["translation"],
            source_language=result["source_language"],
            target_language=result["target_language"],
            review_required=result["review_required"],
            issues=result["issues"],
            context_applied=result["context_applied"],
            detected_topic=result["detected_topic"],
            audio_url=audio_url,
            phonetic_text=phonetic_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")


@router.post("/voice", response_model=VoiceTranslationResponse)
async def translate_voice(
    file: UploadFile = File(...),
    source_language: str = Form(default="hin_Deva"),
    target_language: str = Form(default="sat_Olck"),
    lesson_topic: Optional[str] = Form(default=None)
):
    """
    Full Voice-to-Voice Pipeline:
    Hindi Audio In -> Hindi ASR -> Context-aware Hindi->Santali Translation -> Santali TTS -> Audio Out
    """
    t_start = time.time()
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Uploaded audio file is empty.")

        # 1. Hindi ASR
        t_asr = time.time()
        asr_service = SpeechToTextService.get_instance(model_size="base")
        asr_res = asr_service.transcribe(audio_bytes, language="hi")
        hindi_text = asr_res["text"]
        asr_latency = round(time.time() - t_asr, 3)

        if not hindi_text:
            raise HTTPException(status_code=400, detail="Speech could not be recognized. Please speak clearly and try again.")

        # 2. Context-aware Translation
        t_trans = time.time()
        trans_service = TranslationService.get_instance()
        trans_res = trans_service.translate(
            text=hindi_text,
            src_lang=source_language,
            tgt_lang=target_language,
            lesson_topic=lesson_topic
        )
        santali_text = trans_res["translation"]
        trans_latency = round(time.time() - t_trans, 3)

        # 3. Santali TTS
        t_tts = time.time()
        tts_service = SantaliTTSService.get_instance()
        tts_res = tts_service.synthesize(santali_text)
        audio_url = tts_res["audio_url"]
        phonetic_text = tts_res.get("phonetic_text")
        tts_latency = round(time.time() - t_tts, 3)

        total_latency = round(time.time() - t_start, 3)

        return VoiceTranslationResponse(
            source_text=hindi_text,
            translation=santali_text,
            audio_url=audio_url,
            source_language=source_language,
            target_language=target_language,
            review_required=trans_res["review_required"],
            issues=trans_res["issues"],
            asr_latency=asr_latency,
            translation_latency=trans_latency,
            tts_latency=tts_latency,
            total_latency=total_latency,
            phonetic_text=phonetic_text
        )


    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice translation pipeline error: {str(e)}")


@router.post("/clear-context")
async def clear_context():
    """Clears the conversational/lesson context buffer."""
    ConversationContextManager.get_instance().clear_context()
    return {"status": "success", "message": "Conversation context cleared."}
