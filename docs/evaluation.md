# BhashAI Evaluation & Quality Control Guide

## Overview

Santali is a low-resource indigenous language. Machine translation output must be evaluated and guarded with rigorous linguistic checks rather than assuming 100% correctness.

---

## Evaluation Metrics

1. **chrF (Character n-gram F-score):** Effective metric for agglutinative and morphologically rich languages like Santali where subwords convey grammatical suffixes.
2. **Ol Chiki Script Adherence Ratio:** Verifies what fraction of characters belong to the Unicode Ol Chiki range (`U+1C50` to `U+1C7F`).
3. **Teacher / Human Review Categorization:**
   - **Correct:** Accurate translation matching pedagogical intent.
   - **Needs Review:** Partially translated, minor morphological variance, or low-confidence flagged.
   - **Incorrect:** Script mismatch, hallucination, or untranslated echo.

---

## Running Accuracy Evaluation

To run the automated evaluation suite against the reference FLN dataset:

```powershell
python tests/evaluation/evaluate_accuracy.py
```

The script reads `tests/evaluation/test_sentences.json` (containing 10 diverse classroom sentences across greetings, counting, fruits, commands, and ambiguity tests) and outputs `tests/evaluation/evaluation_report.json`.
