"""Phase 12: Live / Near-Real-Time Court Proceeding Streaming Simulator.

Simulates live courtroom audio capture by slicing continuous audio into
streaming buffers (10-25s), transcribing incrementally, and maintaining a
running extractive summary with latency telemetry.
"""

import os
import sys
import time
import json
import logging
import soundfile as sf
from pathlib import Path
from typing import Dict, Any, List

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LiveCourtSimulator")

from src.asr.transcriber import CourtTranscriber
from src.preprocessing.cleaner import TranscriptCleaner
from src.preprocessing.segmenter import LegalSentenceSegmenter
from src.summarization.textrank_summarizer import TextRankCourtSummarizer
from src.summarization.legal_enhancer import LegalDomainEnhancer


class LiveCourtProceedingSimulator:
    """Simulates near-real-time streaming courtroom transcription and running extractive summary."""

    def __init__(self, chunk_window_sec: float = 15.0, model_size: str = "tiny"):
        self.chunk_window_sec = chunk_window_sec
        self.transcriber = CourtTranscriber(model_size=model_size)
        self.cleaner = TranscriptCleaner()
        self.segmenter = LegalSentenceSegmenter(cleaner=self.cleaner)
        self.summarizer = TextRankCourtSummarizer()
        self.enhancer = LegalDomainEnhancer()

        self.running_sentences: List[Dict[str, Any]] = []
        self.running_summary: List[Dict[str, Any]] = []
        self.latency_log: List[Dict[str, Any]] = []

    def stream_audio_file(self, wav_path: str, output_log: str = "outputs/live_streaming_log.json"):
        """Simulate real-time chunked ingestion of an audio file."""
        p = Path(wav_path)
        if not p.exists():
            raise FileNotFoundError(f"WAV audio file not found: {wav_path}")

        data, sr = sf.read(str(p), dtype="float32")
        total_duration = len(data) / sr
        chunk_frames = int(self.chunk_window_sec * sr)

        logger.info(f"=== Starting Live Simulation for {p.name} ({total_duration:.1f}s) ===")
        logger.info(f"Chunk Window: {self.chunk_window_sec}s | Sample Rate: {sr} Hz")

        temp_chunk_dir = Path("outputs/temp_live_chunks")
        temp_chunk_dir.mkdir(parents=True, exist_ok=True)

        cursor = 0
        chunk_idx = 1
        overall_start_time = time.time()

        while cursor < len(data):
            chunk_start_sec = round(cursor / sr, 2)
            chunk_data = data[cursor:cursor + chunk_frames]
            cursor += chunk_frames
            chunk_end_sec = round(min(total_duration, cursor / sr), 2)

            # Write chunk to ephemeral WAV
            chunk_wav = temp_chunk_dir / f"live_chunk_{chunk_idx:03d}.wav"
            sf.write(str(chunk_wav), chunk_data, sr, subtype="PCM_16")

            # Measure Ingestion & Transcription Latency
            t_chunk_start = time.time()
            asr_res = self.transcriber.transcribe(str(chunk_wav), task="transcribe")
            asr_latency = round(time.time() - t_chunk_start, 2)

            # Offset chunk segment timestamps by global chunk_start_sec
            for seg in asr_res["segments"]:
                seg["start"] = round(seg["start"] + chunk_start_sec, 2)
                seg["end"] = round(seg["end"] + chunk_start_sec, 2)

            # Segment into clean legal sentences
            new_sentences = self.segmenter.segment_transcript(asr_res["segments"])
            for s in new_sentences:
                s["sentence_id"] = len(self.running_sentences) + 1
                self.running_sentences.append(s)

            # Update Running Extractive Summary periodically
            t_sum_start = time.time()
            if len(self.running_sentences) >= 3:
                scores = self.summarizer.score_sentences(self.running_sentences)
                boosted_scores, enriched = self.enhancer.boost_sentence_scores(
                    self.running_sentences, scores, language=asr_res["detected_language"]
                )
                # Keep top 25% of current running transcript
                k = max(2, int(len(self.running_sentences) * 0.25))
                ranked = sorted(zip(enriched, boosted_scores), key=lambda x: x[1], reverse=True)[:k]
                self.running_summary = sorted([r[0] for r in ranked], key=lambda x: x["start_time"])
            sum_latency = round(time.time() - t_sum_start, 3)

            total_step_latency = round(asr_latency + sum_latency, 2)
            rtf = round(total_step_latency / max(0.1, chunk_end_sec - chunk_start_sec), 3)

            step_record = {
                "chunk_index": chunk_idx,
                "window": f"{chunk_start_sec:05.1f}s - {chunk_end_sec:05.1f}s",
                "asr_latency_sec": asr_latency,
                "summary_latency_sec": sum_latency,
                "total_step_latency_sec": total_step_latency,
                "real_time_factor": rtf,
                "transcript_growth_sentences": len(self.running_sentences),
                "running_summary_sentences": len(self.running_summary),
                "latest_text": asr_res["full_transcript"][:80] + "..." if asr_res["full_transcript"] else ""
            }
            self.latency_log.append(step_record)

            logger.info(
                f"[Chunk {chunk_idx:02d}] Window: {chunk_start_sec:05.1f}s-{chunk_end_sec:05.1f}s | "
                f"Latency: {total_step_latency}s (RTF: {rtf}) | Total Sents: {len(self.running_sentences)} | Summary: {len(self.running_summary)}"
            )
            chunk_idx += 1

        total_elapsed = round(time.time() - overall_start_time, 2)

        # Export live simulation telemetry log
        out_p = Path(output_log)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        simulation_summary = {
            "source_file": str(p),
            "total_audio_duration_sec": total_duration,
            "chunk_window_sec": self.chunk_window_sec,
            "total_chunks_processed": chunk_idx - 1,
            "total_processing_time_sec": total_elapsed,
            "mean_step_latency_sec": round(float(sum(x["total_step_latency_sec"] for x in self.latency_log) / max(1, len(self.latency_log))), 2),
            "mean_rtf": round(float(sum(x["real_time_factor"] for x in self.latency_log) / max(1, len(self.latency_log))), 3),
            "final_transcript_sentences": len(self.running_sentences),
            "final_extractive_summary": [
                f"[{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] [{s.get('legal_type', 'PROCEDURAL')}] {s['text']}"
                for s in self.running_summary
            ],
            "step_telemetry": self.latency_log
        }

        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(simulation_summary, f, ensure_ascii=False, indent=2)

        logger.info(f"=== Live Simulation Finished in {total_elapsed}s. Saved log to {out_p} ===")
        return simulation_summary


if __name__ == "__main__":
    print("Testing Live Court Proceeding Simulator...")
    sample_wav = "data/extracted_audio/CASE_01_5_Movie_CLIP_-_Automotive_Exp.wav"
    if Path(sample_wav).exists():
        sim = LiveCourtProceedingSimulator(chunk_window_sec=15.0)
        res = sim.stream_audio_file(sample_wav)
        print(f"\nFinal Running Summary ({len(res['final_extractive_summary'])} sentences):")
        for s in res["final_extractive_summary"][:4]:
            print("  *", s)
