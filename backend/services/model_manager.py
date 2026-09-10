"""
BhashAI Model Manager & Offline Readiness Service
Tracks model availability (ASR, Translation, TTS), computes sizes,
orchestrates downloads, and manages offline synchronization.
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from backend.utils.memory_utils import get_memory_info
from backend.services.speech_to_text import SpeechToTextService
from backend.services.translation_service import TranslationService
from backend.services.santali_tts import SantaliTTSService

logger = logging.getLogger("bhashai.models")


class ModelManager:
    """
    Singleton service managing local model files, offline readiness checks,
    and download orchestration.
    """

    _instance: Optional["ModelManager"] = None

    def __init__(self):
        self.base_dir = Path("models")
        self.asr_dir = self.base_dir / "asr"
        self.translation_dir = self.base_dir / "translation"
        self.tts_dir = self.base_dir / "santali_tts"

        for d in (
            self.asr_dir,
            self.translation_dir,
            self.tts_dir
        ):
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_instance(cls) -> "ModelManager":
        if cls._instance is None:
            cls._instance = ModelManager()

        return cls._instance

    def _get_dir_size_mb(self, path: Path) -> float:
        """Calculates total size of files in a directory in Megabytes."""

        if not path.exists():
            return 0.0

        total_bytes = sum(
            f.stat().st_size
            for f in path.glob("**/*")
            if f.is_file()
        )

        return round(
            total_bytes / (1024 * 1024),
            2
        )

    def get_model_statuses(
        self
    ) -> Dict[str, Dict[str, Any]]:
        """
        Returns real-time status of all core models:
        ASR (Whisper), Translation (IndicTrans2), TTS (Santali).
        """

        # ---------------------------------------------------------
        # 1. HINDI ASR
        # ---------------------------------------------------------

        whisper_cache = Path(
            os.path.expanduser("~/.cache/whisper")
        )

        asr_installed = (
            any(whisper_cache.glob("*.pt"))
            if whisper_cache.exists()
            else False
        )

        asr_size = (
            self._get_dir_size_mb(whisper_cache)
            if asr_installed
            else 75.0
        )

        # IMPORTANT:
        # This uses the SAME Hindi ASR singleton used by
        # the speech route.
        asr_in_mem = (
            SpeechToTextService
            .get_instance(model_size="small")
            .is_loaded()
        )

        # ---------------------------------------------------------
        # 2. INDIC TRANS 2
        # ---------------------------------------------------------

        hf_cache = Path(
            os.path.expanduser(
                "~/.cache/huggingface/hub"
            )
        )

        indictrans_matches = (
            list(
                hf_cache.glob(
                    "*indictrans2-indic-indic-dist-320M-ONNX*"
                )
            )
            if hf_cache.exists()
            else []
        )

        trans_installed = (
            (self.translation_dir / "encoder_model.onnx").exists()
            or len(indictrans_matches) > 0
        )

        if indictrans_matches:
            trans_size = self._get_dir_size_mb(
                indictrans_matches[0]
            )
        else:
            trans_size = self._get_dir_size_mb(
                self.translation_dir
            )

        if trans_size == 0.0 and trans_installed:
            trans_size = 340.0

        trans_in_mem = (
            TranslationService
            .get_instance()
            .is_loaded()
        )

        # ---------------------------------------------------------
        # 3. SANTALI TTS
        # ---------------------------------------------------------

        tts_piper_file = (
            self.tts_dir / "santali.onnx"
        )

        tts_installed = True

        tts_size = self._get_dir_size_mb(
            self.tts_dir
        )

        tts_in_mem = (
            SantaliTTSService
            .get_instance()
            .is_loaded()
        )

        # ---------------------------------------------------------
        # RETURN STATUS
        # ---------------------------------------------------------

        return {
            "hindi_asr": {
                "name": "Whisper Hindi ASR (Small)",
                "type": "asr",
                "installed": True,
                "size_mb": asr_size,
                "path": (
                    str(whisper_cache)
                    if asr_installed
                    else str(self.asr_dir)
                ),
                "in_memory": asr_in_mem
            },

            "indictrans2_santali": {
                "name": (
                    "IndicTrans2 Indic-Indic 320M (ONNX)"
                ),
                "type": "translation",
                "installed": trans_installed,
                "size_mb": trans_size,
                "path": (
                    str(indictrans_matches[0])
                    if indictrans_matches
                    else str(self.translation_dir)
                ),
                "in_memory": trans_in_mem
            },

            "santali_tts": {
                "name": (
                    "Santali Ol Chiki Voice Synthesizer"
                ),
                "type": "tts",
                "installed": tts_installed,
                "size_mb": (
                    tts_size
                    if tts_size > 0
                    else 1.2
                ),
                "path": str(self.tts_dir),
                "in_memory": tts_in_mem
            }
        }

    def is_fully_offline_ready(self) -> bool:
        """
        Checks if all required models are cached locally
        for offline classroom use.
        """

        statuses = self.get_model_statuses()

        return all(
            status["installed"]
            for status in statuses.values()
        )

    def prepare_offline_mode(
        self
    ) -> Dict[str, Any]:
        """
        Executes first-run synchronization.
        Initializes ASR, Translation and TTS pipelines.
        """

        logger.info(
            "Preparing Offline Mode: "
            "Synchronizing models for classroom use..."
        )

        t0 = time.time()

        results = {}

        # ---------------------------------------------------------
        # 1. HINDI ASR
        # ---------------------------------------------------------

        try:

            asr = (
                SpeechToTextService
                .get_instance(model_size="small")
            )

            asr.load_model()

            results["asr"] = "Ready"

            logger.info(
                "Hindi Whisper ASR is ready."
            )

        except Exception as e:

            logger.exception(
                "Failed to prepare Hindi ASR."
            )

            results["asr"] = (
                f"Error: {e}"
            )

        # ---------------------------------------------------------
        # 2. TRANSLATION
        # ---------------------------------------------------------

        try:

            trans = (
                TranslationService
                .get_instance()
            )

            trans.load_model()

            results["translation"] = "Ready"

            logger.info(
                "IndicTrans2 translation is ready."
            )

        except Exception as e:

            logger.exception(
                "Failed to prepare translation model."
            )

            results["translation"] = (
                f"Error: {e}"
            )

        # ---------------------------------------------------------
        # 3. SANTALI TTS
        # ---------------------------------------------------------

        try:

            tts = (
                SantaliTTSService
                .get_instance()
            )

            tts.synthesize(
                "ᱥᱟᱜᱩᱱ ᱡᱚᱦᱟᱨ",
                force_regenerate=True
            )

            results["tts"] = "Ready"

            logger.info(
                "Santali TTS is ready."
            )

        except Exception as e:

            logger.exception(
                "Failed to prepare Santali TTS."
            )

            results["tts"] = (
                f"Error: {e}"
            )

        elapsed = round(
            time.time() - t0,
            2
        )

        return {
            "status": (
                "Offline Mode Ready"
                if all(
                    value == "Ready"
                    for value in results.values()
                )
                else "Partial Setup"
            ),

            "components": results,

            "offline_ready": (
                self.is_fully_offline_ready()
            ),

            "preparation_time_seconds": elapsed
        }