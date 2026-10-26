"""Method C: Multilingual Semantic Embedding Extractive Summarizer.

Uses multilingual sentence transformers to map sentences into dense semantic vector space,
applying Maximal Marginal Relevance (MMR) and semantic centroid clustering for diverse coverage.
Employs lazy-loading and fast robust semantic fallback.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

from src.summarization.base import BaseSummarizer

logger = logging.getLogger("EmbeddingSummarizer")


class MultilingualEmbeddingSummarizer(BaseSummarizer):
    """Semantic extractive summarizer using dense multilingual embeddings with MMR."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        mmr_lambda: float = 0.65,
        use_clustering: bool = False
    ):
        super().__init__(name="Multilingual Embedding (MMR) Summarizer")
        self.model_name = model_name
        self.mmr_lambda = mmr_lambda
        self.use_clustering = use_clustering
        self._embedder = None
        self._load_attempted = False

    def _get_embedder(self):
        """Lazy load embedder on first call only."""
        if not self._load_attempted:
            self._load_attempted = True
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading embedding model: {self.model_name}...")
                self._embedder = SentenceTransformer(self.model_name)
                logger.info("SentenceTransformer loaded.")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Using TF-IDF semantic surrogate.")
                self._embedder = None
        return self._embedder

    def _encode_sentences(self, texts: List[str]) -> np.ndarray:
        """Encode list of sentence texts into 2D float32 numpy embedding matrix."""
        embedder = self._get_embedder()
        if embedder is not None:
            try:
                embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                return np.array(embeddings, dtype=np.float32)
            except Exception as e:
                logger.warning(f"Embedding encoding failed ({e}). Falling back to TF-IDF.")

        # Robust dense TF-IDF semantic surrogate
        from sklearn.feature_extraction.text import TfidfVectorizer
        try:
            vec = TfidfVectorizer(token_pattern=r'(?u)\b\w+\b', max_features=384)
            return vec.fit_transform(texts).toarray().astype(np.float32)
        except Exception:
            return np.ones((len(texts), 64), dtype=np.float32)

    def score_sentences(self, sentences: List[Dict[str, Any]]) -> List[float]:
        """Score sentences based on cosine similarity to proceeding global centroid."""
        n = len(sentences)
        if n == 0:
            return []
        if n == 1:
            return [1.0]

        texts = [(s.get("translated_text") or s.get("text", "")).strip() for s in sentences]
        embeddings = self._encode_sentences(texts)

        centroid = np.mean(embeddings, axis=0, keepdims=True)
        sims = cosine_similarity(embeddings, centroid).flatten()
        return [float(s) for s in sims]

    def summarize(
        self,
        sentences: List[Dict[str, Any]],
        summary_ratio: float = 0.25,
        min_sentences: int = 1,
        max_sentences: int = 8,
        judicial_only: bool = False
    ) -> Dict[str, Any]:
        """Extractive summary using Maximal Marginal Relevance (MMR) or Semantic Clustering."""
        if not sentences:
            return super().summarize(sentences, summary_ratio, min_sentences, max_sentences, judicial_only=judicial_only)

        total_sentences = len(sentences)
        min_s = 1 if judicial_only else min_sentences
        k = max(min_s, int(round(total_sentences * summary_ratio)))
        k = min(k, max_sentences, total_sentences)

        if judicial_only:
            base_scores = self.score_sentences(sentences)
            selected_sentences = BaseSummarizer.select_extractive_summary(
                sentences, base_scores, k=k, judicial_only=True
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

        texts = [(s.get("translated_text") or s.get("text", "")).strip() for s in sentences]
        embeddings = self._encode_sentences(texts)

        if self.use_clustering and total_sentences >= k:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)

            selected_indices = []
            for cluster_id in range(k):
                cluster_members = np.where(cluster_labels == cluster_id)[0]
                cluster_center = kmeans.cluster_centers_[cluster_id].reshape(1, -1)
                member_embeddings = embeddings[cluster_members]
                dists = cosine_similarity(member_embeddings, cluster_center).flatten()
                best_member = cluster_members[np.argmax(dists)]
                selected_indices.append(int(best_member))

            base_scores = self.score_sentences(sentences)

        else:
            centroid = np.mean(embeddings, axis=0, keepdims=True)
            doc_sims = cosine_similarity(embeddings, centroid).flatten()
            base_scores = [float(s) for s in doc_sims]

            sentence_pairwise_sim = cosine_similarity(embeddings, embeddings)

            selected_indices = []
            remaining_indices = list(range(total_sentences))

            for _ in range(k):
                if not remaining_indices:
                    break

                best_idx = -1
                best_mmr = -float('inf')

                for idx in remaining_indices:
                    relevance = doc_sims[idx]
                    if selected_indices:
                        redundancy = max(sentence_pairwise_sim[idx, prev] for prev in selected_indices)
                    else:
                        redundancy = 0.0

                    mmr_score = (self.mmr_lambda * relevance) - ((1.0 - self.mmr_lambda) * redundancy)

                    if mmr_score > best_mmr:
                        best_mmr = mmr_score
                        best_idx = idx

                if best_idx != -1:
                    selected_indices.append(best_idx)
                    remaining_indices.remove(best_idx)

        selected_indices.sort()

        selected_sentences = []
        summary_lines = []
        for idx in selected_indices:
            s = dict(sentences[idx])
            s["summarizer_score"] = round(base_scores[idx], 4)
            selected_sentences.append(s)
            summary_lines.append(f"[{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] {s['text']}")

        total_words = sum(s.get("word_count", len(s["text"].split())) for s in sentences)
        summary_words = sum(s.get("word_count", len(s["text"].split())) for s in selected_sentences)

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
