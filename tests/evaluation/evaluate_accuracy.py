"""
BhashAI Translation Accuracy & Quality Evaluation Script
Evaluates model output on reference FLN classroom sentences.
Computes chrF, Ol Chiki script adherence, and human review status.
"""

import sys
import os
import json
import time
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")

# Ensure repository root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.services.translation_service import TranslationService
from backend.utils.unicode_utils import ol_chiki_character_ratio, clean_unicode


def compute_chrf(reference: str, hypothesis: str, n: int = 4) -> float:
    """Computes character-level n-gram F-score (chrF)."""
    ref = clean_unicode(reference)
    hyp = clean_unicode(hypothesis)

    if not ref or not hyp:
        return 0.0

    def get_ngrams(s, n_len):
        return [s[i:i+n_len] for i in range(len(s) - n_len + 1)]

    ref_ngrams = set(get_ngrams(ref, n))
    hyp_ngrams = set(get_ngrams(hyp, n))

    if not ref_ngrams or not hyp_ngrams:
        return 1.0 if ref == hyp else 0.0

    overlap = len(ref_ngrams.intersection(hyp_ngrams))
    precision = overlap / len(hyp_ngrams) if hyp_ngrams else 0.0
    recall = overlap / len(ref_ngrams) if ref_ngrams else 0.0

    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def run_evaluation(data_path: str = "tests/evaluation/test_sentences.json"):
    print("=" * 60)
    print("           BHASH AI TRANSLATION EVALUATION")
    print("=" * 60)

    with open(data_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    trans_service = TranslationService.get_instance()
    results = []
    total_chrf = 0.0
    olchiki_count = 0

    for item in sentences:
        hi = item["hindi"]
        exp = item["expected_santali"]
        topic = item.get("topic")

        t0 = time.time()
        res = trans_service.translate(hi, lesson_topic=topic)
        elapsed = round(time.time() - t0, 3)

        out = res["translation"]
        chrf = compute_chrf(exp, out)
        total_chrf += chrf
        script_ratio = ol_chiki_character_ratio(out)
        if script_ratio > 0.5:
            olchiki_count += 1

        status = "Correct" if chrf >= 0.6 else ("Needs Review" if chrf >= 0.3 or script_ratio > 0.4 else "Incorrect")

        results.append({
            "id": item["id"],
            "hindi": hi,
            "expected_santali": exp,
            "model_output": out,
            "chrf_score": round(chrf, 3),
            "ol_chiki_ratio": round(script_ratio, 2),
            "status": status,
            "latency_seconds": elapsed
        })

        print(f"[{item['id']}] Hindi: {hi}")
        print(f"    Expected: {exp}")
        print(f"    Output:   {out}")
        print(f"    Status:   {status} | chrF: {round(chrf, 3)} | Latency: {elapsed}s\n")

    avg_chrf = total_chrf / len(sentences) if sentences else 0.0
    olchiki_compliance = (olchiki_count / len(sentences)) * 100 if sentences else 0.0

    summary = {
        "total_evaluated": len(sentences),
        "average_chrf": round(avg_chrf, 3),
        "ol_chiki_script_compliance_percent": round(olchiki_compliance, 1),
        "evaluation_results": results
    }

    report_path = Path("tests/evaluation/evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"Average chrF: {round(avg_chrf, 3)}")
    print(f"Ol Chiki Script Compliance: {round(olchiki_compliance, 1)}%")
    print(f"Report saved to: {report_path}")
    print("=" * 60)
    return summary


if __name__ == "__main__":
    run_evaluation()
