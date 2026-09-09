"""
Unit tests for BhashAI Santali Text-to-Speech (TTS) Service
Contains 10 verification tests.
"""

import os
import unittest
from pathlib import Path

from backend.services.santali_tts import SantaliTTSService
from backend.utils.audio_utils import get_wav_metadata


class TestSantaliTTS(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tts = SantaliTTSService.get_instance()

    def test_01_empty_text_error(self):
        """TTS must raise error on empty text input."""
        with self.assertRaises(ValueError):
            self.tts.synthesize("")

    def test_02_whitespace_text_error(self):
        """TTS must raise error on whitespace-only input."""
        with self.assertRaises(ValueError):
            self.tts.synthesize("   \n\t  ")

    def test_03_single_word_synthesis(self):
        """Synthesize single Ol Chiki word (ᱩᱞ = Mango)."""
        res = self.tts.synthesize("ᱩᱞ")
        self.assertIn("audio_path", res)
        self.assertTrue(os.path.exists(res["audio_path"]))

    def test_04_sentence_synthesis(self):
        """Synthesize full classroom Ol Chiki sentence."""
        res = self.tts.synthesize("ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾")
        self.assertIn("audio_url", res)
        self.assertGreater(res["duration_seconds"], 0.3)

    def test_05_wav_metadata_format(self):
        """Audio must be 16-bit PCM mono with 16000Hz sampling rate."""
        res = self.tts.synthesize("ᱥᱟᱜᱩᱱ ᱡᱚᱦᱟᱨ")
        meta = get_wav_metadata(res["audio_path"])
        self.assertTrue(meta["valid"])
        self.assertEqual(meta["channels"], 1)
        self.assertEqual(meta["sample_rate"], 16000)
        self.assertEqual(meta["bit_depth"], 16)

    def test_06_caching_behavior(self):
        """Subsequent synthesis of same text must return cached=True."""
        text = "ᱥᱟᱱᱛᱟᱲᱤ ᱯᱟᱹᱨᱥᱤ"
        # First pass
        res1 = self.tts.synthesize(text, force_regenerate=True)
        self.assertFalse(res1["cached"])
        # Second pass
        res2 = self.tts.synthesize(text)
        self.assertTrue(res2["cached"])
        self.assertEqual(res1["audio_path"], res2["audio_path"])

    def test_07_punctuation_handling(self):
        """TTS handles Ol Chiki punctuation (᱾ and ᱿) gracefully."""
        res = self.tts.synthesize("ᱚᱞ ᱢᱮ ᱾ ᱯᱟᱲᱦᱟᱣ ᱢᱮ ᱿")
        self.assertTrue(os.path.exists(res["audio_path"]))
        self.assertGreater(res["duration_seconds"], 0.5)

    def test_08_duration_scaling(self):
        """Longer sentences must have greater audio duration than single words."""
        short_res = self.tts.synthesize("ᱩᱞ")
        long_res = self.tts.synthesize("ᱛᱮᱦᱮᱧ ᱫᱚ ᱵᱚᱱ ᱡᱚ ᱵᱟᱵᱚᱛ ᱵᱚᱱ ᱪᱮᱫ-ᱟ ᱾ ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾", force_regenerate=True)
        self.assertGreater(long_res["duration_seconds"], short_res["duration_seconds"])

    def test_09_multiple_fruits_vocabulary(self):
        """Synthesizes multiple FLN fruits without crashing."""
        fruits = ["ᱩᱞ", "ᱥᱮᱣ", "ᱠᱟᱭᱨᱟ", "ᱟᱝᱜᱩᱨ"]
        for f in fruits:
            res = self.tts.synthesize(f)
            self.assertTrue(os.path.exists(res["audio_path"]))

    def test_10_memory_lifecycle_unload(self):
        """Model can be unloaded cleanly to preserve memory."""
        self.tts.unload_model()
        self.assertFalse(self.tts.is_loaded())


if __name__ == "__main__":
    unittest.main()
