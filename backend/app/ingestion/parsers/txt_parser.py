"""
Plain text parser.
Reads UTF-8 text files with encoding error handling.
"""
import logging
from pathlib import Path
from app.ingestion.parsers import ParsedDocument, ParsedPage

logger = logging.getLogger(__name__)


def parse_txt(file_path: str) -> ParsedDocument:
    """
    Parse a plain text file.

    Args:
        file_path: Path to the text file.

    Returns:
        ParsedDocument with a single ParsedPage containing the full text.

    Raises:
        ValueError: If the file is empty or unreadable.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {file_path}")

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise ValueError(f"Unable to read text file: {e}")

    text = text.strip()
    if not text:
        raise ValueError("Text file is empty.")

    return ParsedDocument(
        pages=[ParsedPage(page_number=1, text=text)],
        metadata={"encoding": "utf-8", "file_size": path.stat().st_size},
        record_count=1,
        raw_text=text,
    )
