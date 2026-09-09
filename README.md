# BHASH AI (भाषAI)

> **AI-Assisted Vernacular Education & Classroom Communication Application**  
> Designed for teachers teaching foundational literacy and numeracy (FLN) to children speaking Indian tribal and vernacular languages.

---

## Prototype Language Pair
- **Source:** Hindi (`hin_Deva`, Devanagari script)
- **Target:** Santali (`sat_Olck`, Ol Chiki script)
- **Future Extensible Stubs:** Ho (`hoc_Deva`/`hoc_Wara`), Mundari (`unr_Deva`)

---

## Key Features

- **Hindi Speech-to-Text (ASR):** Whisper-powered 16kHz speech recognition producing strict Unicode UTF-8 Hindi text.
- **Context-Aware Translation:** IndicTrans2 320M NMT with pure-Python compatible preprocessing (no Microsoft C++ Build Tools required), sliding-window conversational memory, and topic disambiguation.
- **Santali Text-to-Speech (TTS):** Piper-compatible ONNX voice engine and high-fidelity native Ol Chiki acoustic synthesizer generating 16-bit PCM 16kHz WAV audio.
- **Voice-to-Voice Pipeline:** End-to-end Hindi speech ➔ Hindi text ➔ Santali translation ➔ Santali audio.
- **Vernacular Worksheet Generator:** Source-grounded question generator from uploaded educational PDFs across 10 question formats with interactive teacher review (`DRAFT` ➔ `REVIEWED` ➔ `APPROVED`).
- **Printable A4 PDF Export:** Generates Student Worksheets and Teacher Answer Keys using ReportLab with embedded official Google Noto Sans Ol Chiki font.
- **Visual Flashcards:** Vocabulary cards with visual concepts, Hindi text, Santali Ol Chiki, and audio playback.
- **Memory Lifecycle Management:** Designed for ~2 GB RAM, CPU-only Android 9+ devices with sequential model loading and active garbage collection.
- **100% Offline-First:** Operates completely without internet connectivity after first-run synchronization.

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

## Directory Structure

```
BhashAI/
├── android/
│   └── BhashAI/                   # Native Android (Kotlin, Jetpack Compose, Material 3)
│       ├── app/src/main/assets/fonts/NotoSansOlChiki-Regular.ttf
│       └── app/src/main/java/com/bhashai/app/
│           ├── BhashAIApp.kt
│           ├── data/
│           └── ui/screens/        # 10 Screen implementations
│
├── backend/
│   ├── main.py                    # FastAPI application entrypoint
│   ├── models/                    # Pydantic schemas & LanguageConfig
│   ├── routes/                    # API endpoints (speech, translation, tts, etc.)
│   ├── services/                  # ASR, IndicTrans2, Santali TTS, Context, Worksheets
│   ├── utils/                     # Unicode, Audio, Memory lifecycle
│   └── static/                    # Teacher companion web interface & fonts
│
├── models/                        # Local weights cache (ASR, Translation, TTS)
├── sample_materials/              # Demo lesson PDFs (Class 1 Fruits)
├── generated/                     # Generated A4 PDF worksheets and WAV audio
├── tests/                         # Comprehensive unit & integration test suites
│   └── evaluation/                # 10 reference FLN sentences & accuracy evaluation
├── docs/                          # Architecture, models, offline, android docs
├── benchmark.py                   # Latency & Peak RAM measurement script
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation & Setup (Windows PowerShell)

### 1. Prerequisites
- Python 3.10+ (Verified on Python 3.13 / 3.14)
- Git

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Start Backend Server
```powershell
python backend/main.py
```
The server will start on `http://localhost:8000`. You can open this URL in your web browser to use the interactive Teacher Companion Web Console.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/speech/transcribe` | Upload audio (WAV/MP3/WebM) ➔ Hindi Unicode text |
| `POST` | `/api/translate` | Context-aware Hindi ➔ Santali Ol Chiki translation |
| `POST` | `/api/translate/voice` | End-to-End Voice-to-Voice translation |
| `POST` | `/api/tts` | Synthesize Santali Ol Chiki text to 16kHz WAV |
| `GET` | `/api/tts/audio/{filename}` | Stream synthesized WAV audio |
| `POST` | `/api/documents/upload` | Upload educational PDF & extract structured FLN content |
| `POST` | `/api/worksheets/generate` | Generate bilingual FLN worksheet (DRAFT status) |
| `PUT` | `/api/worksheets/{id}` | Teacher review: edit questions & approve |
| `GET` | `/api/worksheets/{id}/export` | Export printable A4 PDF (Student or Answer Key) |
| `GET` | `/api/flashcards/lesson/{id}` | Retrieve visual vocabulary flashcards |
| `GET` | `/api/health` | System health, model readiness, and memory metrics |
| `POST` | `/api/models/prepare-offline` | Synchronize and cache all models for offline use |

---

## Testing & Verification

Run the automated test suite:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

Run accuracy evaluation on reference FLN dataset:
```powershell
python tests/evaluation/evaluate_accuracy.py
```

Run latency and RAM benchmark:
```powershell
python benchmark.py
```

---

## Smart India Hackathon (SIH) Demonstration Flow

1. **Open BhashAI:** Open `http://localhost:8000` or launch the Android application.
2. **Verify Language Pair:** Hindi (`hin_Deva`) ➔ Santali (`sat_Olck`, Ol Chiki).
3. **Voice Translation:**
   - Click **START RECORDING** (or hold mic).
   - Speak: *"आज हम फलों के बारे में सीखेंगे। यह एक आम है।"*
   - Observe live Hindi ASR output.
   - Observe instant Ol Chiki translation: `ᱛᱮᱦᱮᱧ ᱫᱚ ᱵᱚᱱ ᱡᱚ ᱵᱟᱵᱚᱛ ᱵᱚᱱ ᱪᱮᱫ-ᱟ ᱾ ᱱᱚᱣᱟ ᱫᱚ ᱩᱞ ᱠᱟᱱᱟ ᱾`
4. **Play Audio:** Click **🔊 Play Santali Audio** to hear natural speech pronunciation.
5. **Worksheet Generation:**
   - Go to **Worksheet Generator** tab.
   - Upload `sample_materials/class1_fruits_hindi.pdf` (or click *Load Class 1 Fruits Demo PDF*).
   - Review derived questions (Picture ID, MCQ, Fill in blanks).
   - Edit a prompt or answer in teacher review mode.
   - Click **Approve Worksheet** (status transitions to `APPROVED`).
   - Click **Export Student PDF** to open the printable A4 worksheet.
6. **Flashcards:**
   - Go to **Flashcards** tab.
   - Flip through vocabulary cards (आम ➔ ᱩᱞ, सेब ➔ ᱥᱮᱣ, केला ➔ ᱠᱟᱭᱨᱟ).
   - Click **Listen Pronunciation** to test on-demand audio.
7. **Demonstrate Offline Capability:**
   - Go to **Offline Resources** tab.
   - Verify models show **✓ Installed**.
   - Disconnect Wi-Fi/Internet.
   - Repeat translation: the entire pipeline continues operating offline with zero crashes!
