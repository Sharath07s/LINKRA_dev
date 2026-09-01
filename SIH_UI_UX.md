# SIH26189 — UI/UX DESIGN SYSTEM & EXPERIENCE SPECIFICATION

## Document Status

Status: FOUNDATION SPECIFICATION
Project: SIH26189 Intelligence Platform
Repository: ICA_AI
Phase: Post-Phase-1 / Pre-Phase-2
Document: UI_UX.md

This document is the authoritative UI/UX foundation for the SIH26189 platform.

All future frontend development must follow this specification unless a deliberate design decision is documented and approved.

---

# 1. DESIGN OBJECTIVE

The SIH26189 platform is not a normal CRUD dashboard.

It is an intelligence and investigation platform intended to help investigators:

- ingest information
- discover entities
- resolve duplicate identities
- investigate relationships
- analyze networks
- identify anomalies
- inspect evidence
- understand timelines
- explore geographic intelligence
- interact with AI-assisted intelligence
- generate reports
- maintain evidence provenance

The UI must therefore optimize for:

1. Speed
2. Clarity
3. Information hierarchy
4. Investigative workflow efficiency
5. Trust
6. Evidence traceability
7. Consistency
8. Accessibility
9. Responsiveness
10. Professional enterprise appearance

The interface must feel like a serious intelligence-analysis product rather than a generic admin dashboard.

---

# 2. PRIMARY UX PRINCIPLE

## "Evidence First. Intelligence Second. Decoration Last."

The interface must never prioritize visual effects over investigative usefulness.

Every major visual element should answer at least one of:

- What happened?
- Where did it happen?
- Who is involved?
- How are entities connected?
- What evidence supports this?
- What changed?
- What requires attention?
- What should the investigator investigate next?

---

# 3. TARGET USER

Primary user:

## Investigator / Intelligence Officer

The UI should assume the user may work with:

- large datasets
- many entities
- multiple cases
- complex relationships
- long timelines
- maps
- evidence documents
- alerts
- AI-generated intelligence

The interface should minimize unnecessary navigation.

---

# 4. UX PRINCIPLES

## 4.1 Clarity Over Complexity

Do not show every available field at once.

Use:

- progressive disclosure
- expandable sections
- drawers
- tabs
- contextual panels
- detail views

Important information should remain immediately visible.

---

## 4.2 Familiar Navigation

Navigation must behave predictably.

Users should always understand:

- where they are
- what module they are using
- what case they are investigating
- how to return
- what actions are available

Avoid experimental navigation patterns.

---

## 4.3 Consistency

The same interaction should always behave the same way.

Examples:

If clicking an entity opens a detail drawer:

Every entity should use the same pattern.

If filters appear in a panel:

All intelligence modules should use the same filter pattern.

If loading states use skeletons:

Use the same skeleton language throughout the platform.

---

## 4.4 Information Density Without Clutter

The platform handles large amounts of intelligence.

Therefore:

Do NOT use excessive whitespace that forces unnecessary scrolling.

But also:

Do NOT create dense walls of information.

Use:

- clear grouping
- compact cards
- strong headings
- spacing hierarchy
- visual separators
- expandable sections

---

## 4.5 Progressive Disclosure

Show:

PRIMARY INFORMATION
↓
SECONDARY INFORMATION
↓
DETAILED INFORMATION
↓
RAW / TECHNICAL INFORMATION

Example:

Suspect:

Name
Risk indicator
Current status

↓

Known identities
Associates
Locations

↓

Timeline

↓

Evidence

↓

Raw source records

---

# 5. VISUAL DIRECTION

## Design Character

The platform should feel:

- professional
- modern
- authoritative
- analytical
- trustworthy
- technically sophisticated
- calm
- focused

Avoid:

- gaming UI
- excessive neon
- excessive gradients
- excessive glassmorphism
- huge decorative illustrations
- unnecessary animations
- excessive rounded cards
- flashy dashboards

---

# 6. COLOR SYSTEM

## Primary Theme

Use a dark-first intelligence workspace.

Primary background:

Deep charcoal / near-black

Secondary background:

Dark slate

Surface:

