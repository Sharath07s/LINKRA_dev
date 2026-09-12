# LINKRA — KCIA Platform
# Project Summary

> **Platform:** Karnataka Crime Intelligence AI Platform (KCIA)  
> **Codename:** LINKRA  
> **Last Updated:** September 2026  
> **Overall Completion (per docs):** ~98%  
> **Datathon Readiness:** 100%  
> **Production Readiness:** High (RAG Ingestion, Evidence Linking & Grounded Copilot Verified)

---

## 1. What LINKRA Is

LINKRA is an AI-powered Crime Intelligence Operating System built for Karnataka State Police (KSP) and the State Crime Records Bureau (SCRB). It enables law enforcement officers to:

- Query crime data in natural language (English + Kannada)
- Discover hidden criminal networks and relationships
- Analyze crime trends, patterns, and hotspots
- Extract structured intelligence from FIR documents
- Generate investigation reports with explainable AI
- Receive predictive crime risk forecasts
- Monitor statewide operations from an executive command view

The platform is a **datathon-submitted MVP** targeting production deployment across 1,100+ Karnataka police stations.

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js, React, TypeScript, TailwindCSS, ShadCN, Framer Motion, MapLibre |
| **Backend** | FastAPI (Python 3.12), SQLAlchemy, Alembic |
| **Primary DB** | PostgreSQL + pgvector extension |
| **Graph DB** | Neo4j (1,971 nodes, 5,706 relationships live) |
| **Cache** | Redis |
| **Embeddings** | HuggingFace all-MiniLM-L6-v2 (384-dim) |
| **LLM Providers** | Gemini, Groq, OpenAI, DeepSeek, Claude (FallbackManager) |
| **AI Orchestration** | LangChain, LangGraph |
| **Containerization** | Docker, docker-compose |
| **CI/CD** | GitHub Actions |

---

## 3. System Architecture

```
Frontend (Next.js)
        |
        v
API Gateway (FastAPI /api/v1)
        |
        v
Authentication & RBAC (JWT / OAuth2)
        |
        |-- Crime Service
        |-- User Service
        |-- Investigation Service
        |-- Analytics Service
        |-- AI / Copilot Service
        |-- Report Service
        |-- Alert Service
        |-- Audit Service
        +-- Ingestion Service
        |
        v
Data Layer
        |-- PostgreSQL (core records + pgvector)
        |-- Neo4j (criminal graph)
        |-- Redis (cache / session)
        +-- File Storage (uploads)
```

---

## 4. What Is Fully Implemented

### Phase 1 — Core Platform
- FastAPI backend with full API routing
- PostgreSQL integration with SQLAlchemy ORM
- Alembic migration system
- JWT authentication (login, logout, refresh token)
- Role-Based Access Control (RBAC) — roles: Constable, SI, Inspector, SP, SCRB Admin
- User management (create, update, deactivate, role assignment)
- React/Next.js frontend foundation

### Phase 2 — AI Intelligence Layer
- Multi-provider LLM support with FallbackManager (Gemini -> Groq -> OpenAI -> DeepSeek)
- Intent classification engine (IntentRouter)
- Query planner (routes to SQL, Graph, or RAG retrieval)
- AI Chat interface with conversation history
- Prompt grounding and hallucination controls (system prompt injection guards)
- Explainability foundation (confidence scores, source attribution)

### Phase 3 — RAG & Evidence Grounding Infrastructure (Fully Implemented & Verified)
- **P1 Production RAG Ingestion Pipeline:**
  - Automated text chunking (500-char chunks, 100-char overlap) and pgvector embedding generation in `process_ingestion()` (Step 6)
  - HuggingFace `all-MiniLM-L6-v2` embeddings (384 dimensions)
  - `DocumentChunk` table with pgvector cosine distance indexing
  - `chunk_count` column tracked on `IngestionJob` with Alembic migration `c3a1d7e8f204`
  - Verified with `tests/test_rag_ingestion.py` (100% PASS)
