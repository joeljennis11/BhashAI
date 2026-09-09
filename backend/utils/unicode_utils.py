"""
BhashAI Unicode Utilities
Provides rigorous Unicode cleaning, script detection, mojibake repair,
and linguistic quality validation for Hindi (Devanagari) and Santali (Ol Chiki).
"""

import re
import unicodedata
from typing import Tuple, List

# Unicode Code Ranges
DEVANAGARI_RANGE = (0x0900, 0x097F)
OL_CHIKI_RANGE = (0x1C50, 0x1C7F)

# Common Ol Chiki Characters and Punctuation
OL_CHIKI_DANDA = "\u1C7E"       # ᱾ (Mucad / single punctuation)
OL_CHIKI_DOUBLE_DANDA = "\u1C7F" # ᱿ (Double mucad)


def clean_unicode(text: str) -> str:
    """
    Normalizes text to Unicode NFC and strips unprintable/control characters
    except standard whitespace.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", str(text))
    # Remove control characters except tab and newline
    cleaned = "".join(
        ch for ch in text if ch in "\n\r\t " or unicodedata.category(ch)[0] != "C"
    )
    # Collapse multiple consecutive whitespace characters (spaces, tabs, newlines)
    return re.sub(r"\s+", " ", cleaned).strip()


def fix_mojibake(text: str) -> str:
    """
    Detects and corrects common encoding corruption (e.g. UTF-8 misinterpreted as latin1 or cp1252),
    such as 'à¤¬à¤š...'.
    """
    if not text:
        return ""
    # Common Mojibake marker in Devanagari UTF-8 bytes read as cp1252 / latin-1: 'à¤', 'à¥'
    if "à¤" in text or "à¥" in text or "á´" in text or "áµ" in text:
        try:
            # Re-encode as latin1 and decode as utf-8
            recovered = text.encode("latin-1").decode("utf-8")
            return clean_unicode(recovered)
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                recovered = text.encode("cp1252").decode("utf-8")
                return clean_unicode(recovered)
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
    return clean_unicode(text)


def has_script(text: str, start: int, end: int) -> bool:
    """Checks if any non-whitespace character in text falls within [start, end]."""
    return any(start <= ord(ch) <= end for ch in text)


def is_devanagari(text: str) -> bool:
    """Checks if text contains Devanagari script characters."""
    return has_script(text, DEVANAGARI_RANGE[0], DEVANAGARI_RANGE[1])


def is_ol_chiki(text: str) -> bool:
    """Checks if text contains Santali Ol Chiki script characters."""
    return has_script(text, OL_CHIKI_RANGE[0], OL_CHIKI_RANGE[1])


def ol_chiki_character_ratio(text: str) -> float:
    """Calculates the proportion of alphabetic characters that are Ol Chiki."""
    alpha_chars = [ch for ch in text if ch.isalpha()]
    if not alpha_chars:
        return 0.0
    ol_chiki_count = sum(1 for ch in alpha_chars if OL_CHIKI_RANGE[0] <= ord(ch) <= OL_CHIKI_RANGE[1])
    return ol_chiki_count / len(alpha_chars)


def normalize_ol_chiki(text: str) -> str:
    """
    Normalizes Ol Chiki text:
    - Standardizes Latin/Devanagari danda to Ol Chiki Mucad (᱾)
    - Replaces double pipes/dandas with double Ol Chiki Mucad (᱿)
    - Normalizes punctuation spacing
    """
    if not text:
        return ""
    text = clean_unicode(text)
    # Standardize full stops and Devanagari dandas after Ol Chiki letters to Ol Chiki danda
    text = text.replace("||", OL_DOUBLE_DANDA if 'OL_DOUBLE_DANDA' in globals() else OL_CHIKI_DOUBLE_DANDA)
    text = text.replace("॥", OL_CHIKI_DOUBLE_DANDA)
    text = text.replace("|", OL_CHIKI_DANDA)
    text = text.replace("।", OL_CHIKI_DANDA)
    # If text is primarily Ol Chiki, trailing periods become ᱾
    if is_ol_chiki(text):
        text = re.sub(r"\.(?=\s|$)", OL_CHIKI_DANDA, text)
    # Punctuation spacing cleanup
    text = re.sub(rf"\s+({re.escape(OL_CHIKI_DANDA)}|{re.escape(OL_CHIKI_DOUBLE_DANDA)})", r"\1", text)
    text = re.sub(rf"({re.escape(OL_CHIKI_DANDA)}|{re.escape(OL_CHIKI_DOUBLE_DANDA)})(?=[^\s])", r"\1 ", text)
    return text.strip()


def validate_translation_quality(
    source_text: str,
    target_text: str,
    src_lang: str = "hin_Deva",
    tgt_lang: str = "sat_Olck",
) -> Tuple[bool, List[str]]:
    """
    Validates translation output against linguistic quality and safety checks.
    Returns:
        (review_required: bool, issues: List[str])
    """
    issues: List[str] = []
    
    clean_src = clean_unicode(source_text)
    clean_tgt = clean_unicode(target_text)

    # 1. Empty check
    if not clean_tgt:
        return True, ["Target translation is empty."]

    # 2. Excessively short check relative to source
    src_tokens = clean_src.split()
    tgt_tokens = clean_tgt.split()
    if len(src_tokens) >= 3 and len(tgt_tokens) == 0:
        issues.append("Translation is missing tokens.")
    elif len(src_tokens) >= 5 and len(tgt_tokens) <= 1:
        issues.append("Translation is suspiciously abbreviated.")

    # 3. Repeated token check (hallucination loop)
    if len(tgt_tokens) >= 4:
        for i in range(len(tgt_tokens) - 2):
            if tgt_tokens[i] == tgt_tokens[i + 1] == tgt_tokens[i + 2]:
                issues.append(f"Repetition detected: token '{tgt_tokens[i]}' repeated consecutively.")
                break

    # 4. Target script check
    if tgt_lang == "sat_Olck":
        ratio = ol_chiki_character_ratio(clean_tgt)
        if ratio < 0.3 and any(ch.isalpha() for ch in clean_tgt):
            # Target should be in Ol Chiki; check if it mistakenly remained in Devanagari or Latin
            if is_devanagari(clean_tgt):
                issues.append("Translation returned Devanagari script instead of expected Ol Chiki.")
            else:
                issues.append("Translation does not match expected Ol Chiki script.")

    # 5. Untranslated echo check
    if clean_src.strip() == clean_tgt.strip() and src_lang != tgt_lang:
        issues.append("Source text returned untranslated.")

    review_required = len(issues) > 0
    return review_required, issues
