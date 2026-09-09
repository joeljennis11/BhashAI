"""
Unit tests for BhashAI Unicode Utilities & Quality Control
"""

import unittest
from backend.utils.unicode_utils import (
    clean_unicode,
    fix_mojibake,
    is_devanagari,
    is_ol_chiki,
    ol_chiki_character_ratio,
    normalize_ol_chiki,
    validate_translation_quality
)


class TestUnicodeUtils(unittest.TestCase):

    def test_clean_unicode(self):
        dirty = "  आज \t हम   सीखेंगे। \u200b "
        cleaned = clean_unicode(dirty)
        self.assertEqual(cleaned, "आज हम सीखेंगे।")

    def test_fix_mojibake_devanagari(self):
        # Mojibake string from misinterpreting utf-8 as latin1
        sample_hi = "नमस्ते"
        corrupted = sample_hi.encode("utf-8").decode("latin-1")
        fixed = fix_mojibake(corrupted)
        self.assertEqual(fixed, "नमस्ते")

    def test_is_devanagari(self):
        self.assertTrue(is_devanagari("आज हम फलों के बारे में सीखेंगे।"))
        self.assertFalse(is_devanagari("Hello world"))
        self.assertFalse(is_devanagari("ᱥᱟᱱᱛᱟᱲᱤ"))

    def test_is_ol_chiki(self):
        self.assertTrue(is_ol_chiki("ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾"))
        self.assertFalse(is_ol_chiki("यह एक आम है।"))
        self.assertFalse(is_ol_chiki("English text"))

    def test_ol_chiki_character_ratio(self):
        ratio_full = ol_chiki_character_ratio("ᱥᱟᱱᱛᱟᱲᱤ")
        self.assertEqual(ratio_full, 1.0)
        ratio_zero = ol_chiki_character_ratio("हिन्दी")
        self.assertEqual(ratio_zero, 0.0)

    def test_normalize_ol_chiki_danda(self):
        raw = "ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ |"
        normalized = normalize_ol_chiki(raw)
        self.assertIn("᱾", normalized)
        self.assertNotIn("|", normalized)

    def test_quality_empty_target(self):
        review_req, issues = validate_translation_quality("आज हम सीखेंगे", "")
        self.assertTrue(review_req)
        self.assertIn("Target translation is empty.", issues)

    def test_quality_script_mismatch(self):
        # Target was expected to be sat_Olck, but returned in Devanagari
        review_req, issues = validate_translation_quality("आज हम सीखेंगे", "आज हम सीखेंगे", tgt_lang="sat_Olck")
        self.assertTrue(review_req)
        self.assertTrue(any("Devanagari" in s or "script" in s for s in issues))

    def test_quality_repetition_hallucination(self):
        # Repetition loop
        hallucinated = "ᱩᱞ ᱩᱞ ᱩᱞ ᱩᱞ ᱩᱞ"
        review_req, issues = validate_translation_quality("यह आम है", hallucinated, tgt_lang="sat_Olck")
        self.assertTrue(review_req)
        self.assertTrue(any("Repetition" in s for s in issues))

    def test_quality_valid_translation(self):
        valid_sat = "ᱱᱚᱣᱟ ᱫᱚ ᱢᱤᱫᱴᱟᱝ ᱩᱞ ᱠᱟᱱᱟ ᱾"
        review_req, issues = validate_translation_quality("यह एक आम है।", valid_sat, tgt_lang="sat_Olck")
        self.assertFalse(review_req)
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
