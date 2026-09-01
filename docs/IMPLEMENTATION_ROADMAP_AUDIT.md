# LINKRA Implementation Roadmap Audit

## Audit Date
August 30, 2026

## Audit Scope
This audit compares `docs/IMPLEMENTATION_ROADMAP.md`, `docs/SIH26189_PHASE_MAP.md`, `IMPLEMENTATION_PLAN.md`, and previous milestone reports against the actual repository source code, database/migrations, tests, frontend, and existing milestone documentation. The goal is to determine the true state of implementation versus documented claims.

---

## 1. Executive Summary

- **Total Phases**: 19
- **Completed Phases**: 1 (Phase 1)
- **Partially Completed Phases**: 10 (Phases 2, 4, 5, 6, 8, 9, 10, 11, 13, 16)
- **Unimplemented/Deferred Phases**: 4 (Phases 7, 14, 18, 19)
- **Mocked/Demo-Dependent Features**: High dependency. Critical pathways like NLP extraction, Investigation Workspace, and feed tickers are heavily mocked, contrary to what `docs/MOCK_DATA_AUDIT.md` claims.
- **Broken Features**: N/A (did not execute tests, but the pipeline is fractured by mocks).
- **Highest-Priority Remaining Work**: Unblocking Phase 3 (Real NLP) so that real data can flow into Postgres and Neo4j, replacing the mocked AI extraction.

---

## 2. Overall Progress

| Phase | Meaningful Name | Status | Completion |
|------|------|------|------|
| Phase 1 | Foundation & State Agnostic | COMPLETE | 100% |
| Phase 2 | Data Ingestion | PARTIAL | 60% |
| Phase 3 | Real NLP Pipeline | MOCKED | 10% |
| Phase 4 | Entity Resolution | PARTIAL | 50% |
| Phase 5 | Knowledge Graph Basics | PARTIAL | 60% |
| Phase 6 | Graph Analytics | PARTIAL | 50% |
| Phase 7 | Community Detection | DEFERRED | 0% |
| Phase 8 | Anomaly Detection | PARTIAL | 40% |
| Phase 9 | Link Prediction | PARTIAL | 30% |
| Phase 10 | Evidence/Explainability | PARTIAL | 40% |
| Phase 11 | Crime Map | PARTIAL | 30% |
| Phase 12 | Investigation Workspace | MOCKED | 20% |
| Phase 13 | AI Copilot | PARTIAL | 40% |
| Phase 14 | Evidence-Grounded AI | NOT STARTED | 0% |
| Phase 15 | Reports | PARTIAL | 30% |
| Phase 16 | Security Hardening | PARTIAL | 50% |
| Phase 17 | Testing | PARTIAL | 30% |
| Phase 18 | Synthetic SIH Dataset | NOT STARTED | 0% |
| Phase 19 | SIH Demonstration Story | NOT STARTED | 0% |

---

## 3. Detailed Phase Checklists

### PHASE 1 — Foundation & State Agnostic
#### Foundation & Security
- [x] JWT integration
- [x] Role-based access control (RBAC)
- [x] Removal of hardcoded branding

**Status**: COMPLETE  
**Evidence**: `backend/app/api/v1/auth.py`, `backend/app/api/v1/users.py`, `backend/tests/test_auth_rbac.py`  
**Gaps**: None identified.  
**Next Action**: None.

### PHASE 2 — Data Ingestion
#### Data Source Support & Ingestion
- [x] Ingestion tables/schema
- [x] Ingestion API (`/api/v1/ingestion`)
- [ ] Multipart upload API fully integrated with NLP
- [ ] Asynchronous background job queue (e.g., Celery)

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/ingestion.py`, Alembic migration `a3f7c8d92e14`.  
**Gaps**: No robust asynchronous queue for background processing of large PDFs.  
**Next Action**: Integrate true background job tracking.

### PHASE 3 — Real NLP Pipeline
#### Text & Entity Extraction
- [ ] NER models integration
- [ ] Real extraction of PERSON, LOCATION, VEHICLE
- [ ] Real relationship extraction

**Status**: MOCKED (DOCUMENTATION CLAIM: COMPLETE, ACTUAL CODEBASE: NOT COMPLETE)  
**Evidence**: `backend/app/ai/workflows/fir_extraction.py` explicitly hardcodes `"suspects": ["Unknown Male"]` and states `# We mock the LLM call for architecture demonstration.`  
**Gaps**: Actual LLM/NLP integration is entirely bypassed.  
**Next Action**: Implement the actual LangChain/LangGraph LLM calls to replace static dictionaries.

