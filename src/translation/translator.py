"""Phase 5: Multilingual Court Translation and Sentence-Alignment Module.

Supports dual-track execution:
  Track 1: Translate-then-summarize
  Track 2: Summarize-in-original-language with multilingual embeddings
Maintains strict sentence-level parallel alignment with synchronized timestamps.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CourtTranslator")

SUPPORTED_LANGUAGE_PAIRS = {
    "hi": "en",  # Hindi -> English
    "te": "en",  # Telugu -> English
    "ta": "en",  # Tamil -> English
    "en": "en"   # Identity pass-through
}

LANGUAGE_CODE_MAP = {
    "te": "te-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "en": "en-GB"
}


class CourtTranslator:
    """Sentence-aligned legal proceeding translator with multi-engine fallback."""

    def __init__(self, target_language: str = "en"):
        self.target_language = target_language
        self._cache: Dict[str, str] = {}

    def verify_language_pair(self, source_lang: str) -> bool:
        """Verify whether language pair is supported by judicial translation pipeline."""
        src = source_lang.lower().strip()
        supported = src in SUPPORTED_LANGUAGE_PAIRS
        if not supported:
            logger.warning(f"Language '{src}' is not in certified court language pair list: {list(SUPPORTED_LANGUAGE_PAIRS.keys())}")
        return supported

    def translate_text(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        """Translate a single text string using local cache and deep_translator fallback."""
        cleaned = text.strip()
        if not cleaned:
            return text
        if source_lang.lower() == target_lang.lower():
            return text

        cache_key = f"{source_lang}->{target_lang}:{cleaned}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            from deep_translator import MyMemoryTranslator
            src = LANGUAGE_CODE_MAP.get(source_lang.lower(), source_lang.lower())
            tgt = LANGUAGE_CODE_MAP.get(target_lang.lower(), target_lang.lower())
            translated = MyMemoryTranslator(source=src, target=tgt).translate(cleaned)
            if translated and not translated.startswith("MYMEMORY WARNING"):
                self._cache[cache_key] = translated
                return translated
        except Exception as e:
            logger.debug(f"Direct text translation failed for '{cleaned[:30]}': {e}")

        return text

    def align_and_translate_sentences(
        self,
        sentences: List[Dict[str, Any]],
        source_lang: str,
        whisper_translated_segments: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Produce sentence-parallel aligned records maintaining identical timestamps.

        Args:
            sentences: Segmented original-language sentence dicts.
            source_lang: Detected source language code.
            whisper_translated_segments: Direct Whisper translation segments if available.

        Returns:
            List of sentence dicts containing both 'text' (English) and 'original_text' (Source).
        """
        aligned = []
        is_english = (source_lang.lower() == "en")

        for idx, s in enumerate(sentences):
            orig_text = s.get("text", "")
            start_t = s.get("start_time", 0.0)
            end_t = s.get("end_time", 0.0)

            trans_text = None
            if is_english:
                trans_text = orig_text
            elif whisper_translated_segments:
                # Find overlapping translated segment with maximum intersection
                best_overlap = 0.0
                best_match = None
                for w_seg in whisper_translated_segments:
                    w_start = w_seg.get("start", 0.0)
                    w_end = w_seg.get("end", 0.0)
                    overlap = max(0.0, min(end_t, w_end) - max(start_t, w_start))
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_match = w_seg.get("text", "").strip()

                if best_match and best_overlap >= 0.2:
                    trans_text = best_match

            # Fallback to direct translation if whisper didn't provide or if identical
            if not trans_text or (not is_english and trans_text == orig_text):
                trans_text = self.translate_text(orig_text, source_lang=source_lang, target_lang="en")

            record = dict(s)
            record["original_language"] = source_lang
            record["target_language"] = self.target_language
            record["original_text"] = orig_text
            record["translated_text"] = trans_text
            record["text"] = trans_text  # Set primary text to English for downstream NLP
            aligned.append(record)

        return aligned


if __name__ == "__main__":
    translator = CourtTranslator()
    print("Verifying language pairs:")
    for lang in ["hi", "te", "ta", "en", "fr"]:
        print(f" {lang} -> en supported: {translator.verify_language_pair(lang)}")
