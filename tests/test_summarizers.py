"""Unit tests for extractive summarizers (TF-IDF, TextRank, Embedding)."""

import pytest
from src.summarization.tfidf_summarizer import TfidfCourtSummarizer
from src.summarization.textrank_summarizer import TextRankCourtSummarizer
from src.summarization.embedding_summarizer import MultilingualEmbeddingSummarizer


@pytest.fixture
def mock_sentences():
    return [
        {"sentence_id": 1, "start_time": 0.0, "end_time": 5.0, "text": "Mr. Shelton, you are charged with first degree murder."},
        {"sentence_id": 2, "start_time": 5.5, "end_time": 12.0, "text": "The prosecution demands that bail be denied outright."},
        {"sentence_id": 3, "start_time": 12.5, "end_time": 15.0, "text": "I understand your honor."},
        {"sentence_id": 4, "start_time": 16.0, "end_time": 25.0, "text": "Under State v. Stewart, tangible evidence is required for pretrial detention."},
        {"sentence_id": 5, "start_time": 26.0, "end_time": 32.0, "text": "The court orders bail granted in the amount of five hundred thousand dollars."},
        {"sentence_id": 6, "start_time": 33.0, "end_time": 40.0, "text": "The defendant is held in direct contempt of court and remanded."}
    ]


def test_tfidf_summarizer_chronology(mock_sentences):
    summarizer = TfidfCourtSummarizer()
    res = summarizer.summarize(mock_sentences, summary_ratio=0.5, min_sentences=2, max_sentences=3)
    assert len(res["summary_sentences"]) <= 3
    # Check strict chronological ordering
    times = [s["start_time"] for s in res["summary_sentences"]]
    assert times == sorted(times)


def test_textrank_summarizer_chronology(mock_sentences):
    summarizer = TextRankCourtSummarizer()
    res = summarizer.summarize(mock_sentences, summary_ratio=0.5, min_sentences=2, max_sentences=3)
    assert len(res["summary_sentences"]) >= 2
    times = [s["start_time"] for s in res["summary_sentences"]]
    assert times == sorted(times)


def test_embedding_summarizer_chronology(mock_sentences):
    summarizer = MultilingualEmbeddingSummarizer()
    res = summarizer.summarize(mock_sentences, summary_ratio=0.5, min_sentences=2, max_sentences=3)
    assert len(res["summary_sentences"]) >= 2
    times = [s["start_time"] for s in res["summary_sentences"]]
    assert times == sorted(times)
