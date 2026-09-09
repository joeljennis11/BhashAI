# BhashAI Offline Architecture & Operation Guide

## Offline-First Design

Rural and tribal schools frequently experience intermittent or absent internet connectivity. BhashAI enforces an **Offline-First Architecture**:

| Operation | Online Phase | Offline Classroom Phase |
|---|---|---|
| **Model Management** | Download & verify model weights | Load from local flash storage (`models/`) |
| **Speech-to-Text** | Check for updates | Local Whisper inference |
| **Translation** | Synchronize vocabulary | Local IndicTrans2 ONNX inference |
| **TTS Synthesis** | Cache voices | Local acoustic / Piper synthesis |
| **Curriculum & PDFs** | Download syllabus | Local PDF parsing & cached worksheets |
| **Worksheet PDFs** | N/A | Local ReportLab PDF generation |

---

## Prepare Offline Mode Workflow

To configure BhashAI for zero-internet field demonstration:

1. Connect device or computer to internet during initial setup.
2. Open the **Offline Resources** tab (or call `POST /api/models/prepare-offline`).
3. Click **Prepare Offline Mode**.
4. The backend initializes:
   - Whisper ASR model in local cache (`~/.cache/whisper`)
   - IndicTrans2 ONNX files in `~/.cache/huggingface/hub` or `models/translation`
   - Noto Sans Ol Chiki font in assets
5. Verify that the indicator turns from **ONLINE** to **OFFLINE READY**.
6. Turn off Wi-Fi and mobile data. All speech, translation, TTS, worksheets, and flashcard features will continue running locally.
