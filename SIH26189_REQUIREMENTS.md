# SIH26189 — ICA_AI Transformation Requirements

> **Single Source of Truth for AI-Assisted Development**
>
> This document defines the requirements, target capabilities, architecture, implementation priorities, constraints, and acceptance criteria for transforming the existing **ICA_AI** project into a solution relevant to **Smart India Hackathon Problem Statement SIH26189**.
>
> **IMPORTANT:** Every AI coding agent working on this repository MUST read this file before implementing, modifying, refactoring, or removing any feature.

---

# 1. Project Identity

## Existing Project

**ICA_AI — Intelligent Crime Analytics & AI Assistant**

Current architecture:

* Next.js
* React
* TypeScript
* Tailwind CSS
* FastAPI
* Python
* PostgreSQL
* Neo4j
* Redis
* pgvector
* LangChain
* LLM provider abstraction
* HuggingFace embeddings
* MapLibre
* JWT
* RBAC

## Target Project

Transform ICA_AI into:

> **AI-Powered Criminal Intelligence & Network Investigation Platform**

The system must support investigators in analyzing fragmented crime/intelligence data, discovering relationships, identifying influential entities, detecting suspicious activity, exploring evidence, and querying the intelligence system using natural language.

---

# 2. SIH26189 Core Objective

The system must be capable of transforming heterogeneous crime/intelligence data into actionable investigative intelligence.

The target pipeline is:

```text
Multiple Data Sources
        ↓
Data Ingestion
        ↓
Cleaning & Normalization
        ↓
NLP / Entity Extraction
        ↓
Entity Resolution
        ↓
Knowledge Graph
        ↓
Graph Analytics
        ↓
Anomaly Detection
        ↓
Link / Relationship Analysis
        ↓
Evidence Retrieval
        ↓
AI Investigator Copilot
        ↓
Investigator Dashboard
```

---

# 3. Critical Development Principle

## DO NOT treat README.md as the source of truth.

The actual implementation is the source of truth.

This file is the **target requirements specification**.

Before implementing any feature:

1. Inspect the existing implementation.
2. Determine its current status.
3. Reuse working components where possible.
4. Modify only what is necessary.
5. Do not duplicate existing services.
6. Do not create parallel architectures unnecessarily.
7. Preserve working functionality.
8. Update the implementation only after understanding the existing architecture.

---

# 4. Existing ICA_AI Baseline

The existing audit identified the following baseline.

## Fully Implemented / Strong Foundation

* JWT authentication
* RBAC
* PostgreSQL integration
* Neo4j integration
* Criminal network graph
* RAG/vector search
* LLM provider abstraction
* Natural-language crime assistant
* Basic CRUD APIs
* Redis infrastructure
* Next.js frontend foundation

## Partially Implemented

* Dashboard analytics
* Repeat offender analysis
* Timeline
* System health
* Security hardening
* Frontend/backend integration

## Mocked / Demo

* Predictive crime analytics
* Crime hotspot data
* Explainable AI
* LangGraph FIR extraction
* Some frontend analytics

## Missing

* Genuine XGBoost/LightGBM pipelines
* Real entity extraction pipeline
* Robust entity resolution
* Network anomaly detection
* Strong link prediction
* Dynamic evidence provenance
* Fully dynamic map data
* Complete investigation workspace

---

# 5. Target Feature Set

The final ICA_AI system should contain the following major modules.

## Priority Definitions

### P0 — Critical

Required for SIH26189 relevance.

### P1 — High

Strongly recommended for a competitive solution.

### P2 — Medium

Useful enhancement.

### P3 — Optional

Only implement if time permits.

---

# 6. P0 — Multi-Source Data Ingestion

## Requirement

The platform must ingest heterogeneous crime/intelligence data.

Supported sources should include:

* FIR documents
* Police reports
* Criminal records
* Case records
* CDR data
* Financial transactions
* Vehicle records
* Phone records
* Location data
* Organization data
* Intelligence reports
* Other structured/unstructured datasets

## Supported formats

At minimum:

* PDF
* TXT
* CSV
* JSON

## Architecture

```text
Source
 ↓
Parser
 ↓
Normalizer
 ↓
Validator
 ↓
Entity Extraction
 ↓
Entity Resolution
 ↓
Storage
```

## Acceptance Criteria

