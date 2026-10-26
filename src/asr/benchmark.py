"""Whisper Multilingual Benchmarking and Legal Entity Error Analysis Module.

Benchmarks model capacity against compute limits (latency, Real-Time Factor, memory),
computes Word Error Rate (WER) against gold-standard references, and performs granular
error breakdowns on legal terminology, proper nouns, and statutory numbers.
"""

import os
import sys
import json
import time
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, List

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ASRBenchmark")

import jiwer
from src.asr.transcriber import CourtTranscriber

LEGAL_KEYWORDS_BENCHMARK = [
    "bail", "murder", "exhibit", "witness", "testimony", "section",
    "ipc", "crpc", "perjury", "acquitted", "convicted", "judge",
    "prosecution", "defense", "overruled", "sustained", "confession"
]


def compute_wer(reference_text: str, hypothesis_text: str) -> float:
    """Calculate standard Word Error Rate (WER)."""
    ref = reference_text.strip().lower()
    hyp = hypothesis_text.strip().lower()
    if not ref:
        return 0.0 if not hyp else 1.0
    return round(float(jiwer.wer(ref, hyp)), 4)


def analyze_legal_entity_errors(reference_text: str, hypothesis_text: str) -> Dict[str, Any]:
    """Perform targeted error analysis on legal terms, numbers, and proper nouns."""
    ref_words = reference_text.lower().split()
    hyp_words = set(hypothesis_text.lower().split())

    legal_hits = 0
    legal_misses = []
    for kw in LEGAL_KEYWORDS_BENCHMARK:
        if kw in ref_words:
            if kw in hyp_words:
                legal_hits += 1
            else:
                legal_misses.append(kw)

    # Check numerical preservation (e.g. years, sections, amounts)
    import re
    ref_numbers = set(re.findall(r'\b\d+\b', reference_text))
    hyp_numbers = set(re.findall(r'\b\d+\b', hypothesis_text))
    num_hits = len(ref_numbers.intersection(hyp_numbers))
    num_misses = list(ref_numbers - hyp_numbers)

    return {
        "legal_term_accuracy": round(legal_hits / max(1, legal_hits + len(legal_misses)), 3),
        "legal_term_misses": legal_misses,
        "number_accuracy": round(num_hits / max(1, len(ref_numbers)), 3) if ref_numbers else 1.0,
        "number_misses": num_misses
    }


def run_asr_benchmark(
    audio_dir: str = "data/extracted_audio",
    gold_dir: str = "data/gold_standard/transcripts",
    models_to_test: List[str] = ["tiny"],
    output_report: str = "reports/asr_benchmark_results.json"
) -> Dict[str, Any]:
    """Execute end-to-end ASR benchmark across available test cases and model sizes."""
    gold_p = Path(gold_dir)
    audio_p = Path(audio_dir)
    benchmark_records = []

    # Map gold references to audio files
    gold_files = list(gold_p.glob("*.json"))
    logger.info(f"Found {len(gold_files)} gold-standard references for ASR evaluation.")

    for model_size in models_to_test:
        logger.info(f"--- Benchmarking Whisper [{model_size}] ---")
        try:
            transcriber = CourtTranscriber(model_size=model_size)
        except Exception as e:
            logger.error(f"Failed to load model {model_size}: {e}")
            continue

        for gf in gold_files:
            with open(gf, "r", encoding="utf-8") as f:
                gold_data = json.load(f)

            case_id = gold_data.get("case_id", gf.stem)
            gold_lang = gold_data.get("language", "en")
            gold_full_text = " ".join(s["text"] for s in gold_data.get("sentences", []))

            # Match extracted audio file for this case
            matched_audio = None
            for af in audio_p.glob("*.wav"):
                if case_id in af.name or case_id.replace("CASE_", "CASE_0") in af.name:
                    matched_audio = af
                    break

            if not matched_audio:
                # Try fallback matching by order
                idx_str = case_id.split("_")[-1]
                for af in audio_p.glob("*.wav"):
                    if af.name.startswith(f"CASE_{idx_str}"):
                        matched_audio = af
                        break

            if not matched_audio:
                logger.warning(f"No audio file matched for {case_id}")
                continue

            # Record system resource snapshot before inference
            mem_before = psutil.Process().memory_info().rss / (1024 * 1024)
            t0 = time.time()

            try:
                result = transcriber.transcribe(str(matched_audio))
            except Exception as e:
                logger.error(f"Transcription error on {matched_audio.name}: {e}")
                continue

            inference_time = round(time.time() - t0, 2)
            mem_after = psutil.Process().memory_info().rss / (1024 * 1024)

            hyp_text = result["full_transcript"]
            wer = compute_wer(gold_full_text, hyp_text)
            err_analysis = analyze_legal_entity_errors(gold_full_text, hyp_text)

            record = {
                "model_size": model_size,
                "case_id": case_id,
                "source_title": gold_data.get("source_title", "Unknown"),
                "language": gold_lang,
                "audio_duration_sec": result["duration_sec"],
                "inference_time_sec": inference_time,
                "real_time_factor": result["real_time_factor"],
                "memory_delta_mb": round(mem_after - mem_before, 2),
                "detected_language": result["detected_language"],
                "language_confidence": result["language_confidence"],
                "wer": wer,
                "legal_term_accuracy": err_analysis["legal_term_accuracy"],
                "legal_term_misses": err_analysis["legal_term_misses"],
                "number_accuracy": err_analysis["number_accuracy"]
            }
            benchmark_records.append(record)
            logger.info(f"[{model_size}] {case_id} ({gold_lang}) -> WER: {wer*100:.1f}%, RTF: {result['real_time_factor']}")

    # Calculate summary metrics per language
    summary = {}
    for r in benchmark_records:
        lang = r["language"]
        if lang not in summary:
            summary[lang] = {"wers": [], "rtfs": [], "legal_accs": []}
        summary[lang]["wers"].append(r["wer"])
        summary[lang]["rtfs"].append(r["real_time_factor"])
        summary[lang]["legal_accs"].append(r["legal_term_accuracy"])

    aggregated = {}
    for lang, metrics in summary.items():
        aggregated[lang] = {
            "mean_wer": round(sum(metrics["wers"]) / len(metrics["wers"]), 4),
            "mean_rtf": round(sum(metrics["rtfs"]) / len(metrics["rtfs"]), 4),
            "mean_legal_term_acc": round(sum(metrics["legal_accs"]) / len(metrics["legal_accs"]), 4),
            "sample_count": len(metrics["wers"])
        }

    final_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "models_evaluated": models_to_test,
        "device": transcriber.device,
        "language_summary": aggregated,
        "individual_runs": benchmark_records
    }

    out_p = Path(output_report)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)

    return final_report


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 4: MULTILINGUAL ASR BENCHMARK & LEGAL ERROR ANALYSIS")
    print("=" * 70)
    report = run_asr_benchmark(models_to_test=["tiny"])
    print("\n--- Summary per Language ---")
    for lang, metrics in report["language_summary"].items():
        print(f"Language: {lang:<6} | Mean WER: {metrics['mean_wer']*100:>5.1f}% | RTF: {metrics['mean_rtf']:>5.3f} | Legal Terms: {metrics['mean_legal_term_acc']*100:>5.1f}%")
    print("=" * 70)
