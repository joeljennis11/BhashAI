"""
BhashAI Visual Flashcards Generator
Generates bilingual digital and printable flashcards with Santali Ol Chiki and audio playback.
"""

import logging
from typing import Dict, Any, List, Optional
from backend.services.translation_service import TranslationService
from backend.services.santali_tts import SantaliTTSService

logger = logging.getLogger("bhashai.flashcards")


class FlashcardGenerator:
    """
    Generates flashcards from educational material vocabulary.
    """
    _instance: Optional['FlashcardGenerator'] = None

    def __init__(self):
        self._flashcards_store: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def get_instance(cls) -> 'FlashcardGenerator':
        if cls._instance is None:
            cls._instance = FlashcardGenerator()
        return cls._instance

    def generate_flashcards(self, educational_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates flashcard items from extracted vocabulary with translations and audio URLs.
        """
        topic = educational_content.get("topic", "FLN Lesson")
        vocab = educational_content.get("vocabulary", [])
        trans_service = TranslationService.get_instance()
        tts_service = SantaliTTSService.get_instance()

        cards: List[Dict[str, Any]] = []

        # Standard Santali mappings for common classroom FLN fruits
        standard_santali = {
            "आम": ("ᱩᱞ", "Ul"),
            "सेब": ("ᱥᱮᱣ", "Sew"),
            "केला": ("ᱠᱟᱭᱨᱟ", "Kayra"),
            "अंगूर": ("ᱟᱝᱜᱩᱨ", "Angur"),
            "संतरा": ("ᱠᱚᱢᱞᱟ", "Komla"),
            "अमरूद": ("ᱟᱢᱨᱩᱫ", "Amrud"),
            "पेड़": ("ᱫᱟᱨᱮ", "Dare"),
            "पत्ता": ("ᱥᱟᱠᱟᱢ", "Sakam"),
            "फूल": ("ᱵᱟᱦᱟ", "Baha"),
        }

        card_id = 1
        for item in vocab:
            w_hi = item.get("word_hindi", "")
            icon = item.get("icon", "📚")
            concept = item.get("word_english", w_hi)

            if not w_hi:
                continue

            if w_hi in standard_santali:
                w_sat, phonetic = standard_santali[w_hi]
            else:
                try:
                    res = trans_service.translate(w_hi, src_lang="hin_Deva", tgt_lang="sat_Olck", lesson_topic=topic)
                    w_sat = res.get("translation", w_hi)
                    phonetic = ""
                except Exception:
                    w_sat = w_hi
                    phonetic = ""

            # Synthesize audio on demand or retrieve cache
            audio_url = None
            try:
                audio_res = tts_service.synthesize(w_sat)
                audio_url = audio_res.get("audio_url")
            except Exception:
                pass

            cards.append({
                "id": card_id,
                "hindi_word": w_hi,
                "santali_word": w_sat,
                "phonetic": phonetic,
                "concept": concept.capitalize(),
                "icon": icon,
                "example_hindi": f"यह एक {w_hi} है।",
                "example_santali": f"ᱱᱚᱣᱟ ᱫᱚ {w_sat} ᱠᱟᱱᱟ ᱾",
                "audio_url": audio_url
            })
            card_id += 1

        return cards
