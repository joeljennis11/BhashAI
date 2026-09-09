"""
BhashAI Language Configuration Architecture
Defines the modular configuration for all supported and planned vernacular languages.
Supports future language expansion (Ho, Mundari) without structural changes.
"""

from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field


class LanguageConfig(BaseModel):
    language_name: str
    language_code: str          # FLORES-200 code e.g. "sat_Olck", "hin_Deva"
    script: str                 # "Ol Chiki", "Devanagari", "Warang Citi", etc.
    script_code: str            # "Olck", "Deva", "Wara"
    translation_model: str      # Model ID or local path
    asr_model: Optional[str] = None
    tts_model: Optional[str] = None
    tokenizer: Optional[str] = None
    supported: bool = True
    description: str = ""
    font_asset: Optional[str] = None


# Language Registry
SUPPORTED_LANGUAGES: Dict[str, LanguageConfig] = {
    "hin_Deva": LanguageConfig(
        language_name="Hindi",
        language_code="hin_Deva",
        script="Devanagari",
        script_code="Deva",
        translation_model="ai4bharat/indictrans2-indic-indic-dist-320M",
        asr_model="openai/whisper-tiny",
        tts_model=None,
        tokenizer="ai4bharat/indictrans2-indic-indic-dist-320M",
        supported=True,
        description="Source classroom language for FLN instruction in Hindi belt.",
        font_asset=None
    ),
    "sat_Olck": LanguageConfig(
        language_name="Santali",
        language_code="sat_Olck",
        script="Ol Chiki",
        script_code="Olck",
        translation_model="ai4bharat/indictrans2-indic-indic-dist-320M",
        asr_model=None,
        tts_model="models/santali_tts/santali_piper.onnx",
        tokenizer="ai4bharat/indictrans2-indic-indic-dist-320M",
        supported=True,
        description="Primary target vernacular language spoken across Jharkhand, Odisha, and West Bengal.",
        font_asset="fonts/NotoSansOlChiki-Regular.ttf"
    ),
    # Extensible architecture for future tribal languages
    "hoc_Deva": LanguageConfig(
        language_name="Ho",
        language_code="hoc_Deva",
        script="Devanagari / Warang Citi",
        script_code="Deva",
        translation_model="planned",
        asr_model=None,
        tts_model=None,
        tokenizer=None,
        supported=False,
        description="Tribal language of the Ho people in Jharkhand and Odisha (future extension).",
        font_asset=None
    ),
    "unr_Deva": LanguageConfig(
        language_name="Mundari",
        language_code="unr_Deva",
        script="Devanagari / Mundari Bani",
        script_code="Deva",
        translation_model="planned",
        asr_model=None,
        tts_model=None,
        tokenizer=None,
        supported=False,
        description="Austroasiatic tribal language spoken by Munda people in eastern India (future extension).",
        font_asset=None
    ),
}


def get_language_config(code: str) -> Optional[LanguageConfig]:
    """Retrieves language configuration by FLORES code."""
    return SUPPORTED_LANGUAGES.get(code)


def list_supported_pairs() -> List[Dict[str, Any]]:
    """Lists currently active translation pairs."""
    return [
        {
            "source": "hin_Deva",
            "source_name": "Hindi (हिन्दी)",
            "target": "sat_Olck",
            "target_name": "Santali (ᱥᱟᱱᱛᱟᱲᱤ)",
            "target_script": "Ol Chiki (ᱚᱞ ᱪᱤᱠᱤ)",
            "supported": True
        }
    ]