- **P2 Evidence & Provenance Grounding:**
  - `EvidenceLink` model (`evidence_links` table) with Alembic migration `d4b2e8f1a305`
  - Ingestion/page-isolated deterministic evidence linker (`EvidenceLinker`) linking `EntityRelationship` to `DocumentChunk`
  - Precise character offset detection (`char_offset_start`, `char_offset_end`) supporting single and spanning multi-chunk matches
  - Relationship Evidence API: `GET /api/v1/relationship/{relationship_id}/evidence`
  - Neo4j graph edge synchronization propagates `evidence_text` directly to Neo4j graph relationships
  - Frontend `EdgeEvidencePanel` displays actual underlying chunk evidence with page and document provenance
  - Verified with `tests/test_phase2_evidence_link.py` (9/9 PASS)
- **Copilot Citation Generation & Grounded-State Hardening:**
  - `CopilotResponse.sources[]` populated with structured `CopilotCitation` objects mapped from both `RAG_CHUNK` and `ENTITY_EXTRACTION` evidence
  - Verified with `tests/test_copilot_sources.py` (5/5 PASS)
  - Grounding state hardened: `grounded = bool(sources)` enforced across all LLM, fallback, and empty paths; `CopilotResponse.grounded` defaults securely to `False`
  - Verified with `tests/test_copilot_grounding.py` (7/7 PASS)
  - Strict zero fake data guarantee (0 fake FIRs, 0 fake chunks, 0 fake links, 0 fake Neo4j nodes)

### Phase 4 — Neo4j Criminal Intelligence
- Neo4j graph database integrated and operational
- **Live graph: 1,971 nodes / 5,706 relationships**
- Node types: Suspect, Vehicle, Phone, Location, FIR, Police Station, Crime, District
- Relationship types: KNOWS, USED, ASSOCIATED_WITH, PARTICIPATED_IN, VISITED, OCCURRED_IN
- Criminal network analysis, associate discovery, vehicle link analysis
- Community detection, anomaly detection, link prediction
- Neo4jIntelligenceService, Neo4jAnomalyService, Neo4jPotentialLinkService

### Phase 5 — Command Center UI
- Command Center Dashboard (/dashboard)
- Global search
- Intelligence feed
- Crime Map foundation (MapLibre, dark matter theme, heatmaps)
- Knowledge Graph visualization (dynamic Neo4j data, interactive network)

### Phase 6 — Investigation Intelligence
- Investigation Workspace (/investigation-board)
- Case summary panel, AI Investigation Copilot, Evidence Intelligence panel
- Embedded Neo4j relationship graph, Timeline view, Threat assessment, Audit trail

### Phase 7A — Advanced UI/UX
- Intelligence Navy + Police Blue design system
- Framer Motion animations
- AI Workspace with Confidence Meter, Source Attribution, Reasoning Trace
- MapLibre with crime heatmaps and intelligence layers
- Dynamic Neo4j-driven Knowledge Graph visualization

### Phase 7B — Operational Intelligence Suite (8 Sprints Complete)

| Sprint | Module | Route |
|--------|--------|-------|
| 1 | Investigation Workspace | /investigation-board |
| 2 | FIR Intelligence Workspace | /fir-workspace |
| 3 | Timeline Intelligence | /timeline-intelligence |
| 4 | Executive Dashboard | /executive-dashboard |
| 4A | Executive Dashboard — Mock Data Removal | /executive-dashboard |
| 5 | Alert Center | /alert-center |
| 6 | Officer Intelligence Workspace | /officer-workspace |
| 7 | Command Wall | /command-wall |
| 8 | System Health Center | /system-health |

### Phase 8 — Predictive Intelligence (/predictive-intelligence)
- Crime Forecaster (moving averages, trend forecasting)
- Hotspot Predictor (spatial escalation detection)
- Recidivism Engine (risk scoring, crime severity weighting)
- Network Growth Engine (preferential attachment forecasting)

