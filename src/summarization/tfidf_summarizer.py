"""Method A: TF-IDF Extractive Summarizer with Legal Position Priors.

Scores sentences based on term frequency-inverse document frequency weights
with court-specific positional biases (salience in opening charges and closing rulings).
"""

import math
import logging
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer

from src.summarization.base import BaseSummarizer

logger = logging.getLogger("TfidfSummarizer")


class TfidfCourtSummarizer(BaseSummarizer):
    """Frequency-based extractive summarizer with domain position weighting."""

    def __init__(self, position_weight: float = 0.25, min_df: int = 1):
        super().__init__(name="TF-IDF Extractive Summarizer")
        self.position_weight = position_weight
        self.min_df = min_df

    def score_sentences(self, sentences: List[Dict[str, Any]]) -> List[float]:
        """Compute TF-IDF salience score for each sentence."""
        if not sentences:
            return []

        # Prioritize English translated text when available
        raw_texts = [(s.get("translated_text") or s.get("text", "")).strip() for s in sentences]
        n_sentences = len(sentences)

        # Handle degenerate single-sentence cases
        if n_sentences == 1:
            return [1.0]

        try:
            vectorizer = TfidfVectorizer(
                lowercase=True,
                token_pattern=r'(?u)\b\w+\b',
                min_df=self.min_df,
                stop_words='english'
            )
            tfidf_matrix = vectorizer.fit_transform(raw_texts)
        except ValueError:
            # Fallback if vocabulary is completely empty or all stop words
            return [1.0 / n_sentences] * n_sentences

        scores = []
        for idx in range(n_sentences):
            row = tfidf_matrix.getrow(idx)
            # Average non-zero TF-IDF weight
            if row.nnz > 0:
                mean_tfidf = float(row.data.mean())
            else:
                mean_tfidf = 0.0

            # Positional prior: In court hearings, the opening 15% (charges/issues)
            # and closing 15% (ruling/disposition) carry higher legal salience
            pos_ratio = idx / max(1, n_sentences - 1)
            if pos_ratio <= 0.15:
                pos_factor = 1.0 + self.position_weight * (1.0 - (pos_ratio / 0.15))
            elif pos_ratio >= 0.85:
                pos_factor = 1.0 + self.position_weight * ((pos_ratio - 0.85) / 0.15)
            else:
                pos_factor = 1.0

            # Length normalization: Penalize overly short (<= 3 words) or overly verbose sentences
            word_count = max(1, sentences[idx].get("word_count", len(raw_texts[idx].split())))
            if word_count < 4:
                length_factor = 0.4
            elif word_count > 50:
                length_factor = 0.8
            else:
                length_factor = 1.0

            final_score = mean_tfidf * pos_factor * length_factor
            scores.append(final_score)

        return scores