Elevated dark panels

Border:

Subtle low-contrast borders

Primary accent:

Blue / cyan intelligence accent

Semantic colors:

SUCCESS
Green

WARNING
Amber

CRITICAL
Red

INFO
Blue

NEUTRAL
Slate

---

## Color Rule

Color must communicate meaning.

Do not use color merely for decoration.

Example:

RED = critical threat

AMBER = attention required

GREEN = healthy / verified

BLUE = informational

GRAY = neutral

---

# 7. ACCESSIBILITY

Target:

WCAG 2.2 AA where practical.

Requirements:

- keyboard navigation
- visible focus states
- semantic HTML
- accessible labels
- meaningful ARIA labels where necessary
- sufficient color contrast
- no information communicated only through color
- accessible dialogs
- accessible tooltips
- keyboard-accessible graphs/maps where possible
- reduced-motion support

Interactive elements must have:

- name
- role
- state

Do not create inaccessible custom controls when native controls are sufficient.

---

# 8. TYPOGRAPHY

Use a modern highly readable sans-serif.

Recommended:

Inter

Fallback:

system-ui, sans-serif

Typography hierarchy:

Display
↓
Page title
↓
Section title
↓
Card title
↓
Body
↓
Secondary text
↓
Metadata

Avoid excessive font weights.

Typography should communicate hierarchy rather than decoration.

---

# 9. SPACING SYSTEM

Use a consistent spacing scale.

Recommended base:

4px

Common values:

4
8
12
16
20
24
32
40
48
64

Never randomly choose spacing values.

---

# 10. BORDER RADIUS

Use moderate rounding.

Recommended:

Small controls:
6px

Cards:
8–12px

Large containers:
12–16px

Avoid extremely rounded "pill everything" interfaces.

---

# 11. SHADOWS

Use shadows sparingly.

Dark interfaces should primarily use:

- borders
- surface contrast
- elevation

rather than huge shadows.

---

# 12. GLOBAL APPLICATION LAYOUT

The application uses:

┌───────────────────────────────────────────────────────────┐
│ TOP BAR                                                   │
├───────────────┬───────────────────────────────────────────┤
│               │                                           │
│ SIDEBAR       │ MAIN CONTENT                              │
│               │                                           │
│ Navigation    │                                           │
│               │                                           │
│               │                                           │
│               │                                           │
└───────────────┴───────────────────────────────────────────┘

---

# 13. SIDEBAR

The sidebar is the primary navigation.

Structure:

SIH26189
Intelligence Platform

--------------------------------

OVERVIEW

Dashboard

--------------------------------

INVESTIGATIONS

Investigations
Entities
Evidence

--------------------------------

INTELLIGENCE

Knowledge Graph
Anomalies
Influencers
Potential Links
Intelligence Map
Timeline

--------------------------------

OPERATIONS

Data Sources
Reports

--------------------------------

SYSTEM

Administration

--------------------------------

User Profile

---

# 14. SIDEBAR BEHAVIOR

Desktop:

Expanded sidebar.

Tablet:

Collapsible sidebar.

Small screens:

Drawer navigation.

Sidebar must support:

- active route indicator
- hover state
- keyboard navigation
- tooltip when collapsed
- role-based menu visibility

---

# 15. TOP BAR

The top bar contains:

LEFT:

Breadcrumb / current workspace

CENTER:

Optional global search

RIGHT:

Notifications
System status
User profile

---

# 16. GLOBAL SEARCH

Global search should eventually support:

- people
- suspects
- cases
- FIRs
- vehicles
- locations
- organizations
- evidence
- reports

Search UI should support:

- keyboard shortcut
- recent searches
- grouped results
- entity type indicators

Suggested shortcut:

CMD/CTRL + K

Do not implement fake search results.

During foundation stage:

Build the interface only.

---

# 17. DASHBOARD

The dashboard is the investigator's operational overview.

Structure:

## Header

Good morning, Investigator

Current operational summary

[Date]

---

## Priority Intelligence

Critical alerts
Pending investigations
Recent anomalies

---

## Intelligence Overview

Cards:

Active Investigations
New Intelligence
Unresolved Entities
Critical Alerts

These cards must eventually use real backend data.

During UI foundation:

Use empty/loading states instead of fake statistics.

---

## Activity

Recent investigation activity.

---

## Intelligence Map Preview

Large map container.

Foundation state:

"Map intelligence will appear here."

Do not invent locations.

---

# 18. INVESTIGATIONS

Main investigation list.

Features:

- search
- filtering
- sorting
- status
- priority
- assigned investigator
- last updated

Table structure:

Case ID
Title
Priority
Status
Assigned
Updated
Actions

---

# 19. INVESTIGATION WORKSPACE

This is one of the most important UI areas.

Structure:

┌───────────────────────────────────────────────────────────┐
│ CASE HEADER                                               │
├───────────────────────────────────────────────────────────┤
│ Overview | Network | Timeline | Map | Evidence | Copilot │
├───────────────────────────────────────────────────────────┤
│                                                           │
│                    ACTIVE VIEW                            │
│                                                           │
└───────────────────────────────────────────────────────────┘

---

# 20. CASE HEADER

Show:

Case ID
Case title
Status
Priority
Assigned officer
Last updated

Actions:

Export
Share
Add evidence
Open Copilot

Actions must respect RBAC.

---

# 21. CASE OVERVIEW

Sections:

Summary

Key Entities

Important Events

Evidence Summary

Intelligence Signals

Related Cases

---

# 22. NETWORK VIEW

Primary visualization:

Knowledge graph.

UI structure:

┌───────────────────────────────┬───────────────────────────┐
│                               │                           │
│       GRAPH CANVAS            │ ENTITY DETAILS            │
│                               │                           │
│                               │                           │
├───────────────────────────────┴───────────────────────────┤
│ Graph controls / filters                                  │
└───────────────────────────────────────────────────────────┘

Graph controls:

Zoom
Pan
Reset
Fit
Filter
Expand
Focus
Hide
Show relationships

Never display fabricated relationships.

---

# 23. GRAPH NODE DESIGN

Different entities should have distinguishable visual types.

Examples:

PERSON
VEHICLE
LOCATION
ORGANIZATION
CASE
PHONE
ACCOUNT

Use:

- icon
- label
- semantic color
- status indicator

Do not rely only on color.

---

# 24. TIMELINE

Timeline should support:

- chronological events
- event grouping
- filtering
- source indicators
- entity association

Visual:

EVENT
│
├── Timestamp
├── Description
├── Entity
└── Evidence

Timeline must remain readable even with many events.

---

# 25. MAP

Map workspace:

┌──────────────────────────────────────────────────────────┐
│ FILTERS                                                  │
├───────────────────────────────────────┬──────────────────┤
│                                       │                  │
│               MAP                     │ DETAILS          │
│                                       │                  │
│                                       │                  │
└───────────────────────────────────────┴──────────────────┘

Map controls:

Zoom
Layers
Filters
Location search
Time filter
Entity filter

Never fabricate map markers.

---

# 26. EVIDENCE

Evidence is a first-class concept.

Evidence cards should show:

Source
Evidence type
Timestamp
Confidence
Related entity
Provenance status

Example:

┌────────────────────────────────────────┐
│ DOCUMENT                               │
│ FIR-2026-00123                         │
│                                        │
│ Source: Police Record                  │
│ Added: 12 Aug 2026                     │
│                                        │
│ [View Evidence] [View Provenance]      │
└────────────────────────────────────────┘

---

# 27. PROVENANCE

Every AI-generated or analytical claim should eventually be traceable.

UI should communicate:

AI-derived
Source-derived
Analyst-confirmed
Unverified

Never visually present AI inference as confirmed fact.

---

# 28. INTELLIGENCE ALERTS

Alert hierarchy:

CRITICAL
HIGH
MEDIUM
LOW
INFO

Alert card:

Severity
Title
Reason
Timestamp
Related entities
Source
Action

Example:

CRITICAL

Potential Network Connection

Supporting evidence available.

[Investigate]

Do not invent numerical confidence values.

---

# 29. ANOMALY UI

Anomaly cards should show:

