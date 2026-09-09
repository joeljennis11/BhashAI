"""
Unit tests for BhashAI Hindi to Santali Translation Service
Contains 10 verification tests.
"""

import unittest
from backend.services.translation_service import TranslationService, CompatibleIndicProcessor
from backend.utils.unicode_utils import is_ol_chiki


class TestTranslationService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = TranslationService.get_instance()
        cls.processor = CompatibleIndicProcessor(inference=True)

    def test_01_singleton_instance(self):
        """Service follows singleton pattern."""
        inst2 = TranslationService.get_instance()
        self.assertIs(self.service, inst2)

    def test_02_empty_input_handling(self):
        """Empty input returns review_required=True and empty translation."""
        res = self.service.translate("")
        self.assertEqual(res["translation"], "")
        self.assertTrue(res["review_required"])

    def test_03_processor_prefix(self):
        """CompatibleIndicProcessor correctly adds source and target language tags."""
        pre = self.processor.preprocess("यह एक आम है", src_lang="hin_Deva", tgt_lang="sat_Olck")
        self.assertTrue(pre.startswith("hin_Deva sat_Olck "))
        self.assertIn("यह एक आम है", pre)

    def test_04_processor_digit_normalization(self):
        """Indic digits are translated to standard Arabic digits for tokenization."""
        pre = self.processor.preprocess("५ फल", src_lang="hin_Deva", tgt_lang="sat_Olck")
        self.assertIn("<ID", pre)

    def test_05_processor_postprocess_olchiki(self):
        """Postprocessor cleans and standardizes Ol Chiki text."""
        raw_output = "ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ |"
        post = self.processor.postprocess(raw_output, tgt_lang="sat_Olck")
        self.assertIn("᱾", post)
        self.assertNotIn("|", post)

    def test_06_hindi_translation_returns_valid_structure(self):
        """Translating a Hindi sentence returns expected metadata fields."""
        res = self.service.translate("यह एक आम है।", lesson_topic="Fruits")
        self.assertIn("translation", res)
        self.assertEqual(res["source_language"], "hin_Deva")
        self.assertEqual(res["target_language"], "sat_Olck")
        self.assertIn("review_required", res)
        self.assertIn("latency_seconds", res)

    def test_07_context_awareness_parameter(self):
        """Supplying context sets context_applied flag to True."""
        res = self.service.translate(
            "आम",
            context=["आज हम फलों के बारे में सीखेंगे।"],
            lesson_topic="Fruits"
        )
        self.assertTrue(res["context_applied"])
        self.assertEqual(res["detected_topic"], "Fruits")

    def test_08_multiturn_translation(self):
        """Translating multiple sentences sequential flow succeeds."""
        sentences = [
            "आज हम फलों के बारे में सीखेंगे।",
            "यह एक आम है।",
            "सेब लाल रंग का होता है।"
        ]
        for s in sentences:
            res = self.service.translate(s)
            self.assertIsNotNone(res["translation"])

    def test_09_quality_control_layer_active(self):
        """Quality control flags are returned with translation result."""
        res = self.service.translate("यह सेब है।")
        self.assertIsInstance(res["review_required"], bool)
        self.assertIsInstance(res["issues"], list)

    def test_10_memory_unload(self):
        """Translation service can be unloaded to free memory."""
        self.service.unload_model()
        self.assertFalse(self.service.is_loaded())


if __name__ == "__main__":
    unittest.main()
