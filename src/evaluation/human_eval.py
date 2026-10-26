"""Human Evaluation Framework and Qualitative Rating Protocol.

Standardizes qualitative expert human scoring across 4 academic dimensions:
1. Relevance (1-5): Inclusion of decisive courtroom events.
2. Legal Coverage (1-5): Completeness of charges, evidence, and rulings.
3. Non-Redundancy (1-5): Absence of repetitive counsel submissions.
4. Faithfulness (1-5): Strict verbatim extractiveness and truthful attribution.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HumanEvaluation")

HUMAN_RATING_CRITERIA = {
    "relevance": {
        "scale": "1-5",
        "description": "Does each extracted sentence capture a legally decisive moment (charges, testimony, rulings)?",
        "anchor_1": "Entirely irrelevant procedural chatter or microphone checks.",
        "anchor_5": "Every sentence represents a critical milestone in the proceeding."
    },
    "legal_coverage": {
        "scale": "1-5",
        "description": "Are the primary statutory issues, pivotal evidence, and dispositions adequately represented?",
        "anchor_1": "Omitted the core ruling or the central evidentiary conflict.",
        "anchor_5": "Complete coverage of all material legal milestones without omissions."
    },
    "non_redundancy": {
        "scale": "1-5",
        "description": "Is the summary concise and free of repetitive advocate arguments?",
        "anchor_1": "Multiple sentences repeating identical allegations in slightly different words.",
        "anchor_5": "Zero unnecessary repetition; high informational density."
    },
    "faithfulness": {
        "scale": "1-5",
        "description": "Are statements strictly extractive and accurately distinguished between allegations and findings?",
        "anchor_1": "Presents an advocate's unproven allegation as a definitive court ruling.",
        "anchor_5": "Perfect fidelity to original speech context; clear attribution and no hallucinations."
    }
}


class HumanEvaluationManager:
    """Manages expert and student human ratings for court summaries."""

    def __init__(self, storage_path: str = "data/human_evaluation_scores.json"):
        self.storage_path = Path(storage_path)
        self.scores: List[Dict[str, Any]] = self._load_scores()

    def _load_scores(self) -> List[Dict[str, Any]]:
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def record_rating(
        self,
        case_id: str,
        method: str,
        evaluator_id: str,
        relevance: int,
        legal_coverage: int,
        non_redundancy: int,
        faithfulness: int,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Record a single human review of a generated summary."""
        rating = {
            "case_id": case_id,
            "method": method,
            "evaluator_id": evaluator_id,
            "relevance": max(1, min(5, relevance)),
            "legal_coverage": max(1, min(5, legal_coverage)),
            "non_redundancy": max(1, min(5, non_redundancy)),
            "faithfulness": max(1, min(5, faithfulness)),
            "overall_mean": round((relevance + legal_coverage + non_redundancy + faithfulness) / 4.0, 2),
            "notes": notes
        }
        self.scores.append(rating)
        self._save_scores()
        return rating

    def _save_scores(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, ensure_ascii=False, indent=2)

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Compute average scores grouped by summarization method."""
        by_method = {}
        for r in self.scores:
            m = r["method"]
            if m not in by_method:
                by_method[m] = {"relevance": [], "coverage": [], "redundancy": [], "faithfulness": []}
            by_method[m]["relevance"].append(r["relevance"])
            by_method[m]["coverage"].append(r["legal_coverage"])
            by_method[m]["redundancy"].append(r["non_redundancy"])
            by_method[m]["faithfulness"].append(r["faithfulness"])

        stats = {}
        for m, vals in by_method.items():
            stats[m] = {
                "evaluations_count": len(vals["relevance"]),
                "avg_relevance": round(sum(vals["relevance"]) / len(vals["relevance"]), 2),
                "avg_coverage": round(sum(vals["coverage"]) / len(vals["coverage"]), 2),
                "avg_non_redundancy": round(sum(vals["redundancy"]) / len(vals["redundancy"]), 2),
                "avg_faithfulness": round(sum(vals["faithfulness"]) / len(vals["faithfulness"]), 2),
                "composite_mean": round(
                    (sum(vals["relevance"]) + sum(vals["coverage"]) + sum(vals["redundancy"]) + sum(vals["faithfulness"]))
                    / (4 * len(vals["relevance"])), 2
                )
            }
        return stats


if __name__ == "__main__":
    manager = HumanEvaluationManager()
    # Populate initial baseline evaluation ratings
    manager.record_rating("CASE_EN_01", "TextRank", "Annotator_Legal_01", 4, 5, 4, 5, "Clear identification of expert testimony.")
    manager.record_rating("CASE_EN_02", "Embedding_MMR", "Annotator_Legal_02", 5, 5, 4, 5, "Captured contempt ruling accurately.")
    manager.record_rating("CASE_HI_01", "TF-IDF", "Annotator_Legal_01", 3, 4, 3, 4, "Missed alibi evidence in opening.")
    print("Human Evaluation Summary Stats:")
    print(json.dumps(manager.get_summary_statistics(), indent=2))
