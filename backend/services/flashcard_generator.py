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

    def get_default_flashcards(self) -> List[Dict[str, Any]]:
        """
        Returns a rich set of starter vocabulary flashcards without emojis.
        """
        default_deck = [
            {
                "hindi": "आम",
                "santali": "ᱩᱞ",
                "phonetic": "Ul",
                "concept": "Mango",
                "category": "Fruits",
                "ex_hi": "यह एक आम है।",
                "ex_sat": "ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾"
            },
            {
                "hindi": "सेब",
                "santali": "ᱥᱮᱣ",
                "phonetic": "Sew",
                "concept": "Apple",
                "category": "Fruits",
                "ex_hi": "सेब लाल रंग का होता है।",
                "ex_sat": "ᱥᱮᱣ ᱫᱚ ᱟᱨᱟᱜ ᱜᱮᱭᱟ ᱾"
            },
            {
                "hindi": "केला",
                "santali": "ᱠᱟᱭᱨᱟ",
                "phonetic": "Kayra",
                "concept": "Banana",
                "category": "Fruits",
                "ex_hi": "केला मीठा होता है।",
                "ex_sat": "ᱠᱟᱭᱨᱟ ᱫᱚ ᱦᱮᱲᱮᱢ ᱜᱮᱭᱟ ᱾"
            },
            {
                "hindi": "एक",
                "santali": "ᱢᱤᱫ",
                "phonetic": "Mid",
                "concept": "One",
                "category": "Numbers",
                "ex_hi": "टोकरी में एक फल है।",
                "ex_sat": "ᱴᱩᱠᱨᱤ ᱨᱮ ᱢᱤᱫ ᱡᱚ ᱢᱮᱱᱟᱜ-ᱟ ᱾"
            },
            {
                "hindi": "दो",
                "santali": "ᱵᱟᱨ",
                "phonetic": "Bar",
                "concept": "Two",
                "category": "Numbers",
                "ex_hi": "दो बच्चे पढ़ रहे हैं।",
                "ex_sat": "ᱵᱟᱨ ᱜᱤᱫᱽᱨᱟᱹ ᱠᱤᱱ ᱯᱟᱲᱦᱟᱣᱜ ᱠᱟᱱᱟ ᱾"
            },
            {
                "hindi": "पेड़",
                "santali": "ᱫᱟᱨᱮ",
                "phonetic": "Dare",
                "concept": "Tree",
                "category": "Nature",
                "ex_hi": "पेड़ पर हरे पत्ते हैं।",
                "ex_sat": "ᱫᱟᱨᱮ ᱨᱮ ᱦᱟᱹᱨᱭᱟᱹᱲ ᱥᱟᱠᱟᱢ ᱢᱮᱱᱟᱜ-ᱟ ᱾"
            },
            {
                "hindi": "किताब",
                "santali": "ᱯᱩᱛᱷᱤ",
                "phonetic": "Puthi",
                "concept": "Book",
                "category": "Classroom",
                "ex_hi": "अपनी किताब खोलिए।",
                "ex_sat": "ᱟᱢᱟᱜ ᱯᱩᱛᱷᱤ ᱡᱷᱤᱡᱽ ᱢᱮ ᱾"
            },
            {
                "hindi": "नमस्ते",
                "santali": "ᱡᱚᱦᱟᱨ",
                "phonetic": "Johar",
                "concept": "Greetings",
                "category": "Phrases",
                "ex_hi": "नमस्ते, आप सब कैसे हैं?",
                "ex_sat": "ᱡᱚᱦᱟᱨ, ᱟᱯᱮ ᱪᱮᱫ ᱞᱮᱠᱟ ᱢᱮᱱᱟᱜ ᱯᱮᱭᱟ?"
            }
        ]

        tts_service = SantaliTTSService.get_instance()
        cards = []
        for idx, item in enumerate(default_deck, 1):
            audio_url = None
            try:
                res = tts_service.synthesize(item["santali"])
                audio_url = res.get("audio_url")
            except Exception:
                pass

            cards.append({
                "id": idx,
                "hindi_word": item["hindi"],
                "santali_word": item["santali"],
                "phonetic": item["phonetic"],
                "concept": item["concept"],
                "icon": item["category"],
                "example_hindi": item["ex_hi"],
                "example_santali": item["ex_sat"],
                "audio_url": audio_url
            })
        return cards