* User/system can ingest supported files.
* Data is validated.
* Invalid records are reported.
* Source metadata is preserved.
* Data reaches PostgreSQL and/or Neo4j appropriately.
* Documents can be indexed for semantic search.
* Ingestion must not rely on manually hardcoded relationships.

---

# 7. P0 — Document Processing

## Requirement

Process FIRs and intelligence documents automatically.

Pipeline:

```text
PDF
 ↓
Text Extraction
 ↓
Cleaning
 ↓
Chunking
 ↓
Metadata Extraction
 ↓
Entity Extraction
 ↓
Embedding
 ↓
Vector Storage
```

## Metadata

Each document should preserve:

* document ID
* source
* case ID
* page
* timestamp
* document type
* ingestion timestamp

## Acceptance Criteria

* PDF text is extracted.
* Text can be searched.
* Relevant chunks can be retrieved.
* Source/page information is retained.
* Documents can be linked to graph entities.

---

# 8. P0 — NLP Entity Extraction

## Requirement

Automatically extract entities from unstructured documents.

Required entity types:

```text
PERSON
ORGANIZATION
LOCATION
PHONE
VEHICLE
CASE
CRIME
DATE
EVENT
FINANCIAL_ACCOUNT
```

## Example

Input:

```text
Ravi Kumar met Suresh near MG Road using
vehicle KA01AB1234.
```

Expected:

```text
PERSON:
Ravi Kumar
Suresh

LOCATION:
MG Road

VEHICLE:
KA01AB1234
```

## Requirements

Every extracted entity should have:

* entity type
* normalized value
* source document
* page/position if available
* confidence score

## Acceptance Criteria

* Extraction is genuinely model/algorithm driven.
* No hardcoded entity outputs.
* Extraction results can feed the graph.
* Low-confidence entities can be reviewed.

---

# 9. P0 — Entity Normalization

Different representations of the same entity must be normalized.

Examples:

```text
Ravi Kumar
R. Kumar
Ravi K.
```

should become candidate representations of the same canonical entity.

Normalize:

* names
* phone numbers
* vehicle numbers
* locations
* organizations
* account identifiers

---

# 10. P0 — Entity Resolution

## Requirement

Determine whether records from different sources refer to the same real-world entity.

Example:

```text
Dataset A:
Ravi Kumar
Phone: 9876543210

Dataset B:
R. Kumar
Phone: +91 9876543210
```

System:

```text
Potential Match
Score: 94%

Evidence:
✓ Name similarity
✓ Same phone
```

## Matching signals

Use combinations of:

* name similarity
* phone
* address
* vehicle
* organization
* location
* temporal overlap
* other permitted identifiers

## Output

```text
canonical_entity_id
match_score
matching_features
source_records
```

## Acceptance Criteria

* Duplicate entities can be identified.
* Matching score is explainable.
* Original source records are preserved.
* False matches are not silently merged.
* High-risk merges can require review.

---

# 11. P0 — Knowledge Graph

## Database

**Neo4j**

## Required entity types

At minimum:

```text
Person
Organization
Location
Vehicle
Phone
Case
Crime
FinancialAccount
Document
Event
```

## Required relationship types

Examples:

```text
ASSOCIATED_WITH
INVOLVED_IN
USES
OWNS
LOCATED_AT
WORKS_FOR
TRANSFERRED_TO
MENTIONS
OCCURRED_AT
CONNECTED_TO
PARTICIPATED_IN
```

Only create relationships supported by source evidence or explicit analytical inference.

---

# 12. Dynamic Graph Construction

The graph must be generated from actual ingested data.

DO NOT rely on:

```text
hardcoded nodes
hardcoded relationships
static graph JSON
```

The pipeline must be:

```text
Source Data
 ↓
Entity Extraction
 ↓
Entity Resolution
 ↓
Relationship Extraction
 ↓
Neo4j
```

---

# 13. P0 — Graph Visualization

The graph interface must allow investigators to:

* search entities
* expand relationships
* collapse relationships
* filter node types
* filter relationship types
* filter dates
* inspect evidence
* highlight suspicious relationships
* find shortest paths
* find common connections
* inspect communities
* inspect influential nodes

Example:

```text
Person
 ↓
Phone
 ↓
Person
 ↓
Case
 ↓
Location
```

---

# 14. P0 — Graph Centrality

Implement graph analytics to identify influential entities.

Required algorithms:

### Degree Centrality