### PHASE 4 — Entity Resolution
#### Resolution & Matching
- [x] Resolution APIs (`resolution.py`)
- [x] Similarity scoring baseline
- [ ] Real human-in-the-loop review API for candidates

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/resolution.py`, `test_resolution.py`.  
**Gaps**: The resolution logic exists but operates on mocked/static NLP outputs.  
**Next Action**: Connect to real NLP output.

### PHASE 5 — Knowledge Graph Basics
#### Graph Sync & Persistence
- [x] Neo4j connection (`neo4j.py`)
- [x] Basic node/edge queries
- [ ] Automated sync from PostgreSQL to Neo4j with real data

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/neo4j.py`, `backend/scripts/verify_neo4j_live.py`.  
**Gaps**: Synchronization relies on the broken/mocked upstream NLP pipeline.  
**Next Action**: Ensure idempotency and build a graph rebuild script from Postgres truth.

### PHASE 6 — Graph Analytics
#### Mathematical Algorithms
- [x] Degree Centrality
- [x] Shortest Path
- [ ] PageRank
- [ ] Betweenness Centrality

**Status**: PARTIAL  
**Evidence**: `backend/app/ai/neo4j/analytics.py` implements bounded shortest path and degree counts.  
**Gaps**: Advanced centralities (PageRank) are missing.  
**Next Action**: Implement PageRank/Betweenness centrality.

### PHASE 7 — Community Detection
#### Network Discovery
- [ ] Louvain OR Leiden implementation
- [ ] Community assignment
- [ ] Visualization of clusters

**Status**: DEFERRED / NOT IMPLEMENTED  
**Evidence**: No Louvain or community detection algorithms found in the codebase.  
**Gaps**: Entirely missing.  
**Next Action**: Implement community detection in Neo4j.

### PHASE 8 — Anomaly Detection
#### Anomalies
- [x] Structural anomaly endpoints
- [ ] True behavioral/temporal anomaly detection (Isolation Forest)
- [ ] Transaction anomalies

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/graph_anomalies.py`, `alert_engine.py`.  
**Gaps**: Heavy reliance on basic structural rules rather than advanced temporal tracking.  
**Next Action**: Expand anomaly rules for temporal data.

### PHASE 9 — Link Prediction
#### Hidden Connections
- [x] Basic prediction endpoints
- [ ] Jaccard / Adamic-Adar algorithms
- [ ] GNN implementation

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/graph_predictions.py`.  
**Gaps**: Deep mathematical implementations of link prediction are deferred.  
**Next Action**: Implement Adamic-Adar in Cypher.

### PHASE 10 — Evidence/Explainability
#### Provenance
- [x] Explainability API (`explainability.py`)
- [ ] Deep source document provenance tracking per relationship

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/explainability.py`.  
**Gaps**: Evidence lacks granularity to the page/row level in PDF documents.  
**Next Action**: Attach page-level provenance during ingestion.

### PHASE 11 — Crime Map
#### Geospatial Intelligence
- [x] Map UI component (`frontend/src/app/map/page.tsx`)
- [ ] PostGIS integration with real data density

**Status**: PARTIAL  
**Evidence**: Map component exists, but relies on mocked forecasts (`MOCK_FORECAST`).  
**Gaps**: Live geospatial querying is not fully wired.  
**Next Action**: Wire MapLibre to live PostGIS endpoints.

### PHASE 12 — Investigation Workspace
#### Analyst Dashboard
- [x] UI scaffolding
- [ ] Real data integration

**Status**: MOCKED (DOCUMENTATION CLAIM: COMPLETE, ACTUAL CODEBASE: NOT COMPLETE)  
**Evidence**: `frontend/src/app/investigation-board/page.tsx` uses `MOCK_CASE` (INV-2026-8812).  
**Gaps**: Workspace does not load actual investigation data from the database.  
**Next Action**: Replace `MOCK_CASE` with live API fetch.

### PHASE 13 — AI Copilot
#### Chat Assistant
- [x] Copilot API (`copilot.py`)
- [ ] True Intent classification & RAG orchestration

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/copilot.py`.  
**Gaps**: RAG is heavily mocked in the NLP workflow.  
**Next Action**: Wire LLM tools to live DB queries.

### PHASE 14 — Evidence-Grounded AI
#### Hallucination Prevention
- [ ] Strict distinction between CONFIRMED/INFERRED/PREDICTED
- [ ] Citation injection

**Status**: NOT STARTED  
**Evidence**: N/A  
**Gaps**: Missing constraint layer.  
**Next Action**: Add evidence validators to LLM output parsers.

### PHASE 15 — Reports
#### Case Summaries
- [x] Reports API (`reports.py`)
- [ ] PDF export functionality

**Status**: PARTIAL  
**Evidence**: `backend/app/api/v1/reports.py`.  
**Gaps**: True PDF binary generation is incomplete.  
**Next Action**: Implement WeasyPrint/ReportLab generation.

