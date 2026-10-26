"""Phase 8: Legal Domain Salience Enhancement and Allegation Segregation Module.

Applies domain-specific lexical cue weighting, strict negation integrity checks,
and formal segregation between advocate allegations and authoritative judicial rulings.
"""

import re
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Guarantee UTF-8 output encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LegalEnhancer")


class LegalDomainEnhancer:
    """Legal domain rules engine for boosting salience and preventing misrepresentation."""

    def __init__(self, lexicon_path: str = "configs/legal_lexicon.json"):
        self.lexicon_path = Path(lexicon_path)
        self.lexicon = self._load_lexicon()
        self.audit_log: List[Dict[str, Any]] = []

    def _load_lexicon(self) -> Dict[str, Any]:
        """Load multilingual cue lexicon JSON."""
        if not self.lexicon_path.exists():
            logger.warning(f"Lexicon file {self.lexicon_path} not found. Using minimal fallback.")
            return {"cue_categories": {}, "negation_tokens": {}}
        with open(self.lexicon_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def analyze_sentence(
        self,
        sentence_text: str,
        language: str = "en",
        speaker: Optional[str] = None,
        speaker_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Examine sentence for legal cue triggers, negation markers, allegation status, and judicial rulings.

        Args:
            sentence_text: Candidate transcript sentence.
            language: Language ISO code ('en', 'hi', 'te', 'ta').
            speaker: Optional speaker label.
            speaker_role: Optional role of speaker (e.g., 'Judge', 'Defense Counsel').

        Returns:
            Dict containing boost factor, category tags, is_allegation flag, has_negation flag, is_ruling flag.
        """
        text_lower = sentence_text.lower()
        matched_categories = []
        cumulative_boost = 1.0
        is_allegation = False
        is_ruling = False

        # 1. Check if speaker or role indicates the presiding Judge / Court
        speaker_str = f"{speaker or ''} {speaker_role or ''}".lower()
        judge_identifiers = [
            "judge", "court", "magistrate", "bench", "justice", "presiding",
            "న్యాయమూర్తి", "జడ్జి", "अदालत", "न्यायाधीश", "நீதிபதி"
        ]
        is_judge_speaker = any(j in speaker_str for j in judge_identifiers)

        categories = self.lexicon.get("cue_categories", {})

        for cat_name, cat_data in categories.items():
            weight = cat_data.get("weight", 1.0)
            lang_phrases = cat_data.get("phrases", {}).get(language, [])
            # Also check English phrases as universal legal terms
            if language != "en":
                lang_phrases = lang_phrases + cat_data.get("phrases", {}).get("en", [])

            matches = []
            for phrase in lang_phrases:
                p_lower = phrase.lower()
                if p_lower in text_lower:
                    matches.append(p_lower)

            if matches:
                matched_categories.append({
                    "category": cat_name,
                    "matched_phrases": matches,
                    "weight": weight
                })
                cumulative_boost *= weight
                if cat_data.get("is_allegation", False):
                    is_allegation = True
                if "ruling" in cat_name or "disposition" in cat_name:
                    is_ruling = True

        # Check for post-hearing transitional judgment phrases ("after hearing both parties", etc.)
        post_hearing_triggers = [
            "after hearing both parties", "having heard both sides", "having heard both parties",
            "having heard the learned counsel", "after hearing arguments", "after considering both",
            "ఇరు పక్షాల వాదనలు", "ఉభయ పక్షాల వాదనలు", "వాదనలు విన్న తర్వాత", "పరిశీలించిన తర్వాత",
            "తీర్పు ఇస్తున్నాను", "తీర్పు ప్రకటిస్తున్నాం", "ఆదేశిస్తున్నాను", "ఆదేశిస్తుంది",
            "दोनों पक्षों की दलीलें", "बहस सुनने के बाद", "अदालत आदेश देती है", "फैसला सुनाया जाता है",
            "இரு தரப்பு வாதங்களையும்", "தீர்ப்பளிக்கப்படுகிறது"
        ]
        has_post_hearing_phrase = any(trig in text_lower for trig in post_hearing_triggers)
        if has_post_hearing_phrase:
            is_ruling = True
            cumulative_boost = max(cumulative_boost, 6.0)

        # If speaker is Judge and sentence expresses orders, bail, conviction, or ruling
        if is_judge_speaker:
            if not is_allegation:
                is_ruling = True
                cumulative_boost = max(cumulative_boost, 5.0)

        # Check Negation
        neg_tokens = self.lexicon.get("negation_tokens", {}).get(language, [])
        if language != "en":
            neg_tokens = neg_tokens + self.lexicon.get("negation_tokens", {}).get("en", [])

        neg_matches = []
        for n_tok in neg_tokens:
            if re.search(r'\b' + re.escape(n_tok.lower()) + r'\b', text_lower):
                neg_matches.append(n_tok)

        has_negation = (len(neg_matches) > 0)

        # CORE DESIGN PRINCIPLE: Allegations must never be presented as court rulings
        if is_ruling:
            legal_type = "JUDICIAL_RULING"
            is_allegation = False
        elif is_allegation:
            legal_type = "ADVOCATE_ALLEGATION"
        else:
            legal_type = "TESTIMONY_OR_PROCEDURAL"

        return {
            "boost_factor": round(cumulative_boost, 3),
            "legal_type": legal_type,
            "is_allegation": is_allegation,
            "is_ruling": is_ruling,
            "has_negation": has_negation,
            "negation_tokens": neg_matches,
            "matched_categories": matched_categories
        }

    def boost_sentence_scores(
        self,
        sentences: List[Dict[str, Any]],
        base_scores: List[float],
        language: str = "en"
    ) -> Tuple[List[float], List[Dict[str, Any]]]:
        """Apply legal domain salience multipliers and annotate sentences with legal tags.

        Args:
            sentences: Ordered candidate sentence dicts.
            base_scores: Raw scores from summarizer algorithm (TF-IDF, TextRank, or Embedding).
            language: Language ISO code.

        Returns:
            Tuple of (boosted_scores, enriched_sentences)
        """
        boosted_scores = []
        enriched_sentences = []
        n_total = len(sentences)

        for idx, (sent, b_score) in enumerate(zip(sentences, base_scores)):
            speaker = sent.get("speaker")
            speaker_role = sent.get("speaker_role")
            timeline_pos = idx / max(1, n_total - 1)

            # Analyze primary text
            analysis = self.analyze_sentence(
                sent["text"],
                language=language,
                speaker=speaker,
                speaker_role=speaker_role
            )

            # Also analyze translated English text if available
            trans_txt = sent.get("translated_text")
            if trans_txt and trans_txt != sent["text"]:
                analysis_en = self.analyze_sentence(
                    trans_txt,
                    language="en",
                    speaker=speaker,
                    speaker_role=speaker_role
                )
                if analysis_en["is_ruling"]:
                    analysis["is_ruling"] = True
                    analysis["legal_type"] = "JUDICIAL_RULING"
                    analysis["boost_factor"] = max(analysis["boost_factor"], analysis_en["boost_factor"], 5.0)
                elif analysis_en["boost_factor"] > analysis["boost_factor"]:
                    analysis = analysis_en

            # Also check original text if different
            orig_txt = sent.get("original_text")
            if orig_txt and orig_txt != sent["text"]:
                analysis_orig = self.analyze_sentence(
                    orig_txt,
                    language=language,
                    speaker=speaker,
                    speaker_role=speaker_role
                )
                if analysis_orig["is_ruling"]:
                    analysis["is_ruling"] = True
                    analysis["legal_type"] = "JUDICIAL_RULING"
                    analysis["boost_factor"] = max(analysis["boost_factor"], analysis_orig["boost_factor"], 5.0)

            # Prioritize Judicial Ruling delivered after listening to both parties
            if analysis["is_ruling"]:
                # Post-hearing disposition bonus (later half of proceeding where judge gives final ruling)
                disposition_mult = 2.0 if timeline_pos >= 0.35 else 1.2
                enhanced_score = b_score * analysis["boost_factor"] * disposition_mult * 3.0
            elif analysis["is_allegation"]:
                # Downweight allegations relative to conclusive rulings
                enhanced_score = b_score * 0.4
            else:
                # Suppress conversational filler and pleasantries
                words = sent.get("text", "").split()
                if len(words) < 4:
                    enhanced_score = b_score * 0.1
                else:
                    enhanced_score = b_score * analysis["boost_factor"]

            boosted_scores.append(round(enhanced_score, 4))

            # Enrich sentence record with legal provenance
            enriched_sent = dict(sent)
            enriched_sent["legal_type"] = analysis["legal_type"]
            enriched_sent["is_allegation"] = analysis["is_allegation"]
            enriched_sent["is_ruling"] = analysis["is_ruling"]
            enriched_sent["has_negation"] = analysis["has_negation"]
            enriched_sent["legal_boost"] = analysis["boost_factor"]
            enriched_sentences.append(enriched_sent)

        return boosted_scores, enriched_sentences


if __name__ == "__main__":
    enhancer = LegalDomainEnhancer()
    samples = [
        "The prosecution claims that Mr. Shelton was not inside his vehicle.",
        "It is hereby ordered that bail is granted on a bond of fifty thousand dollars.",
        "The witness testified regarding the tire tracks."
    ]
    for s in samples:
        res = enhancer.analyze_sentence(s, "en")
        print(f"[{res['legal_type']}] Boost: {res['boost_factor']}x | Negation: {res['has_negation']} | '{s}'")
