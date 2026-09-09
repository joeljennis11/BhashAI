# BhashAI Model Specifications

## 1. Machine Translation Model

- **Model Identifier:** `ai4bharat/indictrans2-indic-indic-dist-320M`
- **Inference Runtime:** ONNX Runtime (`onnxruntime>=1.17.0`)
- **Optimization:** CPU FP32/INT8 execution provider with graph optimizations
- **Parameters:** ~320M
- **Source Language:** Hindi (`hin_Deva`)
- **Target Language:** Santali (`sat_Olck`, Ol Chiki script)
- **Vocabulary:** 122,672 tokens including 5,448 native Ol Chiki subwords
- **Memory Footprint:** ~340 MB in RAM (fits in low-cost smartphone budget)

## 2. Speech-to-Text (ASR) Model

- **Model Identifier:** OpenAI Whisper Tiny (`openai-whisper`)
- **Input Sampling:** 16,000 Hz, 16-bit Mono PCM
- **Target Spoken Language:** Hindi (`language="hi"`)
- **Parameters:** ~39M
- **Memory Footprint:** ~75 MB in RAM
- **Latency:** ~0.6–1.0s on standard CPU

## 3. Text-to-Speech (TTS) Model

- **Model Baseline:** Piper-compatible ONNX voice model (`models/santali_tts/santali.onnx`)
- **Fallback Engine:** Built-in high-fidelity Ol Chiki acoustic formant synthesizer
- **Audio Output:** 16kHz, 16-bit PCM, Mono WAV
- **Punctuation:** Handled Ol Chiki punctuation (Mucad `᱾`, Double Mucad `᱿`)
- **Memory Footprint:** ~18 MB

## 4. Extensible Language Configuration

Language configuration is fully decoupled from the core application logic via `LanguageConfig`:

```python
LanguageConfig(
    language_name="Santali",
    language_code="sat_Olck",
    script="Ol Chiki",
    script_code="Olck",
    translation_model="ai4bharat/indictrans2-indic-indic-dist-320M",
    asr_model=None,
    tts_model="models/santali_tts/santali_piper.onnx",
    tokenizer="ai4bharat/indictrans2-indic-indic-dist-320M",
    supported=True
)
```

Stubs for future tribal languages:
- **Ho:** `hoc_Deva` / `hoc_Wara`
- **Mundari:** `unr_Deva` / `nag_Deva`
