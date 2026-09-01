"""
Real NLP entity extraction using spaCy + regex patterns.

Extracts:
- PERSON (spaCy NER)
- ORGANIZATION (spaCy NER)
- LOCATION (spaCy NER: GPE + LOC)
- DATE (spaCy NER)
- PHONE (regex: Indian 10-digit numbers)
- VEHICLE (regex: Indian registration plates)

Each extraction includes provenance: offsets, confidence, extraction method.
"""
import re
import logging
from dataclasses import dataclass, field
from typing import Optional
from app.nlp.resolution.normalization import normalize_entity

logger = logging.getLogger(__name__)

# Lazy-load spaCy model to avoid import-time costs
_nlp = None


def _get_nlp():
    """Lazy-load the spaCy model."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy en_core_web_sm model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load spaCy model: {e}")
            raise RuntimeError(
                "spaCy model 'en_core_web_sm' is not available. "
                "Install it with: python -m spacy download en_core_web_sm"
            ) from e
    return _nlp


@dataclass
class ExtractedEntityCandidate:
    """A single extracted entity mention with provenance."""
    entity_type: str
    raw_text: str
    normalized_value: Optional[str] = None
    confidence: Optional[float] = None  # null if not provided by extractor
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    extraction_method: str = "spacy_ner"


# ── Regex patterns ──────────────────────────────────────────────────────

# Indian phone: 10 consecutive digits, optionally prefixed with +91 or 0
PHONE_PATTERN = re.compile(
    r'(?:\+91[\s-]?)?(?:0)?(\b\d{10}\b)',
    re.IGNORECASE
)

# Indian vehicle registration: e.g., KA 01 AB 1234, KA01AB1234, KA 01 A 1234
VEHICLE_PATTERN = re.compile(
    r'\b[A-Z]{2}\s?\d{1,2}\s?[A-Z]{1,3}\s?\d{4}\b',
    re.IGNORECASE
)

# SpaCy entity label → LINKRA entity type mapping
SPACY_LABEL_MAP = {
    "PERSON": "PERSON",
    "ORG": "ORGANIZATION",
    "GPE": "LOCATION",        # Geopolitical entities (cities, countries)
    "LOC": "LOCATION",        # Non-GPE locations (mountains, bodies of water)
    "DATE": "DATE",
}


def extract_entities(text: str, page_offset: int = 0) -> list[ExtractedEntityCandidate]:
    """
    Extract entity candidates from text using spaCy NER + regex.

    Args:
        text: The input text to process.
        page_offset: Character offset to add for multi-page provenance.

    Returns:
        List of ExtractedEntityCandidate objects.
    """
    if not text or not text.strip():
        return []

    candidates: list[ExtractedEntityCandidate] = []
    seen_spans: set[tuple[int, int]] = set()  # Avoid duplicate span overlaps

    # ── Regex: Phone numbers ────────────────────────────────────────────
    for match in PHONE_PATTERN.finditer(text):
        start = match.start() + page_offset
        end = match.end() + page_offset
        span_key = (start, end)

        if span_key in seen_spans:
            continue
        seen_spans.add(span_key)

        raw = match.group(0).strip()
        # Extract just the 10 digits
        digits = re.sub(r'\D', '', raw)
        if len(digits) >= 10:
            digits = digits[-10:]  # Take last 10 digits

        candidates.append(ExtractedEntityCandidate(
            entity_type="PHONE",
            raw_text=raw,
            normalized_value=digits,
            confidence=None,
            start_offset=start,
            end_offset=end,
            extraction_method="regex",
        ))

    # ── Regex: Vehicle registration numbers ─────────────────────────────
    for match in VEHICLE_PATTERN.finditer(text):
        start = match.start() + page_offset
        end = match.end() + page_offset
        span_key = (start, end)

        if span_key in seen_spans:
            continue
        seen_spans.add(span_key)

        raw = match.group(0).strip()
        normalized = re.sub(r'\s+', ' ', raw).upper()

        candidates.append(ExtractedEntityCandidate(
            entity_type="VEHICLE",
            raw_text=raw,
            normalized_value=normalized,
            confidence=None,
            start_offset=start,
            end_offset=end,
            extraction_method="regex",
        ))

    # ── spaCy NER extraction ────────────────────────────────────────────
    try:
        nlp = _get_nlp()
        doc = nlp(text)

        for ent in doc.ents:
            linkra_type = SPACY_LABEL_MAP.get(ent.label_)
            if linkra_type is None:
                continue  # Skip entity types we don't track

            raw = ent.text.strip()
            if not raw or len(raw) < 2:
                continue  # Skip single-char noise

            start = ent.start_char + page_offset
            end = ent.end_char + page_offset
            span_key = (start, end)

            # We don't just check exact span match, we check overlap with high-precision regexes
            overlap = False
            for seen_start, seen_end in seen_spans:
                if max(start, seen_start) < min(end, seen_end):
                    overlap = True
                    break
            
            if overlap:
                continue
            seen_spans.add(span_key)

            candidates.append(ExtractedEntityCandidate(
                entity_type=linkra_type,
                raw_text=raw,
                normalized_value=normalize_entity(linkra_type, raw),
                confidence=None,  # spaCy sm model doesn't provide per-entity confidence
                start_offset=start,
                end_offset=end,
                extraction_method="spacy_ner",
            ))
    except Exception as e:
        logger.error(f"spaCy NER extraction failed: {e}")

    return candidates
