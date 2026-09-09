"""
Unit tests for BhashAI Conversation Context Manager
"""

import unittest
from backend.services.context_manager import ConversationContextManager


class TestContextManager(unittest.TestCase):

    def setUp(self):
        self.mgr = ConversationContextManager.get_instance()
        self.mgr.clear_context()

    def test_01_add_turn_and_retrieve(self):
        self.mgr.add_turn("आज हम फलों के बारे में सीखेंगे।")
        recent = self.mgr.get_recent_sentences()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], "आज हम फलों के बारे में सीखेंगे।")

    def test_02_max_history_sliding_window(self):
        self.mgr.add_turn("वाक्य 1")
        self.mgr.add_turn("वाक्य 2")
        self.mgr.add_turn("वाक्य 3")
        self.mgr.add_turn("वाक्य 4")
        recent = self.mgr.get_recent_sentences()
        # Max history is 3
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent, ["वाक्य 2", "वाक्य 3", "वाक्य 4"])

    def test_03_dynamic_topic_inference_fruits(self):
        self.mgr.add_turn("आज हम फलों के बारे में सीखेंगे।")
        summary = self.mgr.get_context_summary()
        self.assertEqual(summary["current_topic"], "Fruits")

    def test_04_explicit_topic_override(self):
        self.mgr.add_turn("यह एक आम है।", explicit_topic="FLN Grade 1")
        summary = self.mgr.get_context_summary()
        self.assertEqual(summary["current_topic"], "FLN Grade 1")

    def test_05_format_context_prefix(self):
        self.mgr.add_turn("आज हम फलों के बारे में सीखेंगे।")
        prefix = self.mgr.format_context_prefix()
        self.assertIn("प्रसंग: Fruits", prefix)
        self.assertIn("पूर्व वाक्य:", prefix)

    def test_06_clear_context(self):
        self.mgr.add_turn("परीक्षण वाक्य")
        self.mgr.clear_context()
        recent = self.mgr.get_recent_sentences()
        self.assertEqual(len(recent), 0)
        self.assertIsNone(self.mgr.get_context_summary()["current_topic"])


if __name__ == "__main__":
    unittest.main()