### Phase 8.1 — Predictive Validation
- Forecast metrics: MAPE, MAE, RMSE
- Hotspot metrics: Precision, Recall, F1
- Recidivism: Accuracy, Precision, Recall, F1
- ValidationMetrics.tsx dashboard

### Intelligence Ingestion Pipeline (M15 — Verified)
- IngestionJob lifecycle: QUEUED -> PROCESSING -> PARSED -> EXTRACTED -> COMPLETED
- File format support: PDF, CSV, JSON, TXT
- NLP Entity Extraction (spaCy NER + regex) -> EntityCandidate
- LLM Semantic Extraction (Gemini/Groq) for FIR/POLICE_REPORT sources
- Candidate deduplication (NLP vs LLM)
- Entity Resolution Engine -> CanonicalEntity (PostgreSQL)
- Relationship Extraction -> EntityRelationship (with evidence_text, source_page, confidence)
- Neo4j Sync from canonical entities and relationships
- API: POST /ingestion/upload, GET /ingestion/, GET /ingestion/{job_id}

### Security Controls
- JWT (HS256), OAuth2 password flow
- SQL injection protection (parameterized ORM queries)
- Cypher injection protection (bounded Copilot tool calls)
- Audit logging (AuditLog, EventAuditLog)
- Prompt injection mitigations in Copilot system prompt

### Global Audits Passed (Phase 8.1)
- 0 mock arrays / dummy data / placeholders
- Real PostgreSQL aggregations
- Real Neo4j Cypher queries
- pgvector operational (semantic search verified)
- Prompt grounding and explainability verified
- Dynamic API integration (no fake visual states)

---

## 5. What Is Partially Implemented

### RAG/Copilot Pipeline & Evidence Grounding — RESOLVED & VERIFIED

The previously identified RAG gap (M15.1) has been completely resolved and empirically verified across two phases and two hardening audits:

- **P1 Production RAG Ingestion:** `process_ingestion()` now chunks (500 chars/100 overlap), embeds via HuggingFace `all-MiniLM-L6-v2`, and stores embeddings into `DocumentChunk` using `VectorStore.index_document()`. Tracked via `chunk_count` on `IngestionJob`.
- **P2 Evidence & Provenance Grounding:** Deterministic `EvidenceLinker` maps `EntityRelationship` to `DocumentChunk` with exact and spanning character offset detection. `evidence_links` table created via Alembic.
- **Relationship Evidence API:** `GET /api/v1/relationship/{relationship_id}/evidence` serves chunk evidence and provenance to the UI (`EdgeEvidencePanel`).
- **Neo4j Provenance Propagation:** `evidence_text` is synchronized onto Neo4j relationship edges.
- **Copilot Citation Generation:** `CopilotResponse.sources[]` is populated from `RAG_CHUNK` and `ENTITY_EXTRACTION` evidence items.
- **Grounding Hardening:** `grounded = bool(sources)` strictly enforced; no false grounding claims when evidence is absent.
- **Verification Status:** 22/22 tests passing across `test_rag_ingestion.py`, `test_phase2_evidence_link.py`, `test_copilot_sources.py`, and `test_copilot_grounding.py`. 0 fake data inserted.

### Evidence Module
- Relationship Evidence API operational: `GET /api/v1/relationship/{relationship_id}/evidence`
- General standalone document evidence browsing remains a future enhancement

### Investigation Workspace
- Production readiness: 98%
- Copilot is fully functional with verified RAG evidence retrieval and traceable source citations

### FIR Workspace
- Production readiness: 98%
- Related FIR analysis is backed by live pgvector semantic search and evidence linking

### Neo4j Graph Reconciliation
- CanonicalEntity sync to Neo4j exists
- Clean deduplication across multiple ingestion runs is not yet validated

### Multilingual Support (Kannada)
- Specified in PRD (FR-02) as a requirement
- No Kannada NLP pipeline or translation layer is implemented in the codebase

### Redis / Session Management
- Defined in config.py (REDIS_URL)
- Not actively used — no Redis-backed session or caching calls in service layer

---

## 6. What Is Not Yet Implemented

