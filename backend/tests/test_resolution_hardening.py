import pytest
from app.nlp.resolution.matching import score_match
from app.nlp.resolution.schemas import ResolutionContext
from tests.fixtures.resolution_data import (
    get_test_candidate_ravi,
    get_test_canonical_ravi,
    get_test_canonical_ravi_diff_phone
)
from app.models.ingestion import EntityCandidate

def test_score_match_case_a_exact_match_with_phone():
    """Case A: Exact name match, matching phone -> AUTO_MATCHED"""
    candidate = get_test_candidate_ravi()
    canonical = get_test_canonical_ravi()
    context = ResolutionContext(phones=["9876543210"])
    
    result = score_match(candidate, context, canonical)
    
    assert result["decision"] == "AUTO_MATCHED"
    assert result["veto"] is False
    assert result["score"] >= 0.8  # Name (0.5) + Phone (0.3)
    assert result["signals"]["name_similarity"] == 1.0
    assert result["signals"]["phone_match"] == 1.0


def test_score_match_case_b_phone_conflict():
    """Case B: Exact name match, explicitly conflicting phone -> VETO -> REVIEW_REQUIRED"""
    candidate = get_test_candidate_ravi()
    canonical = get_test_canonical_ravi_diff_phone()
    # Candidate context has a phone, but it differs from canonical's 9988776655
    context = ResolutionContext(phones=["9876543210"])
    
    result = score_match(candidate, context, canonical)
    
    assert result["veto"] is True
    assert result["decision"] == "REVIEW_REQUIRED"
    assert "Explicit phone mismatch" in result["reason"]

def test_score_match_case_c_name_only():
    """Case C: Name only match, no context -> CREATE_NEW or REVIEW depending on threshold"""
    candidate = EntityCandidate(
        entity_type="PERSON",
        raw_text="R. Kumar",
        normalized_value="R. Kumar"
    )
    canonical = get_test_canonical_ravi()  # Name is "Ravi Kumar"
    context = ResolutionContext()  # No context
    
    result = score_match(candidate, context, canonical)
    
    assert result["veto"] is False
    # R. Kumar vs Ravi Kumar is < 1.0 name similarity. Max score = ~0.35
    # Threshold for CREATE_NEW is < 0.65.
    assert result["decision"] == "CREATE_NEW"

def test_score_match_explicit_phone_entity():
    """Testing that exact phone entity matches bypass weighted logic."""
    candidate = EntityCandidate(
        entity_type="PHONE",
        normalized_value="9876543210"
    )
    canonical = CanonicalEntity(
        entity_type="PHONE",
        name="9876543210"
    )
    context = ResolutionContext()
    
    result = score_match(candidate, context, canonical)
    assert result["decision"] == "AUTO_MATCHED"
    assert result["score"] == 1.0

def test_score_match_temporal_penalty():
    """Temporal differences should apply a penalty, not a hard veto."""
    candidate = get_test_candidate_ravi()
    canonical = get_test_canonical_ravi()
    canonical.attributes["dates"] = ["2026-08-01"]
    
    context = ResolutionContext(phones=["9876543210"], dates=["2026-08-02"])
    
    result = score_match(candidate, context, canonical)
    
    assert result["veto"] is False
    assert result["signals"]["temporal_penalty"] > 0
    # Score should be Name(0.5) + Phone(0.3) - Penalty(0.1) = 0.70 -> REVIEW_REQUIRED
    assert result["decision"] == "REVIEW_REQUIRED"
    
# Add mock CanonicalEntity for testing
from app.models.resolution import CanonicalEntity