Anomaly type
Detected time
Affected entity
Reason
Supporting evidence
Status

Possible states:

New
Investigating
Confirmed
Dismissed

---

# 30. INFLUENCER / NETWORK ANALYSIS

Use ranked analytical cards.

Example:

Entity

Network Centrality
Relationship Count
Connected Cases

But values must come from real backend analytics.

Foundation state:

Use skeletons or "Analysis unavailable".

---

# 31. ENTITY RESOLUTION

UI should clearly distinguish:

Potential duplicate

vs

Confirmed canonical entity

Example:

┌────────────────────────────────────────────┐
│ POSSIBLE MATCH                             │
│                                            │
│ Entity A              Entity B             │
│                                            │
│ Name                 Name                  │
│ DOB                  DOB                   │
│ Phone                Phone                 │
│                                            │
│ Match signals:                            │
│ • Name similarity                         │
│ • Shared phone                            │
│                                            │
│ [Review] [Reject] [Merge]                 │
└────────────────────────────────────────────┘

Never automatically imply a match is confirmed.

---

# 32. DATA INGESTION

Upload interface:

Drag & drop area

Supported formats

Upload progress

Validation

Processing state

Completion

Failure

Example flow:

SELECT FILE
↓
VALIDATING
↓
UPLOADING
↓
PROCESSING
↓
EXTRACTING
↓
READY

Never fake processing progress.

---

# 33. AI COPILOT

Copilot should feel like an investigation assistant.

Layout:

┌─────────────────────────────────────────────┐
│ AI COPILOT                                  │
├─────────────────────────────────────────────┤
│                                             │
│ Conversation                                │
│                                             │
├─────────────────────────────────────────────┤
│ Evidence / Sources                          │
├─────────────────────────────────────────────┤
│ Ask about this investigation...             │
└─────────────────────────────────────────────┘

Important:

AI responses must distinguish:

Answer

Evidence

Sources

Confidence / uncertainty where supported

Suggested next actions

Never make unsupported claims appear factual.

---

# 34. AI RESPONSE DESIGN

Use:

### Answer

Concise explanation.

### Evidence

Supporting records.

### Sources

Clickable provenance.

### Suggested Investigation

Possible next actions.

This creates trust.

---

# 35. REPORTS

Reports page:

Reports list

Filters

Status

Created by

Created date

Actions:

View
Download
Share

---

# 36. ADMINISTRATION

Administration should be visually separated from investigation workflows.

Possible sections:

Users
Roles
Permissions
System Health
Audit Logs
Configuration

Only display modules allowed by RBAC.

---

# 37. TABLE DESIGN

Tables should support:

- sorting
- filtering
- pagination
- column visibility
- row actions
- keyboard navigation

Avoid excessive borders.

Use subtle row separation.

Important status should have:

icon + text

not color alone.

---

# 38. FORMS

Forms must provide:

Label
Input
Helper text
Validation
Error
Success

Example:

Badge Number

[________________]

3–20 alphanumeric characters

Error:

Badge number must contain only letters and numbers.

Do not wait until form submission to reveal obvious validation errors.

---

# 39. BUTTON HIERARCHY

Primary:

Main action.

Secondary:

Alternative action.

Tertiary:

Low-emphasis action.

Destructive:

Delete / irreversible action.

Avoid having multiple primary buttons competing in the same area.

---

# 40. MODALS

Use modals only for:

- confirmation
- focused short workflows
- important decisions

Do not place large complex workflows inside modal dialogs.

Use drawers or dedicated pages for complex investigation workflows.

---

# 41. DRAWERS

Drawers are preferred for contextual information.

Examples:

Entity details
Evidence details
Alert details
Graph node details

This allows investigators to inspect information without losing their current context.

---

# 42. LOADING STATES

Never show blank screens.

Use:

Skeleton loaders
Progress indicators
Subtle shimmer where appropriate

Skeletons should resemble the final content structure.

---

# 43. EMPTY STATES

Empty states should explain:

What is empty

Why it is empty

What the user can do

Example:

No investigations found.

Try changing your filters or create a new investigation.

Do not use fake records to make pages look populated.

---

