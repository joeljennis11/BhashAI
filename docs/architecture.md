# BhashAI System Architecture

## Overview

BhashAI is an offline-capable vernacular education platform designed for primary school teachers teaching Foundational Literacy and Numeracy (FLN) to tribal children. The primary prototype translates from **Hindi (hin_Deva)** to **Santali in Ol Chiki script (sat_Olck)**.

---

## Architecture Diagram

```
                    BHASH AI
                       │
       ┌───────────────┼───────────────┐
       │               │               │
      ASR         Translation          TTS
  (Whisper)     (IndicTrans2)    (Piper/Acoustic)
       │               │               │
  Hindi text      Santali text    Santali audio
       │               │
       └───────┬───────┘
               │
         Context Engine
  (Sliding Window & Topic Guard)
               │
       ┌───────┴────────┐
       │                │
    Lessons        Worksheets
  (PDF Upload)   (10 FLN Types)
       │                │
      OCR         Teacher Review
       │         (DRAFT ➔ APPR)
       └───────┬────────┘
               │
          Offline Cache
               │
       Native Android (9+)
         (~2GB RAM CPU)
```

---

## Core Components

### 1. Speech Recognition (ASR)
- **Model:** Whisper (Tiny/Base), 16kHz mono sampling.
- **Unicode Safety:** Preserves strict UTF-8 Devanagari Unicode. Automatically detects and rectifies Mojibake (`à¤¬...`).

### 2. Machine Translation (NMT)
- **Model:** `ai4bharat/indictrans2-indic-indic-dist-320M` (ONNX Runtime engine).
- **Compatible Preprocessor:** Pure-Python `CompatibleIndicProcessor` eliminates the need for Microsoft C++ Build Tools on Windows/Android.
- **Quality Control Layer:** Detects empty responses, excessive shortness, repeated token hallucination loops, and unexpected scripts before displaying results to teachers.

### 3. Speech Synthesis (TTS)
- **Engine:** Piper-compatible ONNX voice model and native Ol Chiki acoustic formant synthesizer.
- **Audio Output:** 16-bit PCM 16000Hz mono WAV files.
- **Caching:** Content-hash MD5 caching prevents redundant audio synthesis for repetitive vocabulary words.

### 4. Conversation Context Engine
- **Memory:** Sliding window of the previous 2–3 teacher sentences.
- **Dynamic Topic Ingestion:** Identifies active lesson topics (e.g. "Fruits", "Numbers") and prevents polysemous word confusion (e.g. distinguishing fruit "आम" from "ordinary").

### 5. Vernacular Worksheet Generator
- **Grounded Generation:** Derived directly from uploaded lesson PDFs with page number tracking.
- **Formats:** Picture ID, Multiple Choice, Fill in the Blanks, Match, True/False, Count & Write.
- **Review Workflow:** `DRAFT` ➔ `REVIEWED` ➔ `APPROVED`.
- **Export:** Printable A4 PDFs using ReportLab with embedded Google Noto Sans Ol Chiki font.

### 6. Memory Lifecycle Management
- Target hardware: Android 9+ smartphones with ~2 GB RAM.
- Sequential model loader unloads idle pipelines and triggers garbage collection to keep process RSS below 450 MB.
