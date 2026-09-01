"""
Tests for M1.3 — Data Ingestion + NLP Extraction.

Tests parsers, NLP extraction, validation, and provenance independently
(without requiring database or full API startup).
"""
import os
import json
import tempfile
import pytest
from pathlib import Path

# ── Test fixtures path ──────────────────────────────────────────────────
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ingestion"


# ═══════════════════════════════════════════════════════════════════════
# PARSER TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestTxtParser:
    def test_parse_valid_txt(self):
        from app.ingestion.parsers.txt_parser import parse_txt
        result = parse_txt(str(FIXTURES_DIR / "sample_fir.txt"))
        assert result.record_count == 1
        assert len(result.pages) == 1
        assert "Priya Sharma" in result.raw_text
        assert "Ravi Kumar" in result.raw_text
        assert "KA 01 AB 1234" in result.raw_text

    def test_parse_empty_txt(self):
        from app.ingestion.parsers.txt_parser import parse_txt
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("")
            f.flush()
            with pytest.raises(ValueError, match="empty"):
                parse_txt(f.name)
            os.unlink(f.name)

    def test_parse_missing_file(self):
        from app.ingestion.parsers.txt_parser import parse_txt
        with pytest.raises(FileNotFoundError):
            parse_txt("/nonexistent/file.txt")


class TestCsvParser:
    def test_parse_valid_csv(self):
        from app.ingestion.parsers.csv_parser import parse_csv
        result = parse_csv(str(FIXTURES_DIR / "sample_cdr.csv"))
        assert result.record_count == 5
        assert len(result.pages) == 5
        assert "caller" in result.metadata["headers"]
        # Verify structured fields are preserved
        first_row = result.pages[0].metadata["fields"]
        assert first_row["caller"] == "9876543210"

    def test_parse_empty_csv(self):
        from app.ingestion.parsers.csv_parser import parse_csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("")
            f.flush()
            with pytest.raises(ValueError, match="empty"):
                parse_csv(f.name)
            os.unlink(f.name)

    def test_parse_headers_only_csv(self):
        from app.ingestion.parsers.csv_parser import parse_csv
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("name,phone,location\n")
            f.flush()
            with pytest.raises(ValueError, match="no data rows"):
                parse_csv(f.name)
            os.unlink(f.name)


class TestJsonParser:
    def test_parse_valid_json_array(self):
        from app.ingestion.parsers.json_parser import parse_json
        result = parse_json(str(FIXTURES_DIR / "sample_records.json"))
        assert result.record_count == 3
        assert len(result.pages) == 3
        assert "Ravi Kumar" in result.raw_text

    def test_parse_single_json_object(self):
        from app.ingestion.parsers.json_parser import parse_json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"name": "Test Person", "location": "Delhi"}, f)
            f.flush()
            result = parse_json(f.name)
            assert result.record_count == 1
            assert "Test Person" in result.raw_text
            os.unlink(f.name)

    def test_parse_malformed_json(self):
        from app.ingestion.parsers.json_parser import parse_json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json content")
            f.flush()
            with pytest.raises(ValueError, match="Malformed JSON"):
                parse_json(f.name)
            os.unlink(f.name)

    def test_parse_empty_json(self):
        from app.ingestion.parsers.json_parser import parse_json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("")
            f.flush()
            with pytest.raises(ValueError, match="empty"):
                parse_json(f.name)
            os.unlink(f.name)