# 44. ERROR STATES

Errors must be useful.

Example:

Unable to load investigation

We couldn't retrieve this investigation right now.

[Retry]

Technical details should not be exposed to normal users.

---

# 45. PLAYFUL ERROR STATES

The platform is serious, therefore playful behavior must remain subtle.

Allowed:

Small contextual illustrations
Friendly microcopy
Subtle animation

Avoid:

Cartoonish errors
Memes
Excessive jokes

The system should maintain institutional credibility.

---

# 46. MICRO-INTERACTIONS

Use micro-interactions for:

- button feedback
- navigation
- opening drawers
- filtering
- saving
- copying
- expanding sections
- graph focus
- status changes

Animations should communicate state.

They must not exist only for decoration.

---

# 47. MOTION SYSTEM

Motion should feel:

Fast
Controlled
Predictable

Recommended durations:

Micro:
100–150ms

Standard:
150–250ms

Complex:
250–350ms

Avoid excessive animation.

Support:

prefers-reduced-motion

When reduced motion is enabled:

Disable non-essential transitions.

---

# 48. PAGE TRANSITIONS

Avoid dramatic page transitions.

Use subtle:

fade
slide
scale

Only when useful.

The user should feel that navigation is instant.

---

# 49. RESPONSIVENESS

Desktop is the primary target because investigators commonly work on large displays.

Support:

Large desktop
Desktop
Tablet
Mobile

Do not simply shrink desktop layouts.

Adapt:

Sidebar
Tables
Graph controls
Map controls
Cards
Navigation

---

# 50. LARGE SCREEN DESIGN

For large screens:

Use multi-column layouts.

Example:

Main content: 70%

Context panel: 30%

Do not allow content to stretch infinitely.

Use maximum readable widths.

---

# 51. PERFORMANCE

Performance is a design requirement.

Target:

Fast initial load
Fast interaction
Minimal layout shift

Optimize:

- code splitting
- lazy loading
- route-level loading
- image optimization
- virtualized large tables
- graph rendering
- map rendering
- memoization
- API caching where appropriate

Avoid loading:

- graph libraries
- map libraries
- heavy charts

until required.

Use dynamic imports where appropriate.

---

# 52. PERFORMANCE BUDGET

The frontend should aim for:

LCP:
~2.5 seconds or better

INP:
~200ms or better

CLS:
~0.1 or better

These are targets, not excuses to sacrifice usability.

Measure performance rather than assuming it.

---

# 53. DATA VISUALIZATION

Charts must answer questions.

Avoid:

Decorative charts
3D charts
Excessive gradients
Unnecessary animation

Prefer:

Line charts
Bar charts
Area charts
Heatmaps
Network graphs
Timelines

Every visualization needs:

Title
Units
Legend where needed
Accessible interpretation

---

# 54. GRAPH PERFORMANCE

Knowledge graphs can become expensive.

Use:

- progressive rendering
- node limits
- filtering
- clustering
- viewport rendering
- lazy expansion

Do not render thousands of nodes immediately.

---

# 55. MAP PERFORMANCE

Use:

- clustering
- viewport-based loading
- layer toggling
- progressive data loading

Avoid loading the entire geographic dataset at once.

---

# 56. NOTIFICATIONS

Notifications should be categorized:

Critical
Warning
Information
Success

Critical notifications must remain visually distinguishable.

Avoid notification spam.

---

# 57. TOOLTIPS

Use tooltips for:

- unfamiliar icons
- technical metrics
- abbreviated labels

Do not use tooltips for essential information.

Essential information must be visible.

---

# 58. KEYBOARD SHORTCUTS

Eventually support:

CMD/CTRL + K
Global search

ESC
Close drawer/modal

/
Focus search

Arrow keys
Navigate lists where appropriate

Shortcuts should never be the only way to perform an action.

---

# 59. ROLE-BASED UI

Frontend navigation must respect backend RBAC.

Example:

ADMIN:

Administration
System Health
Audit Logs

EXECUTIVE:

Executive Intelligence
Reports
Network Intelligence

OFFICER:

Investigations
Entities
Evidence
Operational Intelligence