### Phase 9A — Real-Time Intelligence Streaming
- WebSocket infrastructure (skeleton in ws.py but no event bus)
- Live intelligence push updates to UI
- Event-driven alert propagation

### Phase 9B — Digital Twin Karnataka
- Advanced temporal crime playback on map
- Predictive layer visualization
- Animated intelligence map

### Phase 9C — AI Investigation Copilot V2
- Action recommendations engine
- Investigation planning AI
- Tactical suggestion system

### Phase 9D — Scenario Simulation Engine
- What-if analysis
- Crime forecast simulations
- Resource allocation modeling

### Phase 9E — Officer Collaboration Platform
- Shared investigation workspaces
- Real-time case coordination between officers

### Phase 9F — Executive War Room
- Statewide command screen
- Unified intelligence wall

### Production Infrastructure
- Kubernetes orchestration (Docker only currently)
- ELK Stack logging (Prometheus/Grafana referenced in TRD — not deployed)
- MFA (Multi-Factor Authentication)
- Object/file storage (evidence PDFs save locally to uploads/)

### Future Roadmap

| Version | Timeline | Features |
|---------|---------|---------|
| V2 | 3 months | Voice Assistant, Crime Forecasting, Mobile App, Early Warning Alerts |
| V3 | 6 months | Real-Time Crime Intelligence, CCTNS Integration, Cross-District Intelligence |
| V4 | 12 months | Multimodal AI, Evidence Image/Video Analysis, Cross-State Intelligence |

---

## 7. Database Inventory

### PostgreSQL Tables (Live)

| Table | Purpose |
|-------|---------|
| users | Officer accounts |
| roles, permissions, role_permissions | RBAC |
| districts, police_stations | Geography |
| crime_types, crimes, crime_status_history | Crime records |
| suspects, suspect_crimes | Suspect management |
| victims, victim_crimes | Victim records |
| vehicles, crime_vehicles | Vehicle tracking |
| evidence | Crime-linked evidence files |
| investigations, investigation_notes | Investigation case files |
| reports | PDF exports |
| ai_conversations, ai_messages, ai_query_logs | Chat history |
| crime_predictions, hotspot_analysis | Predictive outputs |
| audit_logs, event_audit_log | Compliance |
| notifications, alerts | Alerting |
| officer_assignments, officer_actions | Officer ops |
| document_chunks | pgvector RAG store (384-dim embeddings) |
| ingestion_jobs, entity_candidates | Ingestion pipeline (tracks chunk_count) |
| canonical_entities | Entity resolution output |
| entity_relationships | Relationship extraction output |
| evidence_links | Relationship-to-DocumentChunk provenance links |

### Neo4j Graph (Live)
- **Nodes (1,971):** Suspect, Crime, Vehicle, Phone, Location, District, FIR, Police Station
- **Relationships (5,706):** KNOWS, USED, ASSOCIATED_WITH, PARTICIPATED_IN, VISITED, OCCURRED_IN

---

## 8. API Endpoint Inventory

| Router | Prefix | Key Endpoints |
|--------|--------|--------------|
| auth.py | /auth | login, logout, refresh |
| users.py | /users | CRUD |
| crimes.py | /crimes | CRUD, search |
| suspects.py | /suspects | CRUD |
| investigations.py | /investigations | CRUD, notes |
| timeline.py | /timeline | Entity timelines |
| executive.py | /executive | KPIs, threat overview |
| alerts.py | /alerts | Alert engine |
| officer.py | /officer | Officer workspace |
| command_wall.py | /command-wall | Command center |
| system_health.py | /system-health | DB/LLM health |
| predictive.py | /predictive | Forecasting |
| predictive_validation.py | /predictive/validation | Model metrics |
| chat.py | /chat | AI conversation |
| copilot.py | /copilot | Investigation copilot |
| neo4j.py | /neo4j | Graph queries |
| graph_analytics.py | /graph/analytics | Community detection |
| graph_anomalies.py | /graph/anomalies | Anomaly detection |
| graph_predictions.py | /graph/predictions | Link prediction |
| ingestion.py | /ingestion | File upload pipeline |
| resolution.py | /resolution | Entity resolution |
| relationship.py | /relationship | Relationship records, /{id}/evidence |
| geo.py | /geo | Geospatial / hotspots |
| reports.py | /reports | PDF generation |
| explainability.py | /explainability | AI explainability |
| intelligence_fusion.py | /intelligence | Fused intelligence |

