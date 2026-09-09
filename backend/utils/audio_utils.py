"""
BhashAI Audio Utilities
Provides audio format conversion, 16kHz mono normalization for Whisper ASR,
WAV metadata verification, and caching utilities.
"""

import os
import wave
import hashlib
import io
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import numpy as np


def compute_audio_hash(text: str, voice_id: str = "santali_v1") -> str:
    """Returns MD5 hash for a given text and voice identifier for cached audio storage."""
    key = f"{voice_id}::{text.strip()}"
    return hashlib.md5(key.encode("utf-8")).hexdigest()


def get_wav_metadata(file_path_or_bytes: Any) -> Dict[str, Any]:
    """
    Inspects a WAV audio source and returns channels, sample_rate, bit_depth, duration, and num_frames.
    """
    try:
        if isinstance(file_path_or_bytes, (str, Path)):
            wav_file = wave.open(str(file_path_or_bytes), "rb")
        elif isinstance(file_path_or_bytes, bytes):
            wav_file = wave.open(io.BytesIO(file_path_or_bytes), "rb")
        elif hasattr(file_path_or_bytes, "read"):
            wav_file = wave.open(file_path_or_bytes, "rb")
        else:
            raise ValueError("Unsupported audio input type.")

        with wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            duration = num_frames / float(sample_rate) if sample_rate > 0 else 0.0

            return {
                "valid": True,
                "channels": channels,
                "sample_width": sample_width,
                "bit_depth": sample_width * 8,
                "sample_rate": sample_rate,
                "num_frames": num_frames,
                "duration_seconds": round(duration, 3),
            }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


def save_pcm_as_wav(
    pcm_data: np.ndarray,
    output_path: str,
    sample_rate: int = 16000,
) -> str:
    """
    Saves float32 or int16 numpy array audio into standard 16-bit PCM mono WAV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Normalize float32 [-1.0, 1.0] to int16 [-32768, 32767]
    if pcm_data.dtype in (np.float32, np.float64):
        # Clip amplitudes
        clipped = np.clip(pcm_data, -1.0, 1.0)
        int16_data = (clipped * 32767.0).astype(np.int16)
    elif pcm_data.dtype == np.int16:
        int16_data = pcm_data
    else:
        int16_data = pcm_data.astype(np.int16)

    with wave.open(output_path, "wb") as wav_out:
        wav_out.setnchannels(1)       # Mono
        wav_out.setsampwidth(2)      # 16-bit (2 bytes)
        wav_out.setframerate(sample_rate)
        wav_out.writeframes(int16_data.tobytes())

    return output_path


def load_audio_for_asr(
    audio_path_or_bytes: Any,
    target_sample_rate: int = 16000
) -> np.ndarray:
    """
    Loads audio from a file path or in-memory bytes, converts to mono,
    resamples to 16kHz float32 array in range [-1.0, 1.0] suitable for Whisper.
    """
    # 1. Try wave first if it's already a WAV file
    try:
        if isinstance(audio_path_or_bytes, (str, Path)):
            with wave.open(str(audio_path_or_bytes), "rb") as w:
                nchannels = w.getnchannels()
                sampwidth = w.getsampwidth()
                framerate = w.getframerate()
                nframes = w.getnframes()
                raw_bytes = w.readframes(nframes)
            
            if sampwidth == 2:
                samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            elif sampwidth == 1:
                samples = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
            else:
                samples = np.frombuffer(raw_bytes, dtype=np.int32).astype(np.float32) / 2147483648.0

            if nchannels > 1:
                samples = samples.reshape(-1, nchannels).mean(axis=1)

            if framerate != target_sample_rate and len(samples) > 0:
                # Linear or scipy resample
                from scipy import signal
                num_resampled = int(len(samples) * target_sample_rate / framerate)
                samples = signal.resample(samples, num_resampled)

            return samples.astype(np.float32)
    except Exception:
        pass

    # 2. Fallback to pydub / soundfile for MP3/WebM/OGG
    try:
        from pydub import AudioSegment
        if isinstance(audio_path_or_bytes, bytes):
            seg = AudioSegment.from_file(io.BytesIO(audio_path_or_bytes))
        else:
            seg = AudioSegment.from_file(str(audio_path_or_bytes))
        
        seg = seg.set_frame_rate(target_sample_rate).set_channels(1).set_sample_width(2)
        raw_data = seg.raw_data
        samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0
        return samples
    except Exception as e:
        raise RuntimeError(f"Failed to load and convert audio for ASR: {e}")
