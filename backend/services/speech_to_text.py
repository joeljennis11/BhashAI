"""
BhashAI Hindi Speech-to-Text (ASR) Service
Utilizes lightweight Whisper model for robust offline Hindi classroom speech recognition.
Guarantees pristine UTF-8 Devanagari output without Unicode corruption.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
import numpy as np

from backend.utils.audio_utils import load_audio_for_asr
from backend.utils.unicode_utils import clean_unicode, fix_mojibake
from backend.utils.memory_utils import MemoryLifecycleManager

logger = logging.getLogger("bhashai.asr")


class SpeechToTextService:
    """
    Singleton service managing Whisper Hindi ASR.
    Loaded lazily, reused across requests, and respects low-memory lifecycle.
    """
    _instance: Optional['SpeechToTextService'] = None

    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size
        self._model = None
        self._is_loading = False

        # Register with memory lifecycle manager
        mem_mgr = MemoryLifecycleManager.get_instance()
        mem_mgr.register_service("asr", self.unload_model)

    @classmethod
    def get_instance(cls, model_size: str = "tiny") -> 'SpeechToTextService':
        if cls._instance is None:
            cls._instance = SpeechToTextService(model_size=model_size)
        return cls._instance

    def is_loaded(self) -> bool:
        """Returns True if the model weights are currently resident in RAM."""
        return self._model is not None

    def load_model(self):
        """Loads Whisper model into memory lazily."""
        if self._model is not None:
            return

        import whisper
        logger.info(f"Loading Whisper Hindi ASR model (size='{self.model_size}')...")
        t0 = time.time()

        # Prepare memory before loading
        MemoryLifecycleManager.get_instance().prepare_for_model("asr")

        # Load model on CPU
        self._model = whisper.load_model(self.model_size, device="cpu")
        MemoryLifecycleManager.get_instance().mark_active("asr")

        logger.info(f"Whisper ASR model loaded in {round(time.time() - t0, 2)}s.")

    def unload_model(self):
        """Releases Whisper model from RAM to satisfy low-memory constraints."""
        if self._model is not None:
            logger.info("Unloading Whisper ASR model from RAM...")
            self._model = None
            MemoryLifecycleManager.get_instance().mark_inactive("asr")

    def transcribe(
        self,
        audio_input: Any,
        language: str = "hi"
    ) -> Dict[str, Any]:
        """
        Transcribes audio (file path, bytes, or numpy array) into clean Hindi Unicode text.
        Returns:
            {
                "text": "आज हम फलों के बारे में सीखेंगे।",
                "language": "hin_Deva",
                "duration_seconds": 2.4,
                "latency_seconds": 0.82
            }
        """
        t0 = time.time()
        self.load_model()

        # Prepare 16kHz float32 audio
        if isinstance(audio_input, np.ndarray):
            audio_samples = audio_input
        else:
            audio_samples = load_audio_for_asr(audio_input, target_sample_rate=16000)

        duration = len(audio_samples) / 16000.0 if len(audio_samples) > 0 else 0.0

        if len(audio_samples) == 0:
            return {
                "text": "",
                "language": "hin_Deva",
                "duration_seconds": 0.0,
                "latency_seconds": round(time.time() - t0, 3)
            }

        # Perform transcription with Whisper CPU settings
        result = self._model.transcribe(
            audio_samples,
            language="hi",
            task="transcribe",
            fp16=False,
            temperature=0.0,
            best_of=1,
            beam_size=1,
            condition_on_previous_text=False
        )

        raw_text = result.get("text", "")

        # Strict Unicode sanitation and mojibake prevention
        safe_hindi_text = fix_mojibake(raw_text)
        safe_hindi_text = clean_unicode(safe_hindi_text)

        latency = round(time.time() - t0, 3)
        logger.info(f"ASR complete in {latency}s: '{safe_hindi_text}'")

        return {
            "text": safe_hindi_text,
            "language": "hin_Deva",
            "duration_seconds": round(duration, 2),
            "latency_seconds": latency
        }