IMPORTANT:

Frontend hiding is NOT security.

Backend authorization remains authoritative.

---

# 60. SECURITY UX

Never expose:

JWT tokens
API keys
database credentials
internal stack traces
Neo4j credentials
internal server errors

Error messages should be user-friendly.

---

# 61. TRUST DESIGN

Trust is a major differentiator for this platform.

The UI should visually distinguish:

VERIFIED

SOURCE DATA

AI GENERATED

ANALYTICAL INFERENCE

UNVERIFIED

Example:

[VERIFIED SOURCE]

Police Record

vs

[AI INFERENCE]

Potential relationship identified from available evidence.

---

# 62. AI TRUST PRINCIPLE

Never visually imply:

AI prediction = fact

Instead:

AI suggestion
↓
Supporting evidence
↓
Investigator review
↓
Confirmed intelligence

The investigator remains the decision maker.

---

# 63. NO FAKE DATA POLICY

During UI foundation:

DO NOT fabricate:

- suspects
- cases
- crime statistics
- graph relationships
- anomaly percentages
- risk scores
- locations
- intelligence findings

Allowed:

- structural placeholders
- skeleton loaders
- empty states
- "Not yet available"
- "Awaiting backend integration"

---

# 64. PLACEHOLDER DESIGN

Correct:

┌──────────────────────────────┐
│ KNOWLEDGE GRAPH              │
│                              │
│ Graph intelligence will      │
│ appear when graph services   │
│ are connected.               │
│                              │
│ [Configuration status]       │
└──────────────────────────────┘

Incorrect:

"87% suspicious network"

when no real analytics exist.

---

# 65. DESIGN SYSTEM COMPONENTS

Create reusable components for:

Layout
Sidebar
Topbar
Breadcrumb
PageHeader
Card
StatCard
Badge
StatusBadge
Button
Input
Select
Dropdown
Modal
Drawer
Tabs
Tooltip
Toast
Alert
Skeleton
EmptyState
ErrorState
DataTable
Timeline
EvidenceCard
EntityCard
GraphContainer
MapContainer
CopilotPanel
FilterBar
SearchBar
Pagination

---

# 66. DESIGN TOKENS

Centralize:

Colors
Typography
Spacing
Radius
Shadows
Motion
Breakpoints
Z-index
Component dimensions

Do not scatter design values throughout components.

---

# 67. COMPONENT STATES

Every interactive component should consider:

Default
Hover
Focus
Active
Disabled
Loading
Success
Error

For data-driven components:

Loading
Loaded
Empty
Error

---

# 68. RESPONSIVE COMPONENT STATES

Components should remain usable when:

- sidebar is collapsed
- viewport is narrow
- content is long
- data is missing
- network is slow

---

# 69. DARK MODE

Dark mode is the primary visual mode.

Do not make every surface pure black.

Use layered surfaces.

Example hierarchy:

Background
↓
Surface
↓
Elevated surface
↓
Modal / overlay

This creates depth without excessive shadows.

---

# 70. LIGHT MODE

Light mode may be supported later.

The architecture should avoid hardcoding colors that make future theme support difficult.

Use design tokens.

---

# 71. INVESTIGATION WORKFLOW

Primary workflow:

LOGIN
↓
DASHBOARD
↓
INVESTIGATION
↓
CASE OVERVIEW
↓
ENTITY
↓
NETWORK
↓
TIMELINE
↓
MAP
↓
EVIDENCE
↓
AI COPILOT
↓
REPORT

The UI should make this workflow feel continuous.

---

# 72. CONTEXT PRESERVATION

When investigators open:

Entity
Evidence
Alert
Graph node

they should not lose their current investigation context.

Prefer:

Drawer
Side panel
Nested workspace

instead of forcing unnecessary page navigation.

---

# 73. BREADCRUMBS

Example:

Investigations
/
CASE-1024
/
Network

This allows users to understand location within the platform.

---

# 74. SEARCH EXPERIENCE

Search results should be grouped.

Example:

PEOPLE
John Doe

CASES
CASE-1024

VEHICLES
KA-01-AB-1234

LOCATIONS
Bengaluru

