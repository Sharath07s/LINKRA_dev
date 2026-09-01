# LINKRA — Implementation Task Tracker

_Last updated: 2026-08-31_

---

## Phase 2 — Data Ingestion Infrastructure

### Upload
- [x] Real file upload endpoint (`POST /api/v1/ingestion/upload`)
- [x] Multipart/form-data support
- [x] JWT authentication required
- [x] UUID-prefixed safe filename generation (prevents path traversal)
- [x] No internal path exposure in API response

### Validation
- [x] File extension whitelist (pdf, csv, json, txt)
- [x] MIME type cross-check (non-fatal; extension authoritative)
- [x] File size limit (50 MB enforced)
- [x] Empty file rejection
- [x] Missing filename rejection
- [x] Informative user-facing error messages (no stack trace leakage)

### File Type Detection
- [x] PDF → `parse_pdf()` routing
- [x] CSV → `parse_csv()` routing
- [x] JSON → `parse_json()` routing
- [x] TXT → `parse_txt()` routing

### Parsing
- [x] PDF text extraction (pypdf, per-page provenance)
- [x] Scanned PDF gracefully rejected with clear message (no OCR fabrication)
- [x] CSV row parsing (DictReader, per-row provenance, quoted fields, UTF-8)
- [x] JSON parsing (object + array support, per-record provenance)
- [x] TXT extraction (UTF-8, single-document, file-size metadata)
- [x] All parsers: empty file rejection
- [x] All parsers: missing file rejection

### Normalization
- [x] Whitespace normalization (multi-space → single space)
- [x] PERSON casing normalization
- [x] PHONE normalization (10-digit, +91 prefix standardization)
- [x] VEHICLE normalization (uppercase, hyphen/space stripping)
- [x] ORGANIZATION normalization (lowercase)
- [x] LOCATION normalization (lowercase)
- [x] CSV column name normalization (`_normalize_column_name`)
- [x] Raw value preserved alongside normalized value

### Ingestion Job Tracking
- [x] IngestionJob created at upload time (status=QUEUED)
- [x] Status transitions: QUEUED → PROCESSING → PARSED → EXTRACTED → COMPLETED | FAILED
- [x] `started_at` and `completed_at` timestamps
- [x] `record_count` set from parser output
- [x] `entity_count` set from NLP extraction output
- [x] `error_message` captured on failure (max 2000 chars)
- [x] Failed jobs: job persists, error recorded, DB rollback-safe

### Error Tracking
- [x] Job-level error message stored in PostgreSQL
- [x] Full traceback in server logs only
- [x] Generic 500 message to client (no internals exposed)
- [x] Per-format parsing errors handled and reported

### Record Counts
- [x] `record_count` reflects parsed document records (pages/rows/records)
- [x] `entity_count` reflects NLP + structured extraction candidates
- [x] Frontend displays both counts per job

### Provenance Tracking
- [x] `ingestion_job_id` on every EntityCandidate
- [x] `source_page` for PDF entities (page number)
- [x] `source_row` for CSV/JSON entities (row/record index)
- [x] `start_offset` / `end_offset` character offsets (spaCy NER)
- [x] `extraction_method`: `spacy_ner` | `regex` | `structured_field`
- [x] M1.12 Explainability can trace entity → candidate → job → file

### PostgreSQL Persistence
- [x] `ingestion_jobs` table (via migration `a3f7c8d92e14`)
- [x] `entity_candidates` table (via migration `a3f7c8d92e14`)
- [x] `canonical_entities` table (via migration `1f5f437afa86`)
- [x] `entity_relationships` table (via migration `f945aeb86db6`)
- [x] All writes transactional (SQLAlchemy session commit/rollback)
- [x] No fake entities in database

### NLP Pipeline
- [x] spaCy `en_core_web_sm` (v3.8.0) — REAL, installed and verified
- [x] PERSON extraction (spaCy NER)
- [x] ORGANIZATION extraction (spaCy NER)
- [x] LOCATION/GPE extraction (spaCy NER)
- [x] DATE extraction (spaCy NER)
- [x] PHONE extraction (Indian regex — 10-digit + +91 variants)
- [x] VEHICLE extraction (Indian registration regex KA01AB1234)
- [x] Span overlap deduplication (regex takes priority over NER)
- [x] Structured field extraction for CSV/JSON (field-name → entity-type mapping)

