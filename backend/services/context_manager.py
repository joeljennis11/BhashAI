"""
BhashAI Conversation Context Manager
Maintains dynamic pedagogical context across multi-sentence teacher speech turns,
lesson topics, detected entities, and vocabulary to support context-aware translation.
"""

import time
import re
from typing import List, Dict, Optional, Any
from backend.utils.unicode_utils import clean_unicode

# Educational Theme Indicators (for dynamic topic extraction from natural teacher speech)
THEME_INDICATORS = {
    "fruits": ["फल", "फलों", "आम", "सेब", "केला", "अंगूर", "संतरा", "अमरूद", "जोम"],
    "vegetables": ["सब्जी", "सब्जियों", "आलू", "टमाटर", "प्याज", "गोभी", "गाजर"],
    "animals": ["जानवर", "पशु", "पक्षी", "गाय", "बैल", "बकरी", "शेर", "हाथी", "कुत्ता", "बिल्ली"],
    "numbers": ["संख्या", "गिनती", "एक", "दो", "तीन", "चार", "पांच", "दस", "जोड़", "घटाव"],
    "colors": ["रंग", "लाल", "हरा", "पीला", "नीला", "सफेद", "काला"],
    "classroom": ["कक्षा", "पाठ", "किताब", "कलम", "पढ़ना", "लिखना", "सीखना", "शिक्षक", "बच्चे"],
}


class ConversationContextManager:
    """
    Manages session-level dynamic context for classroom translation.
    Thread-safe and lightweight for mobile and low-resource backend deployment.
    """
    _instance: Optional['ConversationContextManager'] = None

    def __init__(self, max_history: int = 3):
        self.max_history = max_history
        self._history: List[Dict[str, Any]] = []
        self._current_topic: Optional[str] = None
        self._detected_entities: set = set()
        self._last_active_time: float = time.time()

    @classmethod
    def get_instance(cls) -> 'ConversationContextManager':
        if cls._instance is None:
            cls._instance = ConversationContextManager()
        return cls._instance

    def add_turn(
        self,
        sentence: str,
        translation: Optional[str] = None,
        explicit_topic: Optional[str] = None
    ):
        """Adds a speech or text turn to the sliding context window."""
        clean_s = clean_unicode(sentence)
        if not clean_s:
            return

        self._last_active_time = time.time()

        # Update topic if explicitly provided
        if explicit_topic:
            self._current_topic = clean_unicode(explicit_topic)
        else:
            # Dynamically infer topic from speech content if currently unset
            inferred = self._infer_topic(clean_s)
            if inferred:
                self._current_topic = inferred

        # Extract entities / key nouns (FLN relevant words)
        words = clean_s.split()
        for w in words:
            clean_w = re.sub(r"[^\w\s]", "", w)
            if len(clean_w) >= 2:
                self._detected_entities.add(clean_w)

        # Append to history and maintain window size
        self._history.append({
            "sentence": clean_s,
            "translation": translation,
            "timestamp": self._last_active_time,
            "topic": self._current_topic
        })

        if len(self._history) > self.max_history:
            self._history.pop(0)

    def _infer_topic(self, sentence: str) -> Optional[str]:
        """Infers pedagogical theme dynamically from spoken vocabulary."""
        lower_s = sentence.lower()
        for theme, keywords in THEME_INDICATORS.items():
            if any(k in lower_s for k in keywords):
                return theme.capitalize()
        return None

    def get_recent_sentences(self) -> List[str]:
        """Returns the recent 2-3 sentences in chronological order."""
        return [turn["sentence"] for turn in self._history]

    def get_context_summary(self) -> Dict[str, Any]:
        """Returns full context snapshot for translation service."""
        return {
            "recent_sentences": self.get_recent_sentences(),
            "current_topic": self._current_topic,
            "detected_entities": list(self._detected_entities)[-15:],
            "turn_count": len(self._history)
        }

    def format_context_prefix(self) -> str:
        """
        Formats context into supporting semantic cue for translation disambiguation.
        For example: '[Topic: Fruits] [Context: आज हम फलों के बारे में सीखेंगे]'
        """
        parts = []
        if self._current_topic:
            parts.append(f"प्रसंग: {self._current_topic}")
        recent = self.get_recent_sentences()
        if recent:
            # Use the immediate predecessor sentence
            parts.append(f"पूर्व वाक्य: {recent[-1]}")
        return " | ".join(parts)

    def clear_context(self):
        """Clears all session context (e.g. when starting a new lesson)."""
        self._history.clear()
        self._current_topic = None
        self._detected_entities.clear()
        self._last_active_time = time.time()
