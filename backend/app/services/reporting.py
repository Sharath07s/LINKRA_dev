"""
M1.14 — ReportingService

Aggregates VERIFIED information for a specific investigation.

Data sources:
  - PostgreSQL (authoritative): Investigation, InvestigationEntity, CanonicalEntity,
    EntityRelationship, EntityCandidate, IngestionJob
  - Neo4j (projection/analytics): degree, anomalies, potential links

Rules:
  - No intelligence is invented.
  - Missing data → explicit empty list / None, never a fabricated value.
  - No full-graph traversals — all Neo4j calls are bounded per entity.
  - Relationships fetched only for entities belonging to the investigation.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.investigation import Investigation, InvestigationEntity
from app.models.resolution import CanonicalEntity
from app.models.relationship import EntityRelationship
from app.models.ingestion import EntityCandidate, IngestionJob
from app.schemas.report import (
    ReportResponse, ReportInvestigationSummary, ReportEntity,
    ReportRelationship, ReportEvidence, ReportGraphSummary,
    ReportGraphEntitySummary, ReportAnomaly, ReportPotentialLink,
    ReportGenerationMetadata, ReportProvenance,
)
from app.ai.neo4j.analytics import neo4j_analytics
from app.ai.neo4j.anomaly import neo4j_anomaly
from app.ai.neo4j.predictions import neo4j_predictions

logger = logging.getLogger(__name__)


class ReportingService:

    @staticmethod
    def assemble(db: Session, investigation_id: str) -> ReportResponse:
        """
        Assemble a full report for a given investigation.
        Returns a ReportResponse with all available data. Empty sections are
        represented as empty lists, never fabricated.
        Raises ValueError if investigation not found.
        """
        # ── 1. Fetch Investigation ─────────────────────────────────
        try:
            inv_uuid = uuid.UUID(investigation_id)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid investigation UUID: {investigation_id}")

        inv = db.query(Investigation).filter(Investigation.id == inv_uuid).first()
        if not inv:
            raise ValueError(f"Investigation {investigation_id} not found")

        investigation_summary = ReportInvestigationSummary(
            investigation_id=str(inv.id),
            crime_id=str(inv.crime_id) if inv.crime_id else None,
            status=inv.status,
            priority=inv.priority,
            summary=inv.summary,
            started_at=inv.started_at.isoformat() if inv.started_at else None,
            completed_at=inv.completed_at.isoformat() if inv.completed_at else None,
        )

        # ── 2. Fetch Entities ─────────────────────────────────────
        inv_entities = (
            db.query(InvestigationEntity)
            .filter(InvestigationEntity.investigation_id == inv_uuid)
            .all()
        )

        entity_ids: List[uuid.UUID] = [ie.entity_id for ie in inv_entities]
        entity_id_strs: List[str] = [str(eid) for eid in entity_ids]

        # Build a quick lookup: uuid → CanonicalEntity
        canonical_map: dict[uuid.UUID, CanonicalEntity] = {}
        if entity_ids:
            rows = (
                db.query(CanonicalEntity)
                .filter(CanonicalEntity.id.in_(entity_ids))
                .all()
            )
            canonical_map = {e.id: e for e in rows}

        report_entities: List[ReportEntity] = []
        for eid in entity_ids:
            ce = canonical_map.get(eid)
            if ce:
                aliases = ce.aliases if isinstance(ce.aliases, list) else []
                attrs = ce.attributes if isinstance(ce.attributes, dict) else {}
                report_entities.append(ReportEntity(
                    entity_id=str(ce.id),
                    name=ce.name,
                    entity_type=ce.entity_type,
                    aliases=aliases,
                    attributes=attrs,
                ))

        # ── 3. Fetch Observed Relationships ───────────────────────
        report_relationships: List[ReportRelationship] = []
        if entity_ids:
            rels = (
                db.query(EntityRelationship)
                .filter(
                    or_(
                        EntityRelationship.source_entity_id.in_(entity_ids),
                        EntityRelationship.target_entity_id.in_(entity_ids),
                    )
                )
                .all()
            )

            # Pre-fetch all IngestionJob ids referenced
            job_ids = {r.ingestion_job_id for r in rels if r.ingestion_job_id}
            jobs_map: dict = {}
            if job_ids:
                jobs = db.query(IngestionJob).filter(IngestionJob.id.in_(job_ids)).all()
                jobs_map = {j.id: j for j in jobs}

            for rel in rels:
                src_name = canonical_map.get(rel.source_entity_id, None)
                tgt_name = canonical_map.get(rel.target_entity_id, None)

                provenance = None
                if rel.ingestion_job_id and rel.ingestion_job_id in jobs_map:
                    job = jobs_map[rel.ingestion_job_id]
                    provenance = ReportProvenance(
                        ingestion_job_id=str(job.id),
                        source_type=job.source_type,
                        file_name=job.file_name,
                        file_type=job.file_type,
                        page=rel.source_page,
                        row=rel.source_row,
                    )

                report_relationships.append(ReportRelationship(
                    source_entity_id=str(rel.source_entity_id),
                    source_entity_name=src_name.name if src_name else str(rel.source_entity_id),
                    target_entity_id=str(rel.target_entity_id),
                    target_entity_name=tgt_name.name if tgt_name else str(rel.target_entity_id),
                    relationship_type=rel.relationship_type,
                    confidence=rel.confidence,
                    extraction_method=rel.extraction_method,
                    event_timestamp=rel.event_timestamp.isoformat() if rel.event_timestamp else None,
                    provenance=provenance,
                ))

        # ── 4. Fetch Source Evidence (EntityCandidate provenance) ──
        report_evidence: List[ReportEvidence] = []
        if entity_ids:
            candidates = (
                db.query(EntityCandidate)
                .filter(EntityCandidate.resolved_to_id.in_(entity_ids))
                .all()
            )

            # Pre-fetch jobs for candidates
            cand_job_ids = {c.ingestion_job_id for c in candidates if c.ingestion_job_id}
            cand_jobs_map: dict = {}
            if cand_job_ids:
                cj = db.query(IngestionJob).filter(IngestionJob.id.in_(cand_job_ids)).all()
                cand_jobs_map = {j.id: j for j in cj}

            for cand in candidates:
                job = cand_jobs_map.get(cand.ingestion_job_id) if cand.ingestion_job_id else None
                provenance = None
                if job:
                    provenance = ReportProvenance(
                        ingestion_job_id=str(job.id),
                        source_type=job.source_type,
                        file_name=job.file_name,
                        file_type=job.file_type,
                        page=cand.source_page,
                        row=cand.source_row,
                    )

                entity_name = ""
                if cand.resolved_to_id and cand.resolved_to_id in canonical_map:
                    entity_name = canonical_map[cand.resolved_to_id].name

                report_evidence.append(ReportEvidence(
                    evidence_type="ENTITY_EXTRACTION",
                    title=f"'{cand.raw_text}' → {entity_name}" if entity_name else cand.raw_text,
                    description=(
                        f"Extracted via {cand.extraction_method} "
                        f"with {int((cand.confidence or 1.0) * 100)}% confidence. "
                        f"Resolution: {cand.resolution_status}."
                    ),
                    timestamp=None,
                    provenance=provenance,
                ))

        # ── 5. Neo4j: Structural Analytics ────────────────────────
        graph_entity_summaries: List[ReportGraphEntitySummary] = []
        for eid_str in entity_id_strs:
            ce = canonical_map.get(uuid.UUID(eid_str))
            entity_name = ce.name if ce else eid_str
            try:
                deg = neo4j_analytics.get_degree(eid_str)
                dist = neo4j_analytics.get_relationship_distribution(eid_str)
                graph_entity_summaries.append(ReportGraphEntitySummary(
                    entity_id=eid_str,
                    entity_name=entity_name,
                    degree=deg.get("total_degree", 0),
                    in_degree=deg.get("in_degree", 0),
                    out_degree=deg.get("out_degree", 0),
                    relationship_distribution=dist.get("distribution", []),
                ))
            except Exception as e:
                logger.warning(f"Neo4j analytics unavailable for {eid_str}: {e}")
                graph_entity_summaries.append(ReportGraphEntitySummary(
                    entity_id=eid_str,
                    entity_name=entity_name,
                    degree=0,
                ))

        graph_summary = ReportGraphSummary(
            total_entities_in_investigation=len(entity_ids),
            entity_summaries=graph_entity_summaries,
        )

        # ── 6. Neo4j: Anomalies ────────────────────────────────────
        report_anomalies: List[ReportAnomaly] = []
        for eid_str in entity_id_strs:
            ce = canonical_map.get(uuid.UUID(eid_str))
            entity_name = ce.name if ce else eid_str
            try:
                result = neo4j_anomaly.get_anomalies_for_entity(eid_str)
                if result.get("status") == "success":
                    for a in result.get("anomalies", []):
                        explanation = a.get("explanation") or {}
                        report_anomalies.append(ReportAnomaly(
                            anomaly_id=a.get("anomaly_id", f"anom-{eid_str}"),
                            entity_id=eid_str,
                            entity_name=entity_name,
                            anomaly_type=a.get("anomaly_type", "UNKNOWN"),
                            severity=a.get("severity", "UNKNOWN"),
                            score=a.get("score", 0.0),
                            observed_value=a.get("observed_value", 0.0),
                            baseline_value=a.get("baseline_value", 0.0),
                            reason=a.get("reason", ""),
                            interpretation=explanation.get("interpretation"),
                        ))
            except Exception as e:
                logger.warning(f"Neo4j anomaly unavailable for {eid_str}: {e}")

        # ── 7. Neo4j: Potential Links ──────────────────────────────
        report_potential_links: List[ReportPotentialLink] = []
        for eid_str in entity_id_strs:
            ce = canonical_map.get(uuid.UUID(eid_str))
            entity_name = ce.name if ce else eid_str
            try:
                result = neo4j_predictions.get_potential_links_for_entity(eid_str)
                if result.get("status") == "success":
                    for pl in result.get("potential_links", []):
                        signals = pl.get("signals", {})
                        explanation = pl.get("explanation", {})
                        report_potential_links.append(ReportPotentialLink(
                            source_entity_id=eid_str,
                            source_entity_name=entity_name,
                            target_entity_id=pl.get("target_entity_id", ""),
                            target_entity_name=pl.get("target_entity_name", ""),
                            target_entity_type=pl.get("target_entity_type", ""),
                            score=pl.get("score", 0.0),
                            common_neighbors=signals.get("common_neighbors", 0),
                            jaccard_similarity=signals.get("jaccard_similarity", 0.0),
                            preferential_attachment_normalized=signals.get("preferential_attachment_normalized", 0.0),
                            reason=explanation.get("reason", ""),
                        ))
            except Exception as e:
                logger.warning(f"Neo4j predictions unavailable for {eid_str}: {e}")

        # ── 8. Limitations ────────────────────────────────────────
        limitations: List[str] = []
        if not entity_ids:
            limitations.append("No entities are associated with this investigation. All analytical sections are empty.")
        if not report_relationships:
            limitations.append("No observed relationships found for the entities in this investigation.")
        if not report_evidence:
            limitations.append("No source evidence (ingestion provenance) found for the entities in this investigation.")
        if not report_anomalies:
            limitations.append("No structural anomalies detected for the entities in this investigation.")
        if not report_potential_links:
            limitations.append("No strong structural link candidates found for the entities in this investigation.")

        # ── 9. Metadata ───────────────────────────────────────────
        metadata = ReportGenerationMetadata(
            generated_at=datetime.now(timezone.utc).isoformat(),
            investigation_id=investigation_id,
            entity_count=len(report_entities),
            relationship_count=len(report_relationships),
            evidence_count=len(report_evidence),
            anomaly_count=len(report_anomalies),
            potential_link_count=len(report_potential_links),
        )

        return ReportResponse(
            investigation=investigation_summary,
            entities=report_entities,
            relationships=report_relationships,
            evidence=report_evidence,
            graph_summary=graph_summary,
            anomalies=report_anomalies,
            potential_links=report_potential_links,
            ai_section=None,
            metadata=metadata,
            limitations=limitations,
        )