# ═══════════════════════════════════════════════════════════════════════
# NLP EXTRACTION TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestNLPExtraction:
    def test_extract_persons(self):
        from app.nlp.extractor import extract_entities
        text = "Ravi Kumar contacted Suresh Rao in Bengaluru."
        entities = extract_entities(text)
        person_entities = [e for e in entities if e.entity_type == "PERSON"]
        person_texts = [e.raw_text for e in person_entities]
        assert any("Ravi" in t for t in person_texts), f"Expected 'Ravi Kumar' in {person_texts}"

    def test_extract_locations(self):
        from app.nlp.extractor import extract_entities
        text = "The incident occurred in Bengaluru, Karnataka near Koramangala."
        entities = extract_entities(text)
        location_entities = [e for e in entities if e.entity_type == "LOCATION"]
        location_texts = [e.raw_text for e in location_entities]
        assert any("Bengaluru" in t or "Karnataka" in t for t in location_texts), \
            f"Expected location in {location_texts}"

    def test_extract_phones(self):
        from app.nlp.extractor import extract_entities
        text = "Contact number 9876543210 was found in the records."
        entities = extract_entities(text)
        phone_entities = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phone_entities) >= 1
        assert phone_entities[0].normalized_value == "9876543210"
        assert phone_entities[0].extraction_method == "regex"

    def test_extract_vehicles(self):
        from app.nlp.extractor import extract_entities
        text = "The motorcycle with registration KA 01 AB 1234 was seen."
        entities = extract_entities(text)
        vehicle_entities = [e for e in entities if e.entity_type == "VEHICLE"]
        assert len(vehicle_entities) >= 1
        assert "KA" in vehicle_entities[0].normalized_value

    def test_extract_dates(self):
        from app.nlp.extractor import extract_entities
        text = "The incident happened on 14 August 2026."
        entities = extract_entities(text)
        date_entities = [e for e in entities if e.entity_type == "DATE"]
        assert len(date_entities) >= 1

    def test_extract_from_empty_text(self):
        from app.nlp.extractor import extract_entities
        entities = extract_entities("")
        assert entities == []

    def test_provenance_offsets(self):
        from app.nlp.extractor import extract_entities
        text = "Call 9876543210 now."
        entities = extract_entities(text)
        phone_entities = [e for e in entities if e.entity_type == "PHONE"]
        assert len(phone_entities) >= 1
        ent = phone_entities[0]
        assert ent.start_offset is not None
        assert ent.end_offset is not None
        assert ent.start_offset < ent.end_offset

    def test_full_fir_extraction(self):
        """End-to-end: parse the sample FIR and extract entities."""
        from app.ingestion.parsers.txt_parser import parse_txt
        from app.nlp.extractor import extract_entities

        parsed = parse_txt(str(FIXTURES_DIR / "sample_fir.txt"))
        entities = extract_entities(parsed.raw_text)

        # Should find multiple entity types
        types_found = set(e.entity_type for e in entities)
        assert "PERSON" in types_found, f"Expected PERSON in {types_found}"
        assert "PHONE" in types_found, f"Expected PHONE in {types_found}"
        assert "VEHICLE" in types_found, f"Expected VEHICLE in {types_found}"
        assert len(entities) >= 5, f"Expected at least 5 entities, got {len(entities)}"


# ═══════════════════════════════════════════════════════════════════════
# VALIDATION TESTS
# ═══════════════════════════════════════════════════════════════════════

class TestValidation:
    def test_valid_pdf_extension(self):
        from app.ingestion.service import validate_file
        ext = validate_file("report.pdf", "application/pdf", 1024)
        assert ext == "pdf"

    def test_valid_csv_extension(self):
        from app.ingestion.service import validate_file
        ext = validate_file("data.csv", "text/csv", 512)
        assert ext == "csv"

    def test_unsupported_extension(self):
        from app.ingestion.service import validate_file
        with pytest.raises(ValueError, match="Unsupported file type"):
            validate_file("malware.exe", None, 1024)

    def test_empty_file(self):
        from app.ingestion.service import validate_file
        with pytest.raises(ValueError, match="empty"):
            validate_file("data.csv", "text/csv", 0)

    def test_oversized_file(self):
        from app.ingestion.service import validate_file
        with pytest.raises(ValueError, match="maximum size"):
            validate_file("huge.pdf", "application/pdf", 100 * 1024 * 1024)

    def test_missing_filename(self):
        from app.ingestion.service import validate_file
        with pytest.raises(ValueError, match="Filename"):
            validate_file("", None, 1024)

class TestPdfParser:
    def test_parse_valid_pdf(self):
        from app.ingestion.parsers.pdf_parser import parse_pdf
        result = parse_pdf(str(FIXTURES_DIR / "sample_document.pdf"))
        assert result.record_count > 0
        assert "FIRST INFORMATION REPORT" in result.raw_text
        assert "Rajesh Sharma" in result.raw_text
        assert "9876543210" in result.raw_text
        assert "KA 01 XY 9876" in result.raw_text

    def test_parse_missing_file(self):
        from app.ingestion.parsers.pdf_parser import parse_pdf
        with pytest.raises(FileNotFoundError):
            parse_pdf(str(FIXTURES_DIR / "nonexistent.pdf"))