### PHASE 16 — Security Hardening
#### Production Security
- [x] RBAC
- [ ] Rate limiting, CORS tightening, Audit Logs

**Status**: PARTIAL  
**Evidence**: RBAC exists, but comprehensive audit logging across all writes is weak.  
**Gaps**: Input sanitization and comprehensive audit trails.  
**Next Action**: Implement Redis-based rate limiting.

### PHASE 17 — Testing
#### Validation
- [x] Backend Unit Tests (`backend/app/tests/`)
- [ ] Frontend Tests
- [ ] True E2E Test Pipeline

**Status**: PARTIAL  
**Evidence**: Only backend test coverage exists. No `frontend/tests`. Scripts exist for E2E but no real E2E suite.  
**Gaps**: Missing E2E integration test (Upload -> NLP -> Neo4j -> UI).  
**Next Action**: Build Playwright E2E tests.

### PHASE 18 — Synthetic SIH Dataset
#### Demonstration Data
- [ ] Generators for FIRs, logs, statements

**Status**: NOT STARTED  
**Evidence**: None.  
**Gaps**: Need realistic data for SIH.  
**Next Action**: Create synthetic data generator scripts.

### PHASE 19 — SIH Demonstration Story
#### Final Pitch
- [ ] Curated investigation scenario

**Status**: NOT STARTED  
**Evidence**: None.  
**Gaps**: N/A  
**Next Action**: Write the demo narrative.

---

## 4. M1.1–M1.14 Verification

| Milestone | Claimed Status | Actual Status | Evidence |
|---|---|---|---|
| M1.1 National Scope | Complete | COMPLETE | Checked `auth.py` and RBAC |
| M1.2 Data Contract | Complete | PARTIAL | Schema exists but not fully utilized |
| M1.3 Real Data Ingestion | Complete | PARTIAL | Endpoints exist, real queue missing |
| M1.4 NLP Extraction | Complete | MOCKED | `fir_extraction.py` uses hardcoded dicts |
| M1.5 Entity Resolution | Complete | PARTIAL | Dependent on mocked NLP |
| M1.6 Relationship Extr. | Complete | MOCKED | Part of mocked NLP workflow |
| M1.7 Knowledge Graph | Complete | PARTIAL | Graph exists but data sync is blocked by mocks |
| M1.8 Graph Analytics | Complete | PARTIAL | `neo4j_analytics.py` has basic degree/path queries |
| M1.9 Anomaly Detection | Complete | PARTIAL | Structural anomalies exist, behavioral missing |
| M1.10 Link Prediction | Complete | PARTIAL | Basic APIs exist |
| M1.11 Invest. Workspace| Complete | MOCKED | `MOCK_CASE` in `investigation-board/page.tsx` |
| M1.12 Evidence/Explain | Complete | PARTIAL | Provenance is shallow |
| M1.13 AI Copilot | Complete | PARTIAL | RAG is incomplete/mocked |
| M1.14 Reports | Complete | PARTIAL | PDF export missing |

---

## 5. Core Intelligence Pipeline Audit

| Pipeline Stage | Status | Real/Mocked | Evidence |
|---|---|---|---|
| Upload | PARTIAL | Real | `ingestion.py` API |
| Validation | PARTIAL | Real | Basic FastAPI validation |
| Parsing | PARTIAL | Real | Simple PDF parsers exist |
| Normalization | UNVERIFIED | Unverified | - |
| PostgreSQL | COMPLETE | Real | SQLAlchemy models/migrations |
| NLP | MOCKED | Mocked | `fir_extraction.py` explicitly mocks LLM |
| Entity Extraction | MOCKED | Mocked | Returns static `Unknown Male` |
| Entity Resolution | PARTIAL | Real logic, Mocked data | `resolution.py` |
| Relationship Extraction | MOCKED | Mocked | Part of `fir_extraction.py` |
| Neo4j Projection | PARTIAL | Real logic, Mocked data | `neo4j.py` |
| Graph Analytics | PARTIAL | Real | `neo4j_analytics.py` |
| Anomaly Detection | PARTIAL | Real | `alert_engine.py` |
| Link Prediction | PARTIAL | Real | `graph_predictions.py` |
| Explainability | PARTIAL | Real | `explainability.py` |
| Copilot | PARTIAL | Real logic, Mocked RAG | `copilot.py` |
| Reports | PARTIAL | Real | `reports.py` |

---

## 6. Mock / Demo Dependency Audit

**CRITICAL FINDING**: `docs/MOCK_DATA_AUDIT.md` incorrectly reports 0 mock hits. The frontend and AI layers heavily rely on mocks.