Measures direct connections.

### Betweenness Centrality

Identifies bridge entities.

### Closeness Centrality

Measures structural proximity.

### PageRank

Measures network influence.

## Output

```text
Entity:
Ravi Kumar

Influence Score:
91

Degree:
37

Betweenness:
High

Community:
Group A
```

Scores must be based on actual graph calculations.

---

# 15. P0 — Community Detection

Identify groups/clusters within criminal networks.

Possible algorithms:

* Louvain
* Leiden
* Connected Components

Output:

```text
Community #1

Members: 14
Cases: 8
Vehicles: 5
Locations: 6

Key Entity:
Ravi Kumar
```

---

# 16. P0 — Suspicious Activity Detection

The platform must identify unusual activity.

Analyze:

* communications
* financial transactions
* locations
* vehicles
* network relationships
* case involvement
* temporal patterns

Examples:

### Communication anomaly

Sudden increase in contacts.

### Financial anomaly

Unusual transaction amount/frequency.

### Location anomaly

Unexpected location pattern.

### Network anomaly

Sudden cross-community connection.

---

# 17. P0 — Network Anomaly Detection

Implement an actual anomaly engine.

Possible methods:

* statistical anomaly detection
* Isolation Forest
* Local Outlier Factor
* graph-based anomaly scoring
* temporal anomaly detection

Output:

```text
Anomaly Score: 91

Reasons:

+ New cross-community connection
+ Unusual transaction volume
+ Abnormal communication pattern
```

Do not use arbitrary hardcoded scores.

---

# 18. P1 — Link Prediction

Identify potentially important relationships that are not explicitly recorded.

Start with:

* Common Neighbors
* Jaccard Similarity
* Adamic-Adar
* Resource Allocation

Optional:

* Node2Vec
* Graph embeddings
* GNN

Example:

```text
Potential Relationship

Person A ↔ Person B

Score: 82%

Evidence:

3 common associates
2 shared locations
Temporal overlap
```

The system MUST clearly label inferred relationships as predictions rather than confirmed facts.

---

# 19. P0 — Evidence Provenance

Every important graph relationship, prediction and AI response must have traceable evidence.

Store:

```text
source_id
document_id
page
source_type
extraction_method
confidence
created_at
```

Example:

```text
Person A
      │
ASSOCIATED_WITH
      │
Person B

Evidence:
FIR-102.pdf
Page 7

Extraction:
NLP

Confidence:
87%
```

---

# 20. P0 — Investigator AI Copilot

The current AI Crime Assistant must evolve into an investigator-focused AI copilot.

The assistant must answer questions using actual system tools.

Possible tools:

```text
Neo4j Tool
SQL Tool
Vector Search Tool
Timeline Tool
Anomaly Detection Tool
Evidence Tool
Graph Analytics Tool
```

---

# 21. AI Copilot Example Questions

The system should support queries such as:

```text
Who is connected to Ravi Kumar?

Show the network around Ravi Kumar.

Who are the most influential people in this network?

Which people connect these two criminal groups?

Show unusual transactions associated with Ravi Kumar.

What evidence connects Ravi Kumar to Case 123?

What is the shortest path between Person A and Case B?

Why was Ravi Kumar flagged as suspicious?

Show all cases associated with this phone number.

Which entities appear across multiple cases?

What relationships are potentially missing from the current graph?
```

---

# 22. P1 — Agentic Reasoning

Use LangGraph or equivalent orchestration only if genuinely required.

Target flow:

```text
User Question
 ↓
Intent Detection
 ↓
Planning
 ↓
Tool Selection
 ↓
Neo4j / SQL / RAG / Analytics
 ↓
Evidence Aggregation
 ↓
Reasoning
 ↓
Answer
```

Do not create fake agent workflows.

---

# 23. P0 — Dynamic Crime Map

Replace static frontend hotspot arrays.

Map data must come from backend/database.

Architecture:

```text
PostgreSQL / Neo4j
 ↓
Geospatial Query
 ↓
GeoJSON API
 ↓
MapLibre
```

Required capabilities:

* crime density
* case locations
* suspicious activity
* entity locations
* network clusters
* temporal filters

---

# 24. P1 — Timeline Analysis

Every event should support timestamps.

Timeline should show:

```text
10 Aug
Phone interaction

12 Aug
Vehicle movement

14 Aug
Financial transaction

16 Aug
Crime incident
```