DOCUMENTS
FIR-2026-001

---

# 75. FILTER EXPERIENCE

Filters should show active state.

Example:

Filters

[Date]
[Entity Type]
[Severity]
[Status]

Active:

Severity: Critical ×

Clear all

---

# 76. DATA TABLE UX

For large tables:

- sticky header
- pagination
- column sorting
- filters
- row hover
- keyboard navigation
- optional column visibility
- responsive overflow

Do not render thousands of DOM rows at once.

---

# 77. FORM UX

Forms should:

- preserve entered values
- validate clearly
- explain errors
- prevent accidental loss
- show loading during submission
- disable duplicate submission

---

# 78. CONFIRMATION UX

For destructive actions:

User action

↓

Confirmation

↓

Clear consequence

↓

Confirm / Cancel

Example:

Delete investigation?

This action cannot be undone.

[Cancel]
[Delete]

---

# 79. SUCCESS FEEDBACK

Use subtle feedback.

Examples:

Evidence uploaded

Entity merged

Report generated

Saved successfully

Avoid intrusive success modals for simple operations.

Use toast notifications where appropriate.

---

# 80. ERROR RECOVERY

Every recoverable error should provide:

What happened

What the user can do

Retry where appropriate

Example:

Graph data couldn't be loaded.

[Retry]

---

# 81. OFFLINE / NETWORK STATES

Eventually support:

Connecting
Connected
Reconnecting
Offline

Important for real-world operational reliability.

---

# 82. SYSTEM STATUS

The application should eventually expose:

API status
Database status
Graph status
AI service status
Ingestion status

Do not expose sensitive infrastructure information to unauthorized users.

---

# 83. AI LOADING EXPERIENCE

AI processing should not look frozen.

Show:

Analyzing evidence...

Retrieving supporting records...

Building response...

But these messages must reflect actual backend states.

Do not fake progress.

---

# 84. COPILOT STREAMING

When backend supports streaming:

Use progressive response rendering.

Display:

Thinking / processing state

↓

Response

↓

Sources

↓

Suggested actions

Avoid artificial delays.

---

# 85. MOTION ACCESSIBILITY

Respect:

prefers-reduced-motion

Users who disable motion should still receive equivalent information.

---

# 86. TOUCH TARGETS

Interactive controls must be sufficiently large for touch.

Avoid tiny icon-only buttons.

Icon buttons should have:

Tooltip
Accessible label
Visible focus

---

# 87. ICONOGRAPHY

Use one consistent icon library.

Do not mix multiple visual icon styles.

Icons should support text, not replace important text.

---

# 88. EMPTY STATE LANGUAGE

Avoid:

"Oops!"

Prefer:

"No investigations yet"

"Upload a data source to begin"

"Nothing matched your filters"

Language should remain professional.

---

# 89. ERROR LANGUAGE

Avoid technical messages:

"AxiosError 500"

"ECONNREFUSED"

"Neo4j driver failed"

Use:

"Unable to load intelligence data."

Technical details remain in server logs.

---

# 90. SIH PRESENTATION PRINCIPLE

The UI should make the complete architecture visually understandable during demonstration.

A judge should be able to understand:

DATA
↓
INGESTION
↓
NLP
↓
ENTITY RESOLUTION
↓
GRAPH
↓
INTELLIGENCE
↓
EVIDENCE
↓
AI COPILOT

without requiring a technical explanation for every screen.

---

# 91. DEMO EXPERIENCE

The eventual SIH demonstration should follow a coherent story:

1. Login

2. Dashboard

3. Open investigation

4. Inspect entities

5. Explore network

6. Inspect timeline

7. View map

8. Inspect evidence

9. Ask Copilot

10. Show supporting evidence

11. Show intelligence insight

12. Generate report

The interface should support this flow naturally.

---

# 92. SIH DIFFERENTIATION

The platform should visually communicate:

### 1. Evidence-grounded AI

AI outputs are connected to evidence.

### 2. Entity Resolution

Duplicate identities can be investigated.

### 3. Knowledge Graph

Relationships become explorable.

### 4. Intelligence Analytics