| Feature | File | Mock/Static Behavior | Production Ready? | Required Action |
|---|---|---|---|---|
| FIR Extraction | `fir_extraction.py` | Hardcoded `Unknown Male`, `KA-01-AB-1234` | NO | Implement real LLM extraction with structured outputs |
| Investigation Board | `investigation-board/page.tsx` | Uses `MOCK_CASE` object | NO | Fetch active case from `/api/v1/crimes/{id}` |
| Intelligence Feed | `IntelligenceFeedTicker.tsx`| Uses `mockFeeds` array | NO | Connect to WebSocket / Alerts API |
| Predictive Forecast | `ForecastOverview.tsx` | Hardcoded forecast arrays | NO | Connect to ML forecasting API |

---

## 7. Database Readiness

**PostgreSQL**:
- Schema: Yes
- Migrations: Yes (`alembic/versions`)
- Source-of-truth status: Schema is ready, but pipeline to populate it is blocked by mocked NLP.

**Neo4j**:
- Schema/Constraints: Yes
- Projection: Sync scripts exist.
- Graph Rebuild: Unverified.

**PostGIS**:
- Status: Unverified / Incomplete.

---

## 8. AI Readiness

- **Real AI/ML**: NOT IMPLEMENTED (Mocked)
- **Structural Analytics**: IMPLEMENTED (`neo4j_analytics.py`)
- **Rule-Based Logic**: IMPLEMENTED
- **LLM-Assisted**: MOCKED
- **Deferred**: Advanced Graph Machine Learning

---

## 9. Security Audit

- RBAC: PASS
- JWT: PASS
- Input validation: PASS (Pydantic)
- Audit Logs: WARNING (Incomplete coverage)
- Hardcoded Secrets: PASS (No API keys found)

---

## 10. Testing Audit

- Backend Unit Tests: ~20 test files in `backend/app/tests/` and `backend/tests/`.
- Frontend Tests: FAIL (Directory `frontend/tests` does not exist).
- E2E Pipeline: FAIL (No Playwright/Cypress suite, only basic python verification scripts).

---

## 11. Critical Gaps

- **P0** — Blocking core product: **Mocked NLP Pipeline.** Real extraction must replace `fir_extraction.py` mocks so that Postgres and Neo4j can be populated with real data.
- **P0** — Blocking core product: **Mocked Investigation Workspace.** The frontend must fetch live data instead of `MOCK_CASE`.
- **P1** — Required for SIH: True background task ingestion queue.
- **P2** — Valuable enhancement: PDF Report generation.
- **P3** — Future/stretch: Advanced link prediction (GNNs).

---

## 12. Recommended Implementation Order

1. **Production ingestion & Real NLP** (Fix Phase 2 & 3) - Replace mocks in `fir_extraction.py`.
2. **Investigation Workspace** - Wire `investigation-board/page.tsx` to live APIs.
3. **Entity resolution** - Validate against the newly un-mocked NLP data.
4. **Evidence-backed relationships** - Propagate provenance.
5. **Graph Analytics & Expansion** - Unblock Neo4j queries with real data.
6. **Community detection** - Implement missing Louvain algorithms.
7. **Temporal/behavioral anomaly detection**
8. **Link prediction upgrades**
9. **Crime map**
10. **Copilot tool integration**
11. **Evidence grounding**
12. **Reports/PDF**
13. **Security hardening**
14. **Full E2E testing**
15. **Synthetic SIH dataset**
16. **Final SIH demo story**

---

# Immediate Next Milestone

> **NEXT: PHASE 3 — Real FIR NLP & Intelligence Extraction**

**Why this is next:** The entire downstream intelligence pipeline (Entity Resolution, Knowledge Graph, Copilot) is currently fed by hardcoded arrays in `fir_extraction.py` (e.g. "Unknown Male"). Until real NLP extraction is implemented, the platform is effectively a static demo.

**What is already available:**
- Ingestion APIs (`ingestion.py`)
- LangGraph orchestration scaffolding (`fir_extraction.py`)
- Pydantic models for structured output (`ExtractedEntities`)

**What is missing:**
- Actual execution of LLM API calls (OpenAI/Gemini/Llama) using `with_structured_output`.
- Feeding raw parsed PDF text into the LLM context.
- Storing the LLM response in PostgreSQL.

**Which files should likely be modified:**
- `backend/app/ai/workflows/fir_extraction.py`

**What must NOT be changed:**
- The PostgreSQL schema (it is already correct).
- The Neo4j graph model.
- The overall FastAPI router structure.

**Definition of Done:**
- `fir_extraction.py` takes raw text and successfully returns dynamically extracted entities via an LLM, entirely replacing the `MOCK` dictionary.