Allow filtering by:

* person
* case
* location
* event type
* date range

---

# 25. P1 — Case Investigation Workspace

Create an investigator workspace.

Sections:

```text
Case Overview
Persons
Organizations
Vehicles
Phones
Locations
Relationships
Timeline
Evidence
Network
Anomalies
AI Summary
Reports
```

The investigator should be able to move from:

```text
Case
 ↓
Person
 ↓
Network
 ↓
Evidence
 ↓
Timeline
 ↓
Analysis
```

without leaving the investigation context.

---

# 26. P1 — Investigation Reports

Generate evidence-grounded reports.

Report structure:

```text
Investigation Summary

Case Information

Key Individuals

Network Structure

Influential Entities

Suspicious Activities

Potential Relationships

Timeline

Supporting Evidence

Confidence

Data Sources
```

Every important claim must be traceable.

---

# 27. P1 — Risk / Investigation Priority Score

Create a transparent analytical score.

Possible components:

```text
Network Influence
+
Anomaly Score
+
Case Association
+
Temporal Pattern
+
Relationship Strength
```

The system MUST NOT state:

> "This person is a criminal."

Instead use:

> "Investigation Priority"

or:

> "Analytical Risk Indicator"

and show the supporting evidence.

---

# 28. P1 — Explainable AI

Every model/analytical output must explain why it was generated.

For ML:

* feature importance
* SHAP where appropriate

For graph:

```text
Degree
Betweenness
Community position
Relationship strength
```

For anomaly:

```text
Transaction deviation
Communication deviation
Location deviation
Network deviation
```

---

# 29. P1 — Source Reliability

Every data source should have metadata.

Example:

```text
Source Type:
Official FIR

Reliability:
High
```

Potential source categories:

```text
Official Record
Police Report
Structured Database
Intelligence Report
AI Inference
User/Analyst Input
```

Do not treat AI-generated inference as confirmed evidence.

---

# 30. P1 — Audit Trail

Track investigator activity.

Examples:

```text
Viewed Case
Viewed Person
Queried Network
Generated Report
Exported Report
Modified Investigation
```

Store:

```text
user_id
action
resource
timestamp
```

---

# 31. P0 — Security

Security is mandatory.

## Authentication

* JWT
* secure password hashing
* token expiration

## Authorization

* RBAC
* least privilege
* protected routes

## CORS

No wildcard CORS in production.

Use environment configuration.

## Secrets

Never hardcode:

* JWT secrets
* API keys
* database passwords
* LLM keys

## Neo4j

Do NOT expose arbitrary Cypher execution to normal users.

Use:

* parameterized queries
* predefined query services
* strict authorization

## Additional

Implement where appropriate:

* rate limiting
* input validation
* security headers
* audit logging
* safe error messages
* secret scanning

---

# 32. P0 — State-Agnostic Architecture

ICA_AI currently contains Karnataka/KSP-specific assumptions.

These must become configuration.

Do NOT hardcode:

```text
Karnataka
KSP
Bengaluru
Mysuru
Mangaluru
Karnataka district lists
Karnataka map bounds
```

Create configuration such as:

```text
STATE_NAME
POLICE_ORGANIZATION
DISTRICTS
SUPPORTED_LANGUAGES
MAP_BOUNDS
CRIME_CATEGORIES
```

The core platform must work independently of one state.

---

# 33. Multilingual Support

Existing Kannada support should be preserved and generalized.

Target architecture:

```text
User Language
 ↓
Language Detection
 ↓
Normalization / Translation
 ↓
NLP
 ↓
Canonical Representation
```

Potential languages:

* English
* Kannada
* Hindi
* Other required languages

The system must preserve entity names correctly during translation.

---

# 34. P2 — Predictive Crime Analytics

Predictive crime forecasting is secondary to network intelligence.

If retained, it must use real models.

Pipeline:

```text
Historical Data
 ↓
Feature Engineering
 ↓
Train/Test Split
 ↓
Model Training
 ↓
Evaluation
 ↓
Prediction
 ↓
Explainability
```

Possible models:

* XGBoost
* LightGBM
* Random Forest
* appropriate time-series models

Never present a moving average as machine learning.

---

# 35. P3 — Blockchain Evidence Integrity

Blockchain is OPTIONAL unless specifically required by the final SIH interpretation.

If implemented, use it for evidence integrity.

