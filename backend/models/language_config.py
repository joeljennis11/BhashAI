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
        asr_model="openai/whisper-base",
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
        asr_model="facebook/mms-1b-all",
        tts_model="gtts-phonetic-santali",
        tokenizer="ai4bharat/indictrans2-indic-indic-dist-320M",
        supported=True,
        description="Primary target vernacular language spoken across Jharkhand, Odisha, and West Bengal.",
        font_asset="fonts/NotoSansOlChiki-Regular.ttf"
    ),
    "hoc_Wara": LanguageConfig(
        language_name="Ho",
        language_code="hoc_Wara",
        script="Warang Chiti / Devanagari",
        script_code="Wara",
        translation_model="facebook/mms-1b-all",
        asr_model="facebook/mms-1b-fl102",
        tts_model="facebook/mms-tts-hoc",
        tokenizer="facebook/mms-1b-all",
        supported=True,
        description="North Munda language of the Ho people in Kolhan division (Jharkhand) and Mayurbhanj (Odisha).",
        font_asset=None
    ),
    "unr_Deva": LanguageConfig(
        language_name="Mundari",
        language_code="unr_Deva",
        script="Devanagari / Mundari Bani",
        script_code="Deva",
        translation_model="facebook/mms-1b-all",
        asr_model="facebook/mms-1b-fl102",
        tts_model="facebook/mms-tts-unr",
        tokenizer="facebook/mms-1b-all",
        supported=True,
        description="Austroasiatic Munda language spoken by Munda community in Ranchi, Khunti, and surrounding plateau.",
        font_asset=None
    ),
}

# Comparative Lexicon across the three Sister Munda Languages
MUNDA_COMPARATIVE_LEXICON: Dict[str, Dict[str, str]] = {
    "नमस्ते": {"hindi": "नमस्ते", "santali": "ᱡᱚᱦᱟᱨ (Johar)", "ho": "ᱡᱚᱦᱟᱨ (Johar)", "mundari": "ᱡᱚᱦᱟᱨ (Johar)"},
    "आम": {"hindi": "आम", "santali": "ᱩᱞ (Ul)", "ho": "ᱩᱞᱤ (Uli)", "mundari": "ᱩᱞᱤ (Uli)"},
    "सेब": {"hindi": "सेब", "santali": "ᱥᱮᱣ (Sew)", "ho": "ᱥᱮᱣ (Sew)", "mundari": "ᱥᱮᱣ (Sew)"},
    "केला": {"hindi": "केला", "santali": "ᱠᱟᱭᱨᱟ (Kayra)", "ho": "ᱠᱟᱫᱟᱞ (Kadal)", "mundari": "ᱠᱟᱫᱟᱞ (Kadal)"},
    "पानी": {"hindi": "पानी", "santali": "ᱫᱟᱜ (Dak')", "ho": "ᱫᱟᱜ (Da')", "mundari": "ᱫᱟᱜ (Da')"},
    "पेड़": {"hindi": "पेड़", "santali": "ᱫᱟᱨᱮ (Dare)", "ho": "ᱫᱟᱨᱩ (Daru)", "mundari": "ᱫᱟᱨᱩ (Daru)"},
    "पत्ता": {"hindi": "पत्ता", "santali": "ᱥᱟᱠᱟᱢ (Sakam)", "ho": "ᱥᱟᱠᱟᱢ (Sakam)", "mundari": "ᱥᱟᱠᱟᱢ (Sakam)"},
    "फूल": {"hindi": "फूल", "santali": "ᱵᱟᱦᱟ (Baha)", "ho": "ᱵᱟᱦᱟ (Baha)", "mundari": "ᱵᱟᱦᱟ (Baha)"},
    "किताब": {"hindi": "किताब", "santali": "ᱯᱩᱛᱷᱤ (Puthi)", "ho": "ᱯᱩᱛᱷᱤ (Puthi)", "mundari": "ᱯᱩᱛᱷᱤ (Puthi)"},
    "गाय": {"hindi": "गाय", "santali": "ᱜᱟᱹᱭ (Gại)", "ho": "ᱜᱟᱹᱭ (Gai)", "mundari": "ᱜᱟᱹᱭ (Gai)"},
    "दूध": {"hindi": "दूध", "santali": "ᱛᱳᱣᱟ (Towa)", "ho": "ᱛᱳᱣᱟ (Towa)", "mundari": "ᱛᱳᱣᱟ (Towa)"},
    "एक": {"hindi": "एक", "santali": "ᱢᱤᱫ (Mid)", "ho": "ᱢᱤᱭᱟᱹᱫ (Miyad)", "mundari": "ᱢᱤᱭᱟᱹᱫ (Miyad)"},
    "दो": {"hindi": "दो", "santali": "ᱵᱟᱨ (Bar)", "ho": "ᱵᱟᱨᱤᱭᱟ (Bariya)", "mundari": "ᱵᱟᱨᱤᱭᱟ (Bariya)"},
    "तीन": {"hindi": "तीन", "santali": "ᱯᱮ (Pe)", "ho": "ᱟᱯᱤᱭᱟ (Apiya)", "mundari": "ᱟᱯᱤᱭᱟ (Apiya)"},
}


def get_language_config(code: str) -> Optional[LanguageConfig]:
    """Retrieves language configuration by FLORES code."""
    return SUPPORTED_LANGUAGES.get(code)


def list_supported_pairs() -> List[Dict[str, Any]]:
    """Lists currently active and planned translation pairs."""
    return [
        {
            "source": "hin_Deva",
            "source_name": "Hindi (हिन्दी)",
            "target": "sat_Olck",
            "target_name": "Santali (ᱥᱟᱱᱛᱟᱲᱤ)",
            "target_script": "Ol Chiki (ᱚᱞ ᱪᱤᱠᱤ)",
            "status": "Active (Fully Implemented)"
        },
        {
            "source": "hin_Deva",
            "source_name": "Hindi (हिन्दी)",
            "target": "hoc_Wara",
            "target_name": "Ho (ᱦᱳ)",
            "target_script": "Warang Chiti / Devanagari",
            "status": "Roadmap Stage 1 (Architecture Ready)"
        },
        {
            "source": "hin_Deva",
            "source_name": "Hindi (हिन्दी)",
            "target": "unr_Deva",
            "target_name": "Mundari (ᱢᱩᱱᱰᱟᱨᱤ)",
            "target_script": "Devanagari / Mundari Bani",
            "status": "Roadmap Stage 1 (Architecture Ready)"
        }
    ]

