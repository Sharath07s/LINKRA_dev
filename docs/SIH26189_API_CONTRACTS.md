# SIH26189 API Contracts
> **STATUS:** TARGET ARCHITECTURE / NOT YET IMPLEMENTED
> These are architectural contracts, not currently working endpoints.

This document defines the comprehensive API contracts for all SIH26189 modules.

---

## 1. Ingestion API

### POST `/api/v1/ingestion/upload`
**Description:** Multipart file upload (PDF/CSV/JSON/TXT) for ingestion.
- **Request Body (Multipart):**
  - `file`: The file to upload.
  - `source_type`: (String) e.g., 'FIR', 'CALL_RECORD', 'FINANCIAL_STATEMENT'.
- **Response (202 Accepted):**
  ```json
  {
    "job_id": "uuid",
    "status": "UPLOADED",
    "message": "File uploaded and ingestion job queued."
  }
  ```
- **Error Responses:** 
  - `400 Bad Request`: Invalid file type.
  - `413 Payload Too Large`: File exceeds size limit.

### GET `/api/v1/ingestion/jobs`
**Description:** List ingestion jobs with pagination and filtering by status.
- **Query Params:** `page`, `size`, `status`
- **Response (200 OK):**
  ```json
  {
    "items": [
      {
        "job_id": "uuid",
        "file_name": "fir_102.pdf",
        "status": "COMPLETED",
        "created_at": "2026-08-25T10:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
  ```

### GET `/api/v1/ingestion/{job_id}`
**Description:** Get job details including status, progress, and extracted entity counts.
- **Job States:** `UPLOADED` → `VALIDATING` → `PARSING` → `EXTRACTING` → `RESOLVING` → `PERSISTING` → `GRAPH_SYNC` → `COMPLETED`, `FAILED`
- **Response (200 OK):**
  ```json
  {
    "job_id": "uuid",
    "status": "EXTRACTING",
    "progress_percent": 45,
    "extracted_entities_count": {
      "PERSON": 12,
      "LOCATION": 3
    }
  }
  ```

### GET `/api/v1/ingestion/{job_id}/errors`
**Description:** Get job error details.
- **Response (200 OK):**
  ```json
  {
    "job_id": "uuid",
    "errors": [
      {
        "stage": "PARSING",
        "message": "Failed to parse page 3, corrupted text block."
      }
    ]
  }
  ```

---

## 2. NLP Pipeline Contract
*Internal Service Interface / Message Queue Contract*

**Description:** Interface definition for text extraction, entity extraction, relationship extraction, and normalization.

- **Entity Types:** `PERSON`, `LOCATION`, `ORGANIZATION`, `VEHICLE`, `PHONE`, `CASE`, `CRIME`, `EVENT`, `DATE`, `ACCOUNT`

- **Extraction Result Schema:**
  ```json
  {
    "entity_type": "PERSON",
    "raw_text": "John Doe",
    "normalized_value": "JOHN DOE",
    "confidence": 0.95,
    "span": { "start": 125, "end": 133 }
  }
  ```

- **Relationship Extraction Result Schema:**
  ```json
  {
    "source_entity": "entity_uuid_1",
    "target_entity": "entity_uuid_2",
    "relationship_type": "ASSOCIATED_WITH",
    "confidence": 0.88,
    "evidence_text": "John Doe was seen communicating with Jane Smith."
  }
  ```

---

## 3. Entity Resolution Contract

### POST `/api/v1/entities/resolve`
**Description:** Trigger resolution for extracted entities asynchronously.
- **Request:** `{ "job_id": "uuid" }`
- **Response (202 Accepted):** `{ "resolution_task_id": "uuid" }`

### GET `/api/v1/entities/candidates/{entity_id}`
**Description:** Get matching candidates for an extracted entity.
- **Statuses:** `PENDING_REVIEW`, `MATCHED`, `REJECTED`, `CREATED_NEW`
- **Response (200 OK):**
  ```json
  {
    "target_entity_id": "uuid",
    "candidates": [
      {
        "candidate_id": "existing_uuid",
        "similarity_score": 0.92,
        "match_signals": ["Exact Name Match", "Same Phone Number"],
        "resolution_status": "PENDING_REVIEW"
      }
    ]
  }
  ```

