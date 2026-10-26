"""Unit tests for legal domain enhancer and allegation filter."""

import pytest
from src.summarization.legal_enhancer import LegalDomainEnhancer


def test_ruling_vs_allegation_segregation():
    enhancer = LegalDomainEnhancer()

    ruling_sent = "It is hereby ordered that bail is granted on personal recognizance."
    analysis_ruling = enhancer.analyze_sentence(ruling_sent, "en")
    assert analysis_ruling["is_ruling"] is True
    assert analysis_ruling["legal_type"] == "JUDICIAL_RULING"
    assert analysis_ruling["boost_factor"] > 1.0

    allegation_sent = "The prosecution alleges that the accused conspired with foreign actors."
    analysis_allegation = enhancer.analyze_sentence(allegation_sent, "en")
    assert analysis_allegation["is_allegation"] is True
    assert analysis_allegation["legal_type"] == "ADVOCATE_ALLEGATION"


def test_multilingual_legal_cues():
    enhancer = LegalDomainEnhancer()

    # Hindi ruling
    hi_sent = "अदालत आरोपी को पचास हजार के मुचलके पर सशर्त जमानत प्रदान करती है।"
    analysis_hi = enhancer.analyze_sentence(hi_sent, "hi")
    assert analysis_hi["boost_factor"] > 1.0

    # Telugu statutory
    te_sent = "సెక్షన్ 211 ఐపీసీ ప్రకారం దర్యాప్తు అధికారిపై విచారణ జరగాలి."
    analysis_te = enhancer.analyze_sentence(te_sent, "te")
    assert analysis_te["boost_factor"] > 1.0
