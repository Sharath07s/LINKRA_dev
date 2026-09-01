# SIH26189 UI/UX FOUNDATION

## Architecture Overview

The `ICA_AI` frontend has been updated to provide a robust UI/UX foundation aligned with the SIH26189 `SIH_UI_UX.md` specification. 

### 1. Reusable Primitives
We integrated standard `shadcn/ui` components to ensure cross-application consistency.
- Standard UI elements: `Button`, `Card`, `Tabs`, `Badge`, `Input`, `Table`, `Alert`, `Dialog`, `Skeleton`, `Select`, `Tooltip`, etc.
- Custom state components in `components/ui/`: `EmptyState`, `ErrorState`, `LoadingState`. These prevent "blank screens" when backend services (Neo4j, FastAPI) are disconnected or loading.

### 2. Global Application Shell
The main `DashboardLayout.tsx` has been refactored to:
- Use grouped navigation (`OVERVIEW`, `INVESTIGATIONS`, `INTELLIGENCE`, `OPERATIONS`, `SYSTEM`).
- Enforce strict Role-Based Access Control (RBAC). For example, `ADMIN` sees System Health, while `OFFICER` sees Command Wall and Officer Workspace.

### 3. Investigation Workspace Core
We implemented the primary intelligence layout under `/investigations/[id]`.
- **Case Summary Layout**: Displays critical alerts, network summaries, and entity highlights in an intelligence-briefing format.
- **Tabbed Interface**: `Overview`, `Network Graph`, `Timeline`, `Map`, `Evidence`, `AI Copilot`.
- **Isolated Containers**: Added `GraphContainer`, `MapContainer`, `TimelineView`, `EvidenceList`, and `AICopilotPanel` which act as secure wrappers for future backend integrations. Currently, they display professional `EmptyState` interfaces, strictly preventing the fabrication of mock intelligence.

### 4. Intelligence Containers
New components in `components/Intelligence/` standardise how AI output is displayed:
- `AnomalyCard`: Displays detected anomalies with severity, ID, entity link, and status (New, Investigating, Confirmed).
- `AlertCard`: For real-time push notifications of intelligence events.

### 5. Operations Scaffold
Added shell routes for `Data Ingestion` (`/ingestion`) and `Entity Resolution` (`/resolution`) to prepare for the data pipeline integration.

### Summary
The foundation is now ready. Phase 2 (Backend Intelligence Integration) can now plug real Neo4j, PostgreSQL, and Gemini API data directly into these standardized containers without altering the layout or UX.
