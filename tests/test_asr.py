"""
Unit tests for BhashAI Hindi Speech-to-Text (ASR) Service
Contains 10 verification tests.
"""

import unittest
import numpy as np

from backend.services.speech_to_text import SpeechToTextService
from backend.utils.audio_utils import load_audio_for_asr, save_pcm_as_wav


class TestHindiASR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.asr = SpeechToTextService.get_instance(model_size="tiny")

    def test_01_singleton_instance(self):
        """Service follows singleton pattern."""
        inst2 = SpeechToTextService.get_instance()
        self.assertIs(self.asr, inst2)

    def test_02_empty_audio_array(self):
        """Empty audio returns empty string safely."""
        res = self.asr.transcribe(np.zeros(0, dtype=np.float32))
        self.assertEqual(res["text"], "")
        self.assertEqual(res["duration_seconds"], 0.0)

    def test_03_zero_silence_input(self):
        """Pure silence array processes without errors."""
        silence = np.zeros(16000 * 1, dtype=np.float32)  # 1 sec silence
        res = self.asr.transcribe(silence)
        self.assertIn("text", res)
        self.assertEqual(res["language"], "hin_Deva")

    def test_04_synthetic_sine_tone_input(self):
        """Audio sine tone array transcribes without crashes."""
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        tone = (0.5 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)
        res = self.asr.transcribe(tone)
        self.assertIn("latency_seconds", res)
        self.assertGreater(res["latency_seconds"], 0.0)

    def test_05_wav_file_input(self):
        """Transcribe directly from a temporary WAV file."""
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        audio = (0.3 * np.sin(2 * np.pi * 300.0 * t)).astype(np.float32)
        tmp_wav = "sample_materials/temp_test.wav"
        save_pcm_as_wav(audio, tmp_wav, sample_rate=16000)

        res = self.asr.transcribe(tmp_wav)
        self.assertEqual(res["language"], "hin_Deva")
        import os
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)

    def test_06_load_audio_resampling(self):
        """Audio loader correctly resamples different sample rates to 16000Hz."""
        # 8000 Hz input audio
        t = np.linspace(0, 1.0, 8000, endpoint=False)
        audio_8k = (0.5 * np.sin(2 * np.pi * 200.0 * t)).astype(np.float32)
        tmp_8k = "sample_materials/test_8k.wav"
        save_pcm_as_wav(audio_8k, tmp_8k, sample_rate=8000)

        loaded = load_audio_for_asr(tmp_8k, target_sample_rate=16000)
        self.assertEqual(len(loaded), 16000)
        import os
        if os.path.exists(tmp_8k):
            os.remove(tmp_8k)

    def test_07_language_code_is_hindi(self):
        """Result language is tagged as hin_Deva."""
        silence = np.zeros(8000, dtype=np.float32)
        res = self.asr.transcribe(silence)
        self.assertEqual(res["language"], "hin_Deva")

    def test_08_duration_tracking(self):
        """Audio duration in seconds is accurately measured."""
        samples_2sec = np.zeros(32000, dtype=np.float32)
        res = self.asr.transcribe(samples_2sec)
        self.assertEqual(res["duration_seconds"], 2.0)

    def test_09_unicode_safety_no_mojibake(self):
        """Transcribe output is clean Unicode."""
        res = self.asr.transcribe(np.zeros(16000, dtype=np.float32))
        self.assertNotIn("à¤", res["text"])

    def test_10_model_unload(self):
        """Model can be unloaded from memory."""
        self.asr.unload_model()
        self.assertFalse(self.asr.is_loaded())


if __name__ == "__main__":
    unittest.main()