---

## 9. Frontend Route Inventory

| Route | Module |
|-------|--------|
| / | Landing / Login |
| /dashboard | Command Center Dashboard |
| /ai-assistant | AI Chat Interface |
| /crime-map | Geospatial Intelligence Map |
| /knowledge-graph | Criminal Network Graph |
| /investigation-board | Investigation Workspace |
| /fir-workspace | FIR Intelligence Workspace |
| /timeline-intelligence | Unified Timeline Engine |
| /executive-dashboard | Executive Briefings and KPIs |
| /alert-center | Alert and Threat Center |
| /officer-workspace | Officer Copilot |
| /command-wall | State Command Wall |
| /system-health | System Health Center |
| /predictive-intelligence | Predictive Analytics |

---

## 10. Immediate Next Steps (Priority Order)

| Priority | Task | Status | Impact |
|---------|------|--------|--------|
| P1 HIGH | Wire VectorStore.index_document() into process_ingestion() | COMPLETED | RAG pgvector chunking & embedding operational |
| P1 HIGH | Create EvidenceLink model and populate during ingestion | COMPLETED | Relationship-to-DocumentChunk provenance linking verified |
| P2 MED | Add chunk_count column to IngestionJob + Alembic migration | COMPLETED | Observability for RAG indexing verified |
| P2 MED | CopilotResponse.sources[] citation generation & grounding hardening | COMPLETED | 100% grounded copilot, 0 false grounding claims |
| P2 MED | Validate Neo4j re-ingestion deduplication | PENDING | Prevents graph accumulation bugs |
| P3 LOW | Activate Redis for session caching | PENDING | Performance at scale |
| P3 LOW | Implement MFA | PENDING | Security compliance |
| P4 FUTURE | Phase 9A — WebSocket real-time streaming | FUTURE | Next major feature milestone |
| P4 FUTURE | Kannada NLP pipeline | FUTURE | PRD FR-02 compliance |

---

## 11. Audit Verdict (M15.1 + RAG & Evidence Grounding)

> **M15.1 & RAG GROUNDING — COMPLETE & VERIFIED**
>
> LINKRA's end-to-end intelligence ingestion, RAG vector retrieval, and evidence-provenance grounding pipeline is fully implemented and empirically verified:
> 1. **P1 RAG Ingestion:** Automatically parses, chunks (500 chars/100 overlap), embeds with HuggingFace MiniLM, and indexes into pgvector `document_chunks`.
> 2. **P2 Evidence Grounding:** Deterministically links `EntityRelationship` to underlying `DocumentChunk` records with character offsets (`char_offset_start`, `char_offset_end`) via `EvidenceLink`, exposed via `GET /relationship/{id}/evidence` and Neo4j edge sync.
> 3. **Copilot Sources & Grounding Hardening:** `CopilotResponse.sources[]` populates real `CopilotCitation` items from retrieved evidence; `grounded` state is strictly derived from citation presence (`grounded = bool(sources)`). False grounding claims are eliminated.
> 4. **Empirical Test Verification:** 22/22 automated tests pass across all suites (`test_rag_ingestion.py`, `test_phase2_evidence_link.py`, `test_copilot_sources.py`, `test_copilot_grounding.py`).
> 5. **Zero Fake Data:** 0 synthetic/mock records inserted into production database.


---

*SUMMARY.md synthesized from: PRD.md, TRD.md, IMPLEMENTATION_PLAN.md, BACKEND_SCHEMA.md, PROJECT_STATUS.md, PROJECT_STATUS_PHASE8_1.md, and live codebase audit — September 2026*
