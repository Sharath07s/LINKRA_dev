"""
JSON parser.
Supports both object-based and array-based JSON.
Validates structure and preserves source record identity.
"""
import json
import logging
from pathlib import Path
from app.ingestion.parsers import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)

MAX_RECORDS = 50000  # Safety limit


def parse_json(file_path: str) -> ParsedDocument:
    """
    Parse a JSON file.

    Supports:
    - A single JSON object (treated as 1 record)
    - A JSON array of objects (each element is a record)

    Args:
        file_path: Path to the JSON file.

    Returns:
        ParsedDocument with one ParsedPage per JSON record.

    Raises:
        ValueError: If the JSON is malformed, empty, or not an object/array.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        raw_text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Unable to read JSON file: {e}")

    if not raw_text.strip():
        raise ValueError("JSON file is empty.")

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON: {e}")

    # Normalize to a list of records
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError(f"Unsupported JSON structure: expected object or array, got {type(data).__name__}")

    if not records:
        raise ValueError("JSON array is empty.")

    if len(records) > MAX_RECORDS:
        logger.warning(f"JSON truncated at {MAX_RECORDS} records.")
        records = records[:MAX_RECORDS]

    pages: list[ParsedPage] = []
    all_text_parts: list[str] = []

    for idx, record in enumerate(records, start=1):
        if isinstance(record, dict):
            # Create text representation from key-value pairs
            text_parts = []
            for k, v in record.items():
                if v is not None and str(v).strip():
                    text_parts.append(f"{k}: {v}")
            record_text = ", ".join(text_parts)
        else:
            record_text = str(record)

        pages.append(ParsedPage(
            page_number=idx,
            text=record_text,
            metadata={"record_index": idx, "fields": record if isinstance(record, dict) else {"value": record}}
        ))
        all_text_parts.append(record_text)

    return ParsedDocument(
        pages=pages,
        metadata={"total_records": len(records)},
        record_count=len(records),
        raw_text="\n".join(all_text_parts),
    )
