"""Boundary-Aware Sentence Segmentation for Timestamped Legal Transcripts.

Preserves legal abbreviations, statutory citations (Sec., Art., v.),
regional Indic sentence boundaries (।, ?, !), and interpolates exact
per-sentence start and end timestamps from raw ASR segments.
"""

import re
import sys
import logging
from typing import Dict, Any, List

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SentenceSegmenter")

from src.preprocessing.cleaner import LEGAL_ABBREVIATIONS, REVERSE_LEGAL_ABBREVIATIONS, TranscriptCleaner


class LegalSentenceSegmenter:
    """Sentence boundary detector designed for legal speech transcripts."""

    def __init__(self, cleaner: TranscriptCleaner = None):
        self.cleaner = cleaner or TranscriptCleaner()

    def _protect_abbreviations(self, text: str) -> str:
        """Replace periods in legal honorifics and citations with safe placeholders."""
        protected = text
        for abbr, token in LEGAL_ABBREVIATIONS.items():
            pattern = re.compile(re.escape(abbr), re.IGNORECASE)
            protected = pattern.sub(token, protected)
        return protected

    def _restore_abbreviations(self, text: str) -> str:
        """Restore protected legal tokens back to standard legal punctuation."""
        restored = text
        for token, abbr in REVERSE_LEGAL_ABBREVIATIONS.items():
            restored = restored.replace(token, abbr)
        return restored

    def segment_transcript(self, raw_asr_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Split continuous ASR segments into indexed sentences with interpolated timestamps.

        Args:
            raw_asr_segments: List of dicts with 'start', 'end', and 'text' keys.

        Returns:
            List of structured sentence dicts:
            [
              {
                "sentence_id": int,
                "start_time": float,
                "end_time": float,
                "text": str,
                "raw_text": str,
                "word_count": int,
                "speaker": str
              }
            ]
        """
        sentences = []
        global_sent_id = 1

        for seg_idx, seg in enumerate(raw_asr_segments):
            seg_start = float(seg.get("start", 0.0))
            seg_end = float(seg.get("end", 0.0))
            seg_text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "Unknown")

            if not seg_text:
                continue

            # Protect abbreviations
            protected_text = self._protect_abbreviations(seg_text)

            # Split on terminal punctuation: . ! ? or Indic danda ।
            raw_splits = re.split(r'(?<=[.!?\u0964])\s+', protected_text)
            raw_splits = [s.strip() for s in raw_splits if s.strip()]

            if not raw_splits:
                raw_splits = [protected_text]

            total_chars = sum(len(s) for s in raw_splits)
            seg_duration = max(0.2, seg_end - seg_start)

            cursor_time = seg_start
            for s_idx, part in enumerate(raw_splits):
                restored = self._restore_abbreviations(part)
                cleaned, _ = self.cleaner.clean_text(restored, f"SEG_{seg_idx}_SENT_{s_idx}")

                if not cleaned:
                    continue

                # Interpolate timestamp based on character length ratio
                char_ratio = len(part) / max(1, total_chars)
                sent_duration = round(seg_duration * char_ratio, 2)
                s_start = round(cursor_time, 2)
                s_end = round(min(seg_end, cursor_time + sent_duration), 2)
                cursor_time = s_end

                words = cleaned.split()
                if len(words) < 2 and len(cleaned) < 5:
                    # Filter out isolated stray characters
                    continue

                sent_record = {
                    "sentence_id": global_sent_id,
                    "start_time": s_start,
                    "end_time": max(s_start + 0.5, s_end),
                    "text": cleaned,
                    "raw_text": restored,
                    "word_count": len(words),
                    "speaker": speaker
                }
                sentences.append(sent_record)
                global_sent_id += 1

        return sentences


if __name__ == "__main__":
    segmenter = LegalSentenceSegmenter()
    sample_segments = [
        {
            "start": 10.0,
            "end": 22.5,
            "text": "The State v. Stewart precedent clearly applies here. Mr. Shelton was not present at the scene. Therefore, bail must be granted."
        }
    ]
    res = segmenter.segment_transcript(sample_segments)
    print(f"Segmented into {len(res)} sentences:")
    for s in res:
        print(f" [{s['start_time']:05.2f}s - {s['end_time']:05.2f}s] ID {s['sentence_id']}: {s['text']}")
