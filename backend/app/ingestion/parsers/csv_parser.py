"""
CSV parser.
Parses headers, validates rows, normalizes column names, preserves source row identity.
"""
import csv
import io
import logging
from pathlib import Path
from app.ingestion.parsers import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)

MAX_ROWS = 50000  # Safety limit


def _normalize_column_name(name: str) -> str:
    """Normalize a column name: lowercase, strip, replace spaces with underscores."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def parse_csv(file_path: str) -> ParsedDocument:
    """
    Parse a CSV file.

    Each row becomes a ParsedPage with its fields serialized as text
    and preserved in metadata for structured extraction.

    Args:
        file_path: Path to the CSV file.

    Returns:
        ParsedDocument with one ParsedPage per CSV row.

    Raises:
        ValueError: If the CSV is empty, malformed, or has no headers.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Unable to read CSV file: {e}")

    if not raw_text.strip():
        raise ValueError("CSV file is empty.")

    reader = csv.DictReader(io.StringIO(raw_text))

    if not reader.fieldnames:
        raise ValueError("CSV file has no headers.")

    normalized_headers = [_normalize_column_name(h) for h in reader.fieldnames]

    pages: list[ParsedPage] = []
    all_text_parts: list[str] = []

    for row_idx, row in enumerate(reader, start=1):
        if row_idx > MAX_ROWS:
            logger.warning(f"CSV truncated at {MAX_ROWS} rows.")
            break

        # Build a normalized dict
        normalized_row = {}
        for orig_key, norm_key in zip(reader.fieldnames, normalized_headers):
            normalized_row[norm_key] = (row.get(orig_key) or "").strip()

        # Create a text representation for NLP processing
        text_parts = [f"{k}: {v}" for k, v in normalized_row.items() if v]
        row_text = ", ".join(text_parts)

        pages.append(ParsedPage(
            page_number=row_idx,
            text=row_text,
            metadata={"row_index": row_idx, "fields": normalized_row}
        ))
        all_text_parts.append(row_text)

    if not pages:
        raise ValueError("CSV file contains headers but no data rows.")

    return ParsedDocument(
        pages=pages,
        metadata={
            "headers": normalized_headers,
            "original_headers": list(reader.fieldnames),
        },
        record_count=len(pages),
        raw_text="\n".join(all_text_parts),
    )
