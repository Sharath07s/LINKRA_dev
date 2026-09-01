import pytest
from app.nlp.llm_extractor import extract_entities_llm, LLMExtractedEntity, LLMExtractionResult
from unittest.mock import patch, MagicMock

@patch("app.nlp.llm_extractor.FallbackManager.execute_with_fallback")
def test_extract_entities_llm_success(mock_execute):
    mock_execute.return_value = {
        "result": LLMExtractionResult(
            entities=[
                LLMExtractedEntity(
                    entity_type="PERSON",
                    raw_text="John Doe",
                    evidence_text="John Doe was seen at the scene.",
                    confidence=0.9
                )
            ]
        ),
        "provider": "mocked"
    }
    
    text = "John Doe was seen at the scene."
    candidates = extract_entities_llm(text)
    
    assert len(candidates) == 1
    assert candidates[0].entity_type == "PERSON"
    assert candidates[0].raw_text == "John Doe"
    assert candidates[0].normalized_value == "john doe"
    assert candidates[0].confidence == 0.9
    assert candidates[0].extraction_method == "llm_semantic"

@patch("app.nlp.llm_extractor.FallbackManager.execute_with_fallback")
def test_extract_entities_llm_hallucination_rejection(mock_execute):
    # LLM returns evidence not found in text
    mock_execute.return_value = {
        "result": LLMExtractionResult(
            entities=[
                LLMExtractedEntity(
                    entity_type="PERSON",
                    raw_text="Jane Smith",
                    evidence_text="Jane Smith is a known associate.", # Not in text
                    confidence=0.9
                )
            ]
        ),
        "provider": "mocked"
    }
    
    text = "John Doe was seen at the scene."
    candidates = extract_entities_llm(text)
    
    # Entity should be rejected due to evidence not found
    assert len(candidates) == 0

@patch("app.nlp.llm_extractor.FallbackManager.execute_with_fallback")
def test_extract_entities_llm_low_confidence_rejection(mock_execute):
    mock_execute.return_value = {
        "result": LLMExtractionResult(
            entities=[
                LLMExtractedEntity(
                    entity_type="PERSON",
                    raw_text="John Doe",
                    evidence_text="John Doe",
                    confidence=0.4 # Below 0.5 threshold
                )
            ]
        ),
        "provider": "mocked"
    }
    
    text = "Maybe John Doe was there."
    candidates = extract_entities_llm(text)
    
    assert len(candidates) == 0

def test_extract_entities_llm_empty_text():
    assert extract_entities_llm("") == []
    assert extract_entities_llm("   ") == []
