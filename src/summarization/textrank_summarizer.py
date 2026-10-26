"""Method B: TextRank / LexRank Graph-Centrality Extractive Summarizer.

Builds a sentence affinity graph, computes PageRank centrality, and applies
greedy redundancy suppression to eliminate repetitive advocate submissions.
"""

import logging
import numpy as np
import networkx as nx
from typing import Dict, Any, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.summarization.base import BaseSummarizer

logger = logging.getLogger("TextRankSummarizer")


class TextRankCourtSummarizer(BaseSummarizer):
    """Graph-based extractive summarizer with PageRank and redundancy control."""

    def __init__(
        self,
        similarity_threshold: float = 0.10,
        damping: float = 0.85,
        redundancy_penalty: float = 0.30
    ):
        super().__init__(name="TextRank Graph Centrality Summarizer")
        self.similarity_threshold = similarity_threshold
        self.damping = damping
        self.redundancy_penalty = redundancy_penalty

    def score_sentences(self, sentences: List[Dict[str, Any]]) -> List[float]:
        """Compute graph-based PageRank centrality for candidate sentences."""
        n = len(sentences)
        if n == 0:
            return []
        if n == 1:
            return [1.0]

        # Prioritize English translated text when available for accurate graph centrality
        texts = [(s.get("translated_text") or s.get("text", "")).strip() for s in sentences]

        try:
            vectorizer = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', stop_words='english')
            tfidf = vectorizer.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf, tfidf)
        except Exception:
            # Fallback for empty vocabulary
            return [1.0 / n] * n

        # Construct NetworkX Graph
        graph = nx.Graph()
        for i in range(n):
            graph.add_node(i)

        for i in range(n):
            for j in range(i + 1, n):
                weight = float(sim_matrix[i, j])
                if weight >= self.similarity_threshold:
                    graph.add_edge(i, j, weight=weight)

        try:
            # Run PageRank on sentence similarity graph
            pagerank_scores = nx.pagerank(graph, alpha=self.damping, weight='weight', max_iter=200)
            raw_scores = [pagerank_scores.get(i, 0.0) for i in range(n)]
        except Exception as e:
            logger.warning(f"PageRank convergence issue: {e}. Falling back to uniform weights.")
            raw_scores = [1.0 / n] * n

        return raw_scores

    def summarize(
        self,
        sentences: List[Dict[str, Any]],
        summary_ratio: float = 0.25,
        min_sentences: int = 1,
        max_sentences: int = 8,
        judicial_only: bool = False
    ) -> Dict[str, Any]:
        """Extractive summary with whole-video temporal coverage, redundancy control, and post-hearing judgment focus."""
        if not sentences:
            return super().summarize(sentences, summary_ratio, min_sentences, max_sentences, judicial_only=judicial_only)

        total_sentences = len(sentences)
        min_s = 1 if judicial_only else min_sentences
        k = max(min_s, int(round(total_sentences * summary_ratio)))
        k = min(k, max_sentences, total_sentences)

        # Compute base PageRank scores
        base_scores = self.score_sentences(sentences)

        # Use unified temporal-stratified extractive selector with optional judicial ruling focus
        selected_sentences = BaseSummarizer.select_extractive_summary(
            sentences,
            base_scores,
            k=k,
            diversity_threshold=1.0 - self.redundancy_penalty,
            judicial_only=judicial_only
        )

        summary_lines = []
        for s in selected_sentences:
            txt = s.get("translated_text") or s.get("text", "")
            summary_lines.append(f"[{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] {txt}")

        total_words = sum(s.get("word_count", len(s.get("text", "").split())) for s in sentences)
        summary_words = sum(s.get("word_count", len(s.get("text", "").split())) for s in selected_sentences)

        return {
            "method": self.name,
            "summary_sentences": selected_sentences,
            "summary_text": "\n".join(summary_lines),
            "sentence_count": len(selected_sentences),
            "total_candidate_sentences": total_sentences,
            "compression_ratio": round(summary_words / max(1, total_words), 3),
            "selected_ids": [s["sentence_id"] for s in selected_sentences],
            "all_scores": [round(sc, 4) for sc in base_scores]
        }