### Entity Resolution
- [x] `resolve_candidate()` fuzzy-matches EntityCandidate to CanonicalEntity
- [x] Creates new CanonicalEntity if no match found
- [x] Sets `candidate.resolved_to_id` and `candidate.resolution_status`
- [x] Neo4j node sync via `sync_canonical_entity()` (best-effort)

### Relationship Extraction
- [x] CDR structured relationship extraction (caller↔callee)
- [x] NLP trigger-based co-mention relationship extraction
- [x] `entity_relationships` written to PostgreSQL
- [x] Neo4j relationship sync (best-effort; does not block PostgreSQL writes)

### Data Sources UI
- [x] Real API integration (no mock data in UI)
- [x] Drag-and-drop file upload
- [x] Source type selector (FIR, CDR, FINANCIAL_TRANSACTION, etc.)
- [x] Upload + process with loading state
- [x] Job list from real API (`GET /api/v1/ingestion/`)
- [x] Empty state: "No ingested datasets yet"
- [x] Status badges: QUEUED | PROCESSING | PARSED | EXTRACTED | COMPLETED | FAILED
- [x] Entity count per job
- [x] Expanded entity detail view (grouped by type, provenance tooltip)
- [x] Upload error display (user-facing message, no stack trace)
- [x] Refresh button

### Security
- [x] JWT authentication on all ingestion endpoints
- [x] File extension whitelist enforced
- [x] File size limit enforced (50 MB)
- [x] UUID-safe filenames
- [x] No filesystem paths in API responses
- [x] No executable uploads (.exe, .py, .sh not in whitelist)
- [x] Error sanitization (generic 500 to client)

### Tests
- [x] TXT parser: valid, empty, missing (3 tests)
- [x] CSV parser: valid, empty, headers-only (3 tests)
- [x] JSON parser: valid array, valid object, malformed, empty (4 tests)
- [x] PDF parser: valid, missing file (2 tests) — **added in Phase 2**
- [x] NLP extraction: PERSON, LOCATION, PHONE, VEHICLE, DATE, empty, offsets, full FIR (8 tests)
- [x] Validation: extension, empty, oversize, missing filename (6 tests)
- [x] **26 / 26 ingestion tests PASS**
- [x] **109 / 109 full regression suite PASS**

### Documentation
- [x] `docs/PHASE_2/P2.1_INGESTION_AUDIT.md`
- [x] `docs/PHASE_2/P2.2_INGESTION_ARCHITECTURE.md`
- [x] `docs/PHASE_2/P2.3_INGESTION_VERIFICATION.md`
- [x] `task.md` updated

### End-to-End Verification
- [x] Real fixture: `tests/fixtures/ingestion/sample_fir.txt` — persons, phones, vehicles extracted
- [x] Real fixture: `tests/fixtures/ingestion/sample_cdr.csv` — structured CDR records
- [x] Real fixture: `tests/fixtures/ingestion/sample_document.pdf` — PDF text extracted
- [x] Frontend build: `npm run build` → EXIT 0 (25 pages, 0 errors)

---

## Phase 2 Mock Audit Results

| Component | Mock Type | Phase |
|-----------|-----------|-------|
| `app/ai/workflows/fir_extraction.py` | LLM call mocked | Phase 3 |
| `frontend/src/app/investigation-board/page.tsx` | `MOCK_CASE` scaffold | Phase 3 |
| `frontend/src/components/IntelligenceFeedTicker.tsx` | `mockFeeds` array | Phase 4 |
| `backend/app/ingestion/` | **NONE** | ✅ Phase 2 CLEAN |
| `frontend/src/app/data-sources/page.tsx` | **NONE** | ✅ Phase 2 CLEAN |

---

## Phase 3 Blockers (Identified During Phase 2)

- [ ] Replace mock LLM call in `fir_extraction.py` with real LangGraph + Gemini/Anthropic
- [ ] Wire Investigation Board to real PostgreSQL investigations (replace `MOCK_CASE`)
- [ ] RBAC role restriction on upload endpoint (restrict to OFFICER+ role)
- [ ] API-level integration tests with live test database
- [ ] Phase 3 NLP: LLM-backed semantic extraction for FIRs

## Phase 4 Deferred

- [ ] OCR support for scanned PDFs (image-only)
- [ ] Async job queue (Celery + Redis)
- [ ] Wire `IntelligenceFeedTicker` to real-time alerts (Redis/WebSocket)
- [ ] Bulk ingestion API
- [ ] Duplicate file detection