Patterns and anomalies become discoverable.

### 5. Provenance

Users can understand where information came from.

### 6. Investigator-in-the-loop

AI assists rather than replacing the investigator.

---

# 93. IMPLEMENTATION RULE

UI development must not break existing functionality.

Before modifying an existing page:

1. Inspect current implementation.
2. Understand existing API dependencies.
3. Preserve working functionality.
4. Refactor incrementally.
5. Run type checking.
6. Verify routes.
7. Verify authentication.
8. Verify RBAC behavior.

---

# 94. NO BIG-BANG FRONTEND REWRITE

Do NOT delete and rebuild the entire frontend.

Use incremental modernization.

Existing working functionality must remain available.

---

# 95. ROUTING FOUNDATION

The following routes should exist in the design architecture:

/dashboard

/investigations

/investigations/[id]

/entities

/resolution

/knowledge-graph

/intelligence

/intelligence/anomalies

/intelligence/influencers

/intelligence/potential-links

/map

/timeline

/evidence

/ingestion

/copilot

/reports

/admin

---

# 96. FEATURE IMPLEMENTATION BOUNDARY

During UI foundation:

IMPLEMENT:

- navigation
- layouts
- components
- design system
- responsive behavior
- states
- workspace shells
- visualization containers
- loading/error/empty states
- role-aware navigation

DO NOT IMPLEMENT:

- fake analytics
- fake graph relationships
- fake anomaly results
- fake map data
- fake AI answers
- fake evidence
- fake intelligence scores

---

# 97. FUTURE INTEGRATION

Backend feature → UI integration.

Example:

Phase X:
Graph backend becomes functional

↓

GraphContainer receives real data

↓

Graph UI becomes functional

Same principle applies to:

Map
Timeline
Anomaly engine
Entity resolution
Copilot
Evidence
Reports

---

# 98. DESIGN QUALITY CHECKLIST

Before considering UI work complete:

## Visual

- [ ] Clear hierarchy
- [ ] Consistent spacing
- [ ] Consistent typography
- [ ] Consistent colors
- [ ] Consistent components
- [ ] No unnecessary decoration

## UX

- [ ] Navigation is predictable
- [ ] Context is preserved
- [ ] Important actions are obvious
- [ ] Forms provide feedback
- [ ] Errors are recoverable
- [ ] Empty states are useful

## Performance

- [ ] Routes load quickly
- [ ] Heavy libraries are lazy-loaded
- [ ] Large lists are virtualized/paginated
- [ ] No unnecessary network requests
- [ ] No layout jumps

## Accessibility

- [ ] Keyboard navigation
- [ ] Visible focus
- [ ] Accessible labels
- [ ] Sufficient contrast
- [ ] Reduced motion support
- [ ] Semantic structure

## Intelligence Trust

- [ ] AI output distinguished from source data
- [ ] Evidence visible
- [ ] Provenance visible
- [ ] Uncertainty communicated
- [ ] No fabricated intelligence

---

# 99. DEFINITION OF DONE

UI/UX Foundation is complete when:

1. The application has one consistent visual language.

2. All primary SIH modules have defined navigation.

3. The investigation workspace structure exists.

4. Core reusable components exist.

5. Loading/error/empty states exist.

6. Role-based navigation exists.

7. Responsive behavior is established.

8. Accessibility principles are implemented.

9. Performance principles are implemented.

10. Graph/map/timeline/evidence/copilot containers exist.

11. No fabricated intelligence is displayed.

12. Existing ICA_AI functionality remains operational.

13. Future backend features can plug into the UI without redesigning the entire application.

---

# 100. FINAL DESIGN PRINCIPLE

The SIH26189 platform should feel like:

"An intelligence workstation built for investigators."

Not:

"A website containing many dashboards."

Every design decision should reinforce that distinction.

The interface should be:

FAST.
CLEAR.
TRUSTWORTHY.
EVIDENCE-GROUNDED.
CONSISTENT.
ACCESSIBLE.
RESPONSIVE.
INVESTIGATOR-FIRST.

The UI is not decoration around the intelligence engine.

The UI IS the investigator's interface to the intelligence engine.