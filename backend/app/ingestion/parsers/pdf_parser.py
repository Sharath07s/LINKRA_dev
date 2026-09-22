"""
PDF parser using pypdf (already installed).
Extracts text from text-based PDFs, preserving page boundaries.
"""
import logging
from pathlib import Path
from pypdf import PdfReader
from app.ingestion.parsers import ParsedDocument, ParsedPage
import pytesseract
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)


def parse_pdf(file_path: str) -> ParsedDocument:
    """
    Parse a PDF file and extract text per page.

    Args:
        file_path: Path to the PDF file.

    Returns:
        ParsedDocument with one ParsedPage per PDF page.

    Raises:
        ValueError: If the PDF is empty, unreadable, or image-only.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
    except Exception as e:
        raise ValueError(f"Unable to read PDF file: {e}")

    if len(reader.pages) == 0:
        raise ValueError("PDF file contains no pages.")

    pages: list[ParsedPage] = []
    all_text_parts: list[str] = []
    empty_page_count = 0
    pdf_images = None

    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            logger.warning(f"Failed to extract text from page {i + 1}: {e}")
            text = ""

        text = text.strip()
        
        if len(text) < 50:
            logger.info(f"Page {i + 1} has insufficient text ({len(text)} chars). Falling back to OCR.")
            try:
                if pdf_images is None:
                    pdf_images = convert_from_path(file_path)
                
                if i < len(pdf_images):
                    ocr_text = pytesseract.image_to_string(pdf_images[i])
                    ocr_text = ocr_text.strip()
                    if ocr_text:
                        text = ocr_text
                        logger.info(f"Successfully extracted {len(text)} chars via OCR for page {i + 1}.")
                    else:
                        logger.warning(f"OCR yielded no text for page {i + 1}.")
                else:
                    logger.warning(f"Could not find image representation for page {i + 1}.")
            except Exception as e:
                logger.error(f"OCR fallback failed for page {i + 1}: {e}")

        if not text:
            empty_page_count += 1

        pages.append(ParsedPage(
            page_number=i + 1,
            text=text,
            metadata={"page_index": i}
        ))
        all_text_parts.append(text)

    raw_text = "\n\n".join(all_text_parts).strip()

    if not raw_text:
        raise ValueError(
            "PDF contains no extractable text and OCR fallback failed."
        )

    metadata = {
        "total_pages": len(reader.pages),
        "empty_pages": empty_page_count,
    }
    if reader.metadata:
        if reader.metadata.title:
            metadata["title"] = reader.metadata.title
        if reader.metadata.author:
            metadata["author"] = reader.metadata.author

    return ParsedDocument(
        pages=pages,
        metadata=metadata,
        record_count=len(reader.pages),
        raw_text=raw_text,
    )