### POST `/api/v1/entities/merge`
**Description:** Merge entities (requires analyst review).
- **Request:**
  ```json
  {
    "source_entity_ids": ["uuid_1", "uuid_2"],
    "target_entity_id": "uuid_master",
    "rationale": "Same person confirmed via phone record."
  }
  ```
- **Response (200 OK):** `{ "status": "MERGED" }`

### POST `/api/v1/entities/reject`
**Description:** Reject a merge candidate.
- **Request:**
  ```json
  {
    "extracted_entity_id": "uuid",
    "candidate_entity_id": "existing_uuid",
    "rationale": "Different date of birth."
  }
  ```
- **Response (200 OK):** `{ "status": "REJECTED" }`

---

## 4. Knowledge Graph API

### GET `/api/v1/graph/nodes/{node_id}`
**Description:** Get node details with its immediate relationships (1-hop).
- **Response (200 OK):**
  ```json
  {
    "node_id": "uuid",
    "labels": ["PERSON"],
    "properties": { "name": "John Doe", "age": 35 },
    "relationships": [
      {
        "rel_id": "rel_uuid",
        "type": "OWNS",
        "target_node_id": "uuid_vehicle",
        "properties": { "since": "2020-01-01" }
      }
    ]
  }
  ```

### POST `/api/v1/graph/traverse`
**Description:** Graph traversal with depth/filters.
- **Request:**
  ```json
  {
    "start_node_ids": ["uuid"],
    "max_depth": 3,
    "relationship_filters": ["KNOWS", "OWNS", "PARTICIPATED_IN"],
    "node_filters": { "labels": ["PERSON", "VEHICLE", "CASE"] }
  }
  ```
- **Response (200 OK):** `{ "nodes": [...], "edges": [...] }`

### POST `/api/v1/graph/search`
**Description:** Search nodes by properties (using Neo4j full-text search).
- **Request:**
  ```json
  {
    "query": "John",
    "labels": ["PERSON"]
  }
  ```
- **Response (200 OK):** `{ "nodes": [...] }`

### POST `/api/v1/graph/sync`
**Description:** Trigger PostgreSQL → Neo4j synchronization.
- **Response (202 Accepted):** `{ "sync_job_id": "uuid", "status": "STARTED" }`

---

## 5. Graph Analytics Contract

### GET `/api/v1/analytics/centrality/{entity_id}`
**Description:** Calculate centrality metrics for a node.
- **Response (200 OK):**
  ```json
  {
    "entity_id": "uuid",
    "metrics": {
      "degree": 15,
      "betweenness": 0.45,
      "closeness": 0.32,
      "pagerank": 1.2
    }
  }
  ```

### GET `/api/v1/analytics/shortest-path`
**Description:** Find the shortest path between two entities.
- **Query Params:** `source_id`, `target_id`
- **Response (200 OK):**
  ```json
  {
    "path_length": 3,
    "nodes": ["uuid_A", "uuid_B", "uuid_C", "uuid_D"],
    "edges": ["rel_1", "rel_2", "rel_3"]
  }
  ```

### GET `/api/v1/analytics/communities`
**Description:** Get community detection results (e.g., Louvain).
- **Response (200 OK):**
  ```json
  {
    "communities": [
      {
        "community_id": 1,
        "node_count": 45,
        "top_nodes": ["uuid_1", "uuid_2"]
      }
    ]
  }
  ```

### GET `/api/v1/analytics/link-prediction/{entity_id}`
**Description:** Get predicted relationships for an entity.
- **Response (200 OK):**
  ```json
  {
    "entity_id": "uuid",
    "predicted_links": [
      {
        "target_entity_id": "uuid_x",
        "predicted_relationship": "ASSOCIATED_WITH",
        "score": 0.89,
        "evidence": ["Common known associates", "Geographic proximity"]
      }
    ]
  }
  ```

