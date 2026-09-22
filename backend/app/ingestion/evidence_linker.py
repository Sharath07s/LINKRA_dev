"""
backend/app/ingestion/evidence_linker.py
========================================
Phase 2: Grounds knowledge graph relationships to their corresponding
RAG DocumentChunk rows in PostgreSQL by creating EvidenceLink records.
"""
import re
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.ingestion import IngestionJob
from app.models.relationship import EntityRelationship
from app.models.document import DocumentChunk
from app.models.evidence_link import EvidenceLink

logger = logging.getLogger(__name__)


def find_offsets_in_chunk(evidence_text: str, chunk_content: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Deterministically find the character span of evidence_text within chunk_content.
    Returns (char_start, char_end) if reliably found, or (None, None).
    """
    if not evidence_text or not chunk_content:
        return None, None

    # 1. Exact match
    idx = chunk_content.find(evidence_text)
    if idx != -1:
        return idx, idx + len(evidence_text)

    # 2. Case-insensitive exact match
    idx = chunk_content.lower().find(evidence_text.lower())
    if idx != -1:
        return idx, idx + len(evidence_text)

    # 3. Flexible whitespace match (handles newlines, extra spaces)
    words = evidence_text.strip().split()
    if words:
        pattern = r"\s+".join(re.escape(w) for w in words)
        match = re.search(pattern, chunk_content, re.IGNORECASE)
        if match:
            return match.start(), match.end()

    return None, None


def is_partial_spanning_match(evidence_text: str, chunk_content: str, min_chars: int = 20) -> Tuple[bool, Optional[int], Optional[int]]:
    """
    Detect if evidence text spans across chunk boundaries (overlap region).
    Checks if a substantial prefix or suffix of the evidence exists in the chunk.
    Returns (matched, char_start, char_end).
    """
    words = evidence_text.strip().split()
    if len(words) < 3 or len(evidence_text) < min_chars:
        return False, None, None

    # Check decreasing prefixes
    for k in range(len(words) - 1, 2, -1):
        sub_prefix = " ".join(words[:k])
        if len(sub_prefix) < min_chars:
            break
        start, end = find_offsets_in_chunk(sub_prefix, chunk_content)
        if start is not None:
            return True, start, end

    # Check decreasing suffixes
    for k in range(1, len(words) - 2):
        sub_suffix = " ".join(words[k:])
        if len(sub_suffix) < min_chars:
            continue
        start, end = find_offsets_in_chunk(sub_suffix, chunk_content)
        if start is not None:
            return True, start, end

    return False, None, None


def link_evidence_for_job(db: Session, job: IngestionJob) -> List[EvidenceLink]:
    """
    Creates EvidenceLink records linking EntityRelationships belonging to this
    ingestion job to the DocumentChunks containing the supporting evidence.

    Isolation guarantees:
    - Only matches DocumentChunks where metadata_json.ingestion_job_id == job.id.
    - Only matches chunks on the same page_number as the relationship's source_page.
    - Supports overlapping chunks by linking all valid matching chunks.
    """
    try:
        rels = (
            db.query(EntityRelationship)
            .filter(EntityRelationship.ingestion_job_id == job.id)
            .all()
        )
        if not rels:
            logger.info(f"Ingestion job {job.id}: No EntityRelationships to link.")
            return []

        chunks = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.metadata_json["ingestion_job_id"].as_string() == str(job.id))
            .all()
        )
        if not chunks:
            logger.warning(f"Ingestion job {job.id}: No DocumentChunks found to link evidence to.")
            return []

        # Index chunks by page_number for fast, page-isolated lookup
        chunks_by_page: dict[int, list[DocumentChunk]] = {}
        for chunk in chunks:
            page_num = chunk.metadata_json.get("page_number")
            if page_num is not None:
                try:
                    p_int = int(page_num)
                    chunks_by_page.setdefault(p_int, []).append(chunk)
                except (ValueError, TypeError):
                    pass

        created_links: List[EvidenceLink] = []

        for rel in rels:
            if not rel.evidence_text or not rel.evidence_text.strip():
                continue

            # Identify target candidate chunks on the same page
            if rel.source_page is not None and rel.source_page in chunks_by_page:
                candidate_chunks = chunks_by_page[rel.source_page]
            else:
                # If source_page is missing or not indexed by page, check all job chunks
                candidate_chunks = chunks

            matched_chunk_ids = set()

            for chunk in candidate_chunks:
                # 1. Check complete match
                char_start, char_end = find_offsets_in_chunk(rel.evidence_text, chunk.content)
                if char_start is not None and char_end is not None:
                    link = EvidenceLink(
                        relationship_id=rel.id,
                        document_chunk_id=chunk.id,
                        char_start=char_start,
                        char_end=char_end,
                        quote_snippet=rel.evidence_text,
                        confidence=1.0,
                    )
                    created_links.append(link)
                    matched_chunk_ids.add(chunk.id)
                    continue

                # 2. Check spanning / boundary match
                is_spanning, span_start, span_end = is_partial_spanning_match(rel.evidence_text, chunk.content)
                if is_spanning:
                    link = EvidenceLink(
                        relationship_id=rel.id,
                        document_chunk_id=chunk.id,
                        char_start=span_start,
                        char_end=span_end,
                        quote_snippet=rel.evidence_text,
                        confidence=1.0,
                    )
                    created_links.append(link)
                    matched_chunk_ids.add(chunk.id)

            if not matched_chunk_ids:
                logger.info(
                    f"Ingestion job {job.id}: Relationship {rel.id} ({rel.relationship_type}) "
                    f"evidence_text not matched to any chunk on page {rel.source_page}."
                )

        if created_links:
            db.add_all(created_links)
            db.commit()
            logger.info(
                f"Ingestion job {job.id}: Created {len(created_links)} EvidenceLink(s) "
                f"grounding {len(rels)} relationship(s) into pgvector DocumentChunks."
            )

        return created_links

    except Exception as e:
        logger.error(f"Failed to create EvidenceLinks for ingestion job {job.id}: {e}", exc_info=True)
        # Never raise to break the main pipeline — return empty list
        return []
