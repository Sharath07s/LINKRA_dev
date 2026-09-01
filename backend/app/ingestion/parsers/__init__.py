"""
Parsers for multi-source data ingestion.
Each parser returns a common ParsedDocument structure.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ParsedPage:
    """A single unit of parsed content (page, row, or record)."""
    page_number: int
    text: str
    metadata: dict = field(default_factory=dict)


@dataclass
class ParsedDocument:
    """Common output format for all parsers."""
    pages: list[ParsedPage]
    metadata: dict = field(default_factory=dict)
    record_count: int = 0
    raw_text: str = ""  # Full concatenated text for NLP