Example:

```text
Evidence
 ↓
Hash
 ↓
Immutable Record
```

Do NOT introduce cryptocurrency or unnecessary blockchain complexity.

---

# 36. P3 — Real-Time Streaming

Optional advanced feature.

Potential sources:

```text
CDR stream
Transaction stream
Location stream
```

Pipeline:

```text
Event
 ↓
Redis / Message Queue
 ↓
Processing
 ↓
Graph Update
 ↓
Anomaly Detection
 ↓
Alert
```

Only implement after core SIH functionality is complete.

---

# 37. Data Privacy Requirements

This system deals with highly sensitive information.

Use:

* synthetic/anonymized demo data
* controlled access
* source provenance
* minimal data exposure
* role-based access
* audit trails
* encrypted transport
* secure secrets

Never use unauthorized real criminal/personal data for demonstrations.

---

# 38. Frontend Requirements

The UI should be investigator-oriented.

Required major screens:

```text
Login
Dashboard
Investigation Workspace
Network Explorer
Entity Explorer
Evidence Explorer
Timeline
Crime Map
Anomaly Dashboard
AI Copilot
Reports
Administration
```

UI should prioritize:

* clarity
* evidence
* relationships
* explainability
* investigation workflow

Avoid unnecessary decorative dashboards.

---

# 39. Dashboard Requirements

Dashboard should display real backend data.

Recommended:

```text
Active Investigations
Cases
Persons
Organizations
Networks
High Priority Alerts
Anomalies
Influential Entities
Recent Activity
```

Charts must not use hardcoded mock arrays in production/demo mode.

---

# 40. AI Response Requirements

AI must:

1. Use actual data.
2. Cite/identify evidence where possible.
3. Distinguish facts from inference.
4. Distinguish predictions from confirmed relationships.
5. Avoid fabricating evidence.
6. Provide confidence where meaningful.
7. Explain reasoning at an appropriate level.
8. Respect user permissions.
9. Never expose unauthorized data.

---

# 41. Graph Intelligence Requirements

The graph engine should eventually support:

```text
Shortest Path
Common Neighbors
Community Detection
Centrality
Influence Ranking
Relationship Filtering
Temporal Graph Analysis
Anomaly Detection
Link Prediction
```

---

# 42. Data Model Requirements

Every important entity should have:

```text
id
type
source
created_at
updated_at
confidence
```

Relationships should support:

```text
source
target
relationship_type
timestamp
confidence
evidence
```

---

# 43. Architecture Rules

## Reuse first

Before creating a new service:

1. Search the repository.
2. Determine whether equivalent functionality exists.
3. Extend existing service if appropriate.

## No duplicate systems

Do not create:

```text
graph_service_v2.py
graph_service_new.py
graph_service_final.py
```

without architectural justification.

## API consistency

Follow the existing API structure.

## Database consistency

Do not create a second database architecture.

## Frontend consistency

Reuse existing UI components.

---

# 44. Anti-Mock Rule

This is mandatory.

Never implement a feature using:

```text
hardcoded arrays
fake predictions
fake confidence
static graph relationships
placeholder AI answers
fake API responses
```

unless explicitly labelled as demo/test fixtures.

If real implementation cannot yet be completed:

```text
TODO
```

should be documented rather than pretending it works.

---

# 45. No Hallucinated AI

The AI system must never invent:

* criminal relationships
* evidence
* cases
* transactions
* locations
* people
* organizations

All generated intelligence must be grounded in available data.

---

# 46. Feature Status System

Every major feature should have one of these statuses:

```text
✅ FULLY IMPLEMENTED

🟡 PARTIALLY IMPLEMENTED

🔵 IMPLEMENTED BUT UNVERIFIED

🟠 MOCKED / DEMO

❌ NOT IMPLEMENTED

⚠️ BROKEN
```

---

# 47. Definition of Done

A feature is considered **FULLY IMPLEMENTED** only when:

* Backend logic exists.
* Frontend integration exists where applicable.
* Database integration exists where applicable.
* Real data is processed.
* No hardcoded production behavior exists.
* Error handling exists.
* Authentication/authorization is respected.
* Feature can be demonstrated.
* Relevant tests exist where practical.
* Documentation is updated.

---

# 48. SIH26189 Priority Matrix

