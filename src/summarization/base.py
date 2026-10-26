"""Abstract Base Class for Extractive Court Summarizers.

Enforces strict extractiveness, chronological order preservation,
and uniform evaluation scoring interfaces across all algorithms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseSummarizer(ABC):
    """Abstract base class ensuring all summarizers produce strictly extractive results."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def score_sentences(self, sentences: List[Dict[str, Any]]) -> List[float]:
        """Compute salience importance score for each candidate sentence.

        Args:
            sentences: List of sentence dicts containing 'sentence_id', 'text', 'start_time', etc.

        Returns:
            List of float scores corresponding index-wise to input sentences.
        """
        pass

    @staticmethod
    def select_extractive_summary(
        sentences: List[Dict[str, Any]],
        scores: List[float],
        k: int,
        diversity_threshold: float = 0.45,
        judicial_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Select top-k extractive summary sentences with:
        1. Strict non-repetition (no identical words or near-duplicate sentences)
        2. Representation of authoritative judicial determinations / rulings
        3. Strict preservation of chronological order and timestamp anchoring
        4. Focus on judgmental words / judicial rulings after hearing both parties when requested
        """
        import re

        if not sentences:
            return []

        total_s = len(sentences)
        k = min(k, total_s)

        # Step 1: Pre-process candidates for substance and token signature
        valid_pool = []
        for idx, s in enumerate(sentences):
            text = (s.get("translated_text") or s.get("text") or "").strip()
            orig = (s.get("original_text") or s.get("text") or "").strip()

            # Tokenize for lexical similarity & substance
            words = [w.lower() for w in re.findall(r'\b\w+\b', text) if len(w) > 1]
            is_ruling = s.get("is_ruling", False) or s.get("legal_type") == "JUDICIAL_RULING"
            is_allegation = s.get("is_allegation", False) or s.get("legal_type") == "ADVOCATE_ALLEGATION"

            # Filter trivial 1-2 word conversational fillers unless legally critical
            if len(words) < 3 and not (is_ruling or is_allegation):
                continue

            score = scores[idx] if idx < len(scores) else 0.0
            valid_pool.append({
                "orig_idx": idx,
                "sent": s,
                "score": score,
                "words": words,
                "norm_text": " ".join(words),
                "is_ruling": is_ruling,
                "start_time": s.get("start_time", 0.0),
                "end_time": s.get("end_time", 0.0)
            })

        if not valid_pool:
            return [dict(s, final_salience_score=round(scores[i], 4) if i < len(scores) else 1.0) for i, s in enumerate(sentences[:k])]

        selected = []
        selected_indices = set()
        selected_signatures = []

        def is_redundant(cand_words, cand_norm) -> bool:
            cand_set = set(cand_words)
            for prev_words, prev_norm in selected_signatures:
                if cand_norm == prev_norm:
                    return True
                prev_set = set(prev_words)
                intersection = cand_set & prev_set
                union = cand_set | prev_set
                if union:
                    jaccard = len(intersection) / len(union)
                    if jaccard >= diversity_threshold:
                        return True
            return False

        # --- SPECIAL JUDICIAL RULING FOCUS ---
        # When judicial rulings exist or judicial_only is requested:
        # Prioritize the authoritative judgment / rulings delivered after hearing both parties.
        ruling_candidates = [item for item in valid_pool if item["is_ruling"]]

        if judicial_only and ruling_candidates:
            # Sort judicial rulings by score descending (most definitive rulings first)
            ruling_candidates.sort(key=lambda x: x["score"], reverse=True)
            for cand in ruling_candidates:
                if not is_redundant(cand["words"], cand["norm_text"]):
                    selected.append(cand)
                    selected_indices.add(cand["orig_idx"])
                    selected_signatures.append((cand["words"], cand["norm_text"]))
                    if len(selected) >= k:
                        break

            # If judicial_only is requested and we selected rulings, return them chronologically
            if selected:
                selected.sort(key=lambda x: x["start_time"])
                return [dict(item["sent"], final_salience_score=round(item["score"], 4)) for item in selected]

        # First guarantee inclusion of any authoritative judicial rulings
        if ruling_candidates:
            ruling_candidates.sort(key=lambda x: x["score"], reverse=True)
            for cand in ruling_candidates:
                if not is_redundant(cand["words"], cand["norm_text"]):
                    selected.append(cand)
                    selected_indices.add(cand["orig_idx"])
                    selected_signatures.append((cand["words"], cand["norm_text"]))
                    if len(selected) >= max(1, k // 2):
                        break

        # Step 2: Temporal Stratification Across Entire Video for remaining slots
        if len(selected) < k:
            t_start = valid_pool[0]["start_time"]
            t_end = max(item["end_time"] for item in valid_pool)
            duration = max(1.0, t_end - t_start)
            slots_left = k - len(selected)
            bin_size = duration / max(1, slots_left)

            # Sample the most salient, non-redundant point from each chronological bin
            for b in range(slots_left):
                b_low = t_start + b * bin_size
                b_high = t_start + (b + 1) * bin_size

                bin_candidates = [
                    item for item in valid_pool
                    if b_low <= item["start_time"] <= b_high and item["orig_idx"] not in selected_indices
                ]
                if not bin_candidates:
                    continue

                bin_candidates.sort(key=lambda x: x["score"], reverse=True)

                for cand in bin_candidates:
                    if not is_redundant(cand["words"], cand["norm_text"]):
                        selected.append(cand)
                        selected_indices.add(cand["orig_idx"])
                        selected_signatures.append((cand["words"], cand["norm_text"]))
                        break

        # Step 3: MMR fallback if slots still remain
        if len(selected) < k:
            remaining = [item for item in valid_pool if item["orig_idx"] not in selected_indices]
            while remaining and len(selected) < k:
                best_cand = None
                best_mmr_score = -float('inf')

                for cand in remaining:
                    cand_set = set(cand["words"])
                    max_sim = 0.0
                    for prev_words, _ in selected_signatures:
                        prev_set = set(prev_words)
                        inter = len(cand_set & prev_set)
                        un = len(cand_set | prev_set)
                        sim = (inter / un) if un > 0 else 0.0
                        if sim > max_sim:
                            max_sim = sim

                    if max_sim >= 0.70:
                        continue

                    mmr_score = cand["score"] - (0.50 * max_sim)
                    if mmr_score > best_mmr_score:
                        best_mmr_score = mmr_score
                        best_cand = cand

                if best_cand is None:
                    break

                selected.append(best_cand)
                selected_indices.add(best_cand["orig_idx"])
                selected_signatures.append((best_cand["words"], best_cand["norm_text"]))
                remaining.remove(best_cand)

        # Step 4: Sort back to strict chronological order
        selected.sort(key=lambda x: x["start_time"])

        final_summary = []
        for item in selected:
            s_dict = dict(item["sent"])
            s_dict["final_salience_score"] = round(item["score"], 4)
            final_summary.append(s_dict)

        return final_summary

    def summarize(
        self,
        sentences: List[Dict[str, Any]],
        summary_ratio: float = 0.25,
        min_sentences: int = 1,
        max_sentences: int = 8,
        judicial_only: bool = False
    ) -> Dict[str, Any]:
        """Generate extractive summary by selecting top-ranked sentences and ordering them chronologically.

        Args:
            sentences: Ordered list of candidate sentences from transcript.
            summary_ratio: Target proportion of sentences to extract (e.g. 0.25 = 25%).
            min_sentences: Lower bound on selected sentence count.
            max_sentences: Upper bound on selected sentence count.
            judicial_only: If True, focus strictly on judicial rulings and judgments after hearing both sides.

        Returns:
            Dict containing selected sentences, chronological summary text, and metadata.
        """
        if not sentences:
            return {
                "method": self.name,
                "summary_sentences": [],
                "summary_text": "",
                "sentence_count": 0,
                "compression_ratio": 0.0,
                "selected_ids": []
            }

        total_sentences = len(sentences)
        k = max(min_sentences, int(round(total_sentences * summary_ratio)))
        k = min(k, max_sentences, total_sentences)

        scores = self.score_sentences(sentences)
        selected_sentences = self.select_extractive_summary(
            sentences, scores, k=k, judicial_only=judicial_only
        )

        summary_lines = []
        for s in selected_sentences:
            txt = s.get("translated_text") or s.get("text", "")
            summary_lines.append(f"[{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] {txt}")

        total_words = sum(s.get("word_count", len(s.get("text", "").split())) for s in sentences)
        summary_words = sum(s.get("word_count", len(s.get("text", "").split())) for s in selected_sentences)
        compression = round(summary_words / max(1, total_words), 3)

        return {
            "method": self.name,
            "summary_sentences": selected_sentences,
            "summary_text": "\n".join(summary_lines),
            "sentence_count": len(selected_sentences),
            "total_candidate_sentences": total_sentences,
            "compression_ratio": compression,
            "selected_ids": [s["sentence_id"] for s in selected_sentences],
            "all_scores": [round(sc, 4) for sc in scores]
        }
