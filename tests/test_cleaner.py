"""Unit tests for legal transcript cleaner and sentence segmenter."""

import pytest
from src.preprocessing.cleaner import TranscriptCleaner
from src.preprocessing.segmenter import LegalSentenceSegmenter


def test_negation_preservation():
    cleaner = TranscriptCleaner()
    # Ensure critical legal negation tokens are strictly retained
    text = "The accused was not present and never signed the contract."
    cleaned, changes = cleaner.clean_text(text, "SENT_01")
    assert "not" in cleaned.lower()
    assert "never" in cleaned.lower()


def test_filler_disfluency_removal():
    cleaner = TranscriptCleaner(preserve_fillers=False)
    text = "The um, witness testified, testified that um, he saw the car."
    cleaned, changes = cleaner.clean_text(text, "SENT_02")
    assert "um" not in cleaned.lower()
    assert len(changes) > 0


def test_legal_abbreviation_segmentation():
    segmenter = LegalSentenceSegmenter()
    segments = [
        {
            "start": 0.0,
            "end": 10.0,
            "text": "In State v. Stewart, Hon. Judge Burch ruled in favor of Mr. Shelton. Bail was revoked."
        }
    ]
    sentences = segmenter.segment_transcript(segments)
    # Should not split on 'v.', 'Hon.', or 'Mr.'
    assert len(sentences) == 2
    assert "State v. Stewart" in sentences[0]["text"]
    assert "Bail was revoked" in sentences[1]["text"]