| Feature                       | Priority |
| ----------------------------- | -------- |
| Multi-source ingestion        | P0       |
| FIR/document processing       | P0       |
| NLP entity extraction         | P0       |
| Entity normalization          | P0       |
| Entity resolution             | P0       |
| Dynamic Neo4j graph           | P0       |
| Graph visualization           | P0       |
| Centrality analysis           | P0       |
| Influential person detection  | P0       |
| Community detection           | P0       |
| Suspicious activity detection | P0       |
| Network anomaly detection     | P0       |
| Evidence provenance           | P0       |
| Investigator AI Copilot       | P0       |
| Security hardening            | P0       |
| State-agnostic configuration  | P0       |
| Dynamic crime map             | P1       |
| Timeline                      | P1       |
| Link prediction               | P1       |
| Case investigation workspace  | P1       |
| Investigation reports         | P1       |
| Risk/priority scoring         | P1       |
| Explainable AI                | P1       |
| Source reliability            | P1       |
| Audit trail                   | P1       |
| Multilingual NLP              | P1       |
| Predictive crime forecasting  | P2       |
| Advanced GNN                  | P2       |
| Blockchain evidence integrity | P3       |
| Real-time streaming           | P3       |

---

# 49. Recommended Implementation Order

The project MUST generally progress in this order unless technical dependencies require otherwise.

## Phase 1 — Foundation

* Security hardening
* State abstraction
* API cleanup
* Database validation

## Phase 2 — Data Intelligence

* Multi-source ingestion
* Document processing
* NLP entity extraction
* Entity normalization
* Entity resolution

## Phase 3 — Knowledge Graph

* Dynamic graph construction
* Expanded schema
* Evidence relationships
* Graph visualization

## Phase 4 — Graph Intelligence

* Centrality
* Influence scoring
* Community detection
* Shortest path
* Network analysis

## Phase 5 — Suspicious Activity

* Anomaly detection
* Temporal analysis
* Network anomaly detection
* Investigation priority

## Phase 6 — Hidden Relationships

* Link prediction
* Graph similarity
* Relationship confidence

## Phase 7 — Investigator Copilot

* Neo4j tools
* SQL tools
* RAG
* Evidence retrieval
* Agentic reasoning

## Phase 8 — Investigation UI

* Case workspace
* Timeline
* Dynamic map
* Evidence explorer
* Network explorer

## Phase 9 — Reporting

* Evidence-grounded reports
* AI summaries
* Export

## Phase 10 — Advanced

* Predictive analytics
* Multilingual
* Local LLM
* Blockchain integrity
* Streaming

---

# 50. Target End-to-End Demonstration

The final system should support this complete scenario:

```text
1. Investigator uploads FIR/report data
            ↓
2. System extracts entities
            ↓
3. Entities are normalized
            ↓
4. Duplicate identities are resolved
            ↓
5. Relationships are extracted
            ↓
6. Neo4j graph is constructed
            ↓
7. Investigator opens a person
            ↓
8. Network is visualized
            ↓
9. Centrality identifies influential entities
            ↓
10. Community detection identifies groups
            ↓
11. Anomaly engine detects unusual behavior
            ↓
12. Link prediction identifies potential relationships
            ↓
13. Evidence is retrieved from documents
            ↓
14. Investigator asks AI Copilot questions
            ↓
15. AI queries Neo4j / SQL / RAG / Analytics
            ↓
16. AI returns evidence-grounded answer
            ↓
17. Investigator reviews timeline/map
            ↓
18. System generates investigation report
```

This is the primary target workflow.

---

# 51. Example Final Investigator Scenario

The system should be able to demonstrate:

### Input

```text
FIR_001.pdf
CDR.csv
Transactions.csv
VehicleRecords.csv
CriminalRecords.csv
```

### Processing

```text
Entities extracted:
47 persons
18 locations
12 vehicles
31 phones
9 organizations
23 cases
```

### Entity Resolution

```text
Ravi Kumar
R. Kumar
Ravi K.

→ Canonical Entity #P102
```

### Graph

```text
Person
 ↓
Phone
 ↓
Person
 ↓
Vehicle
 ↓
Location
 ↓
Case
```

### Graph Analysis

```text
Top Influencer:
Ravi Kumar

Influence Score:
91
```

### Anomaly

```text
Suspicious Activity:
High

Reasons:
- unusual communication spike
- abnormal transaction
- new cross-community relationship
```

### Link Prediction