---

## 6. Anomaly/Pattern Detection Contract

### GET `/api/v1/anomalies/`
**Description:** List detected anomalies.
- **Query Params:** `type`, `severity`
- **Response (200 OK):**
  ```json
  {
    "anomalies": [
      {
        "anomaly_id": "uuid",
        "type": "FINANCIAL",
        "severity": "HIGH",
        "description": "Unusually large transfer pattern",
        "created_at": "2026-08-25T12:00:00Z"
      }
    ]
  }
  ```

### GET `/api/v1/anomalies/{anomaly_id}`
**Description:** Get anomaly detail with evidence.
- **Response (200 OK):**
  ```json
  {
    "anomaly_id": "uuid",
    "type": "FINANCIAL",
    "detection_method": "STATISTICAL",
    "confidence": 0.95,
    "entities_involved": ["uuid_A", "uuid_B"],
    "evidence_references": [
      { "source_id": "tx_1029", "excerpt": "Transfer of $50,000 at 3 AM" }
    ]
  }
  ```

### GET `/api/v1/patterns/`
**Description:** Discovered complex patterns (e.g., cyclic money flow, communication rings).
- **Response (200 OK):** Array of detected patterns with participating nodes.

---

## 7. Evidence/Provenance Contract

### GET `/api/v1/evidence/{result_id}`
**Description:** Get the evidence chain for any analytical result, extraction, or prediction.
- **Response (200 OK):**
  ```json
  {
    "result_id": "uuid",
    "evidence_chain": [
      {
        "source_type": "FIR_DOCUMENT",
        "source_id": "doc_uuid",
        "confidence_level": "CONFIRMED",
        "page": 2,
        "excerpt": "Subject was seen leaving the premises at 22:00."
      }
    ]
  }
  ```

---

## 8. AI Copilot Tool Contract

**Description:** Tool definitions used by the AI Copilot Intent Engine.

### Tool Workflow
`User Question` → `Intent Detection` → `Tool Planning` → `Tool Execution` → `Evidence Retrieval` → `Result Validation` → `LLM Explanation` → `Evidence-Grounded Answer`

### Tool Definitions

1. **SQL Tool**
   - **Name:** `query_relational_data`
   - **Description:** Executes SQL against PostgreSQL for structured reporting.
   - **Input:** `{ "sql_query": "SELECT..." }`
   - **Output:** JSON array of rows.

2. **Neo4j Tool**
   - **Name:** `query_graph_data`
   - **Description:** Executes Cypher queries for deep relationship extraction.
   - **Input:** `{ "cypher_query": "MATCH..." }`
   - **Output:** Graph paths/nodes.

3. **RAG Tool**
   - **Name:** `search_unstructured_text`
   - **Description:** Semantic search over ingested documents (pgvector).
   - **Input:** `{ "query": "string", "top_k": int }`
   - **Output:** Array of text chunks with metadata.

4. **Graph Analytics Tool**
   - **Name:** `run_graph_algorithm`
   - **Description:** Run centrality, pathfinding, or community detection.
   - **Input:** `{ "algorithm": "shortest_path", "params": {...} }`
   - **Output:** Algorithm metrics/results.

5. **Anomaly Tool**
   - **Name:** `fetch_anomalies`
   - **Description:** Retrieve anomalies related to an entity.
   - **Input:** `{ "entity_id": "uuid" }`
   - **Output:** List of anomalies.

6. **Timeline Tool**
   - **Name:** `generate_timeline`
   - **Description:** Extract a chronological sequence of events for an entity.
   - **Input:** `{ "entity_ids": ["uuid"], "start_date": "date", "end_date": "date" }`
   - **Output:** Sorted array of events.

7. **Evidence Tool**
   - **Name:** `fetch_evidence`
   - **Description:** Get provenance for a specific claim or entity.
   - **Input:** `{ "target_id": "uuid" }`
   - **Output:** Evidence chain structure.
