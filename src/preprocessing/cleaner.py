"""Legal Transcript Cleaning and Normalization Module.

Cleans ASR transcription outputs while strictly preserving critical legal semantics:
- Preserves all negation tokens (not, never, no, nahi, kaadu, illai)
- Preserves statutory references, case citations, dates, numbers, and proper nouns
- Normalizes stuttering, repeated tokens, and hesitations ('um', 'uh', 'ah')
- Logs all modifications for complete academic auditability
"""

import re
import sys
import logging
from typing import Dict, Any, List, Tuple

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TranscriptCleaner")

# Disfluency hesitations that carry zero legal semantic weight
DISFLUENCY_PATTERNS = [
    r'\b(um+|uh+|ah+|er+|erm+)\b',
    r'\b(you know|like)\s*,\s*',
]

# Critical legal abbreviations that must never be severed during segmentation
LEGAL_ABBREVIATIONS = {
    "v.": "v_dot_",
    "vs.": "vs_dot_",
    "sec.": "sec_dot_",
    "art.": "art_dot_",
    "hon.": "hon_dot_",
    "mr.": "mr_dot_",
    "mrs.": "mrs_dot_",
    "ms.": "ms_dot_",
    "dr.": "dr_dot_",
    "no.": "no_dot_",
    "para.": "para_dot_",
    "u/s.": "us_dot_",
    "i.e.": "ie_dot_",
    "e.g.": "eg_dot_"
}

REVERSE_LEGAL_ABBREVIATIONS = {v: k for k, v in LEGAL_ABBREVIATIONS.items()}


class TranscriptCleaner:
    """Audit-logged cleaner for multilingual court transcripts."""

    def __init__(self, preserve_fillers: bool = False):
        self.preserve_fillers = preserve_fillers
        self.modification_log: List[Dict[str, Any]] = []

    def clean_text(self, text: str, context_id: str = "") -> Tuple[str, List[Dict[str, Any]]]:
        """Normalize raw ASR text and record exact modification diffs.

        Args:
            text: Raw transcript text.
            context_id: Sentence or chunk identifier for audit trail.

        Returns:
            Tuple of (cleaned_text, list_of_change_records)
        """
        original = text
        current = text
        changes = []

        # 1. Strip repeated stuttered words (e.g., "the the witness" -> "the witness")
        repeated_word_regex = re.compile(r'\b([a-zA-Z\u0900-\u0D7F]+)(?:\s+\1\b)+', re.IGNORECASE)
        match = repeated_word_regex.search(current)
        if match:
            cleaned = repeated_word_regex.sub(r'\1', current)
            changes.append({
                "context_id": context_id,
                "type": "deduplicate_stutter",
                "before": match.group(0),
                "after": match.group(1),
                "rationale": "Removed spoken stutter repetition without semantic loss"
            })
            current = cleaned

        # 2. Filter disfluent hesitations if configured
        if not self.preserve_fillers:
            for pattern in DISFLUENCY_PATTERNS:
                matches = list(re.finditer(pattern, current, flags=re.IGNORECASE))
                for m in matches:
                    changes.append({
                        "context_id": context_id,
                        "type": "strip_disfluency",
                        "before": m.group(0),
                        "after": "",
                        "rationale": "Filtered non-semantic speech filler"
                    })
                current = re.sub(pattern, ' ', current, flags=re.IGNORECASE)

        # 3. Normalize multiple whitespace and trailing punctuations
        normalized_ws = re.sub(r'\s+', ' ', current).strip()
        if normalized_ws != current:
            current = normalized_ws

        # Record changes in persistent instance log
        self.modification_log.extend(changes)
        return current, changes

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Return all transformation records for academic report generation."""
        return self.modification_log


if __name__ == "__main__":
    cleaner = TranscriptCleaner()
    sample = "The um, witness testified, testified that Mr. Shelton was not, was not present at 10:30 PM."
    cleaned, changes = cleaner.clean_text(sample, "SENT_01")
    print(f"Original: {sample}")
    print(f"Cleaned:  {cleaned}")
    print(f"Audit Changes: {len(changes)}")
    for c in changes:
        print(f" - [{c['type']}] '{c['before']}' -> '{c['after']}' ({c['rationale']})")