```text
Potential relationship:
Ravi Kumar ↔ Person X

Score:
82%
```

### AI

Investigator:

```text
Why was Ravi Kumar flagged?
```

System:

```text
Ravi Kumar was assigned a high investigation-priority
score because of:

1. High network centrality.
2. Recent cross-community connections.
3. Abnormal transaction activity.
4. Increased communication frequency.

Supporting evidence:
FIR-001, CDR-202, Transaction-88.
```

The system must clearly distinguish:

```text
CONFIRMED FACT
vs
ANALYTICAL INFERENCE
vs
PREDICTION
```

---

# 52. Final Success Criteria

ICA_AI will be considered SIH26189-ready when the following are true:

## Data

* [ ] Multiple data sources supported
* [ ] FIR/document ingestion works
* [ ] Structured data ingestion works
* [ ] Data normalization works
* [ ] Source provenance preserved

## NLP

* [ ] Entity extraction works
* [ ] Entity normalization works
* [ ] Entity resolution works
* [ ] Confidence is available

## Graph

* [ ] Neo4j graph is dynamically generated
* [ ] Multiple entity types supported
* [ ] Multiple relationship types supported
* [ ] Evidence linked to relationships
* [ ] Graph visualization is dynamic
* [ ] Centrality works
* [ ] Community detection works
* [ ] Influential entities are identified

## Intelligence

* [ ] Suspicious activity detection works
* [ ] Network anomaly detection works
* [ ] Timeline analysis works
* [ ] Link prediction works
* [ ] Investigation priority scoring works
* [ ] Results are explainable

## AI

* [ ] AI Copilot uses real system data
* [ ] Neo4j tool available
* [ ] SQL tool available
* [ ] RAG available
* [ ] Evidence retrieval works
* [ ] AI does not fabricate evidence
* [ ] Facts and predictions are distinguished

## Visualization

* [ ] Dynamic network graph
* [ ] Dynamic crime map
* [ ] Timeline
* [ ] Evidence panel
* [ ] Investigation dashboard

## Security

* [ ] JWT
* [ ] RBAC
* [ ] Secure secrets
* [ ] Restricted CORS
* [ ] Parameterized Neo4j queries
* [ ] Audit logs
* [ ] Input validation

## Deployment

* [ ] No Karnataka hardcoding
* [ ] State configuration exists
* [ ] Demo dataset is synthetic/anonymized/authorized
* [ ] Environment configuration works
* [ ] Production secrets are not committed

---

# 53. Mandatory Instructions for AI Coding Agents

Whenever an AI agent receives a task in this repository:

## FIRST

Read:

```text
SIH26189_REQUIREMENTS.md
```

Then inspect the existing implementation.

## SECOND

Determine:

```text
What already exists?
What is missing?
What is broken?
What can be reused?
```

## THIRD

Implement the requested feature according to this document.

## FOURTH

Do not break existing functionality.

## FIFTH

Test the implementation.

## SIXTH

Report:

```text
Implemented:
Files changed:
APIs changed:
Database changes:
Tests:
Verification:
Remaining limitations:
SIH26189 requirement satisfied:
```

---

# 54. Change Management Rule

When a feature is implemented:

1. Update its status.
2. Document the implementation.
3. Add tests where practical.
4. Do not falsely mark incomplete functionality as complete.

The requirements document should remain synchronized with the actual project.

---

# 55. Final Product Vision

ICA_AI should ultimately become:

> **A secure, evidence-grounded AI criminal intelligence platform that converts fragmented structured and unstructured crime data into a dynamic knowledge graph, performs graph and behavioral analytics, identifies influential entities and suspicious patterns, discovers potential hidden relationships, and provides investigators with an explainable natural-language intelligence copilot.**

The platform should be:

```text
Evidence Grounded
        +
Graph Driven
        +
AI Assisted
        +
Explainable
        +
Secure
        +
State Agnostic
        +
Investigator Centric
```

---

# 56. Final Rule

**Do not build features merely because they sound impressive.**

Every feature must answer:

> **How does this help an investigator analyze criminal networks, discover relationships, identify influential entities, detect suspicious activity, or understand evidence?**

If a feature does not contribute meaningfully to that objective, it is secondary and should not take priority over unfinished P0 requirements.

**SIH26189_REQUIREMENTS.md is the target specification.
The actual codebase is the implementation source of truth.
Never confuse the two.**
