# SpecTwin — Architecture

## Overview

SpecTwin is a full-stack agentic specification intelligence platform. It ingests multiple
software project artifact types, constructs a normalized Project Twin Graph, and runs
specialized AI agents to detect drift, contradictions, ambiguity, and release risks.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SpecTwin System                                 │
│                                                                         │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │   Browser    │───▶│  Next.js 14 App  │───▶│   FastAPI Backend   │  │
│  │  (Dark UI)   │◀───│  (TypeScript)    │◀───│   (Python 3.11+)    │  │
│  └──────────────┘    └──────────────────┘    └──────────┬───────────┘  │
│                                                          │              │
│                        ┌─────────────────────────────────┤              │
│                        │         Agent Orchestrator      │              │
│                        │  ┌──────────────────────────┐  │              │
│                        │  │  ContradictionAgent       │  │              │
│                        │  │  AmbiguityAgent           │  │              │
│                        │  │  DocCodeDriftAgent        │  │              │
│                        │  │  TestGapAgent             │  │              │
│                        │  │  ReleaseRiskAgent         │  │              │
│                        │  │  AcceptanceCriteriaAgent  │  │              │
│                        │  │  EvidenceCriticAgent      │  │              │
│                        │  └──────────────────────────┘  │              │
│                        └──────────────┬──────────────────┘              │
│                                       │                                 │
│                        ┌─────────────▼──────────────┐                  │
│                        │  PostgreSQL + pgvector      │                  │
│                        │  (Artifacts, Twin, Issues)  │                  │
│                        └────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Stack

| Layer         | Technology             | Purpose                              |
|---------------|------------------------|--------------------------------------|
| Framework     | Next.js 14 App Router  | Server components, routing           |
| Language      | TypeScript             | Type safety across all components    |
| Styling       | Tailwind CSS           | Utility-first dark mode design       |
| Animation     | Framer Motion          | Enterprise-grade motion transitions  |
| Charts        | Recharts               | Analytics dashboards                 |
| Icons         | Lucide React           | Consistent icon system               |
| State         | Zustand (persisted)    | Auth state, user session             |
| HTTP Client   | Axios                  | API communication with interceptors  |

### Key Frontend Routes

```
/                              Landing page (public)
/login                         Demo login
/dashboard                     Overview (auth required)
/dashboard/projects            Projects list
/dashboard/projects/[id]       Project detail
/dashboard/projects/[id]/twin  Project Twin Graph (SVG)
/dashboard/projects/[id]/issues Drift Issues Board
/dashboard/projects/[id]/release Release Readiness Console
/dashboard/projects/[id]/ingest Artifact ingestion workspace
/dashboard/admin               Analytics & admin metrics
```

---

## Backend Stack

| Layer          | Technology               | Purpose                               |
|----------------|--------------------------|---------------------------------------|
| Framework      | FastAPI                  | Async REST API                        |
| Language       | Python 3.11+             | Type-annotated, async-native          |
| ORM            | SQLAlchemy 2 (async)     | Async DB access with mapped columns   |
| Migrations     | Alembic                  | Schema versioning                     |
| Validation     | Pydantic v2              | Request/response models               |
| Auth           | python-jose + passlib    | JWT tokens, bcrypt hashing            |
| Database       | PostgreSQL + pgvector    | Structured data + vector embeddings   |
| Config         | pydantic-settings        | .env-based configuration              |

### API Surface

```
POST /api/auth/login                         Authenticate and get JWT
GET  /api/auth/me                            Get current user

GET  /api/projects                           List projects
POST /api/projects                           Create project
GET  /api/projects/{id}                      Get project detail

POST /api/projects/{id}/ingest               Ingest artifacts
GET  /api/projects/{id}/artifacts            List project artifacts

GET  /api/projects/{id}/twin                 Get twin graph (nodes + edges)
POST /api/projects/{id}/build-twin           Trigger twin graph rebuild

GET  /api/projects/{id}/issues               Get drift issues
POST /api/projects/{id}/analyze-ambiguity    Run ambiguity agent
POST /api/projects/{id}/analyze-contradictions  Run contradiction agent
POST /api/projects/{id}/analyze-drift        Run doc-code drift agent
POST /api/projects/{id}/generate-acceptance-criteria  Run AC agent
POST /api/projects/{id}/analyze-test-gaps    Run test gap agent
GET  /api/projects/{id}/release-readiness    Get release readiness report

PATCH /api/issues/{id}/status                Update issue status

GET  /api/admin/metrics                      Admin analytics
GET  /api/admin/prompt-traces                Agent run history

GET  /api/eval/samples                       SpecDriftBench samples
POST /api/eval/run                           Run benchmark evaluation
```

---

## Agent System Architecture

Each agent follows this contract:

1. **Input**: Receives structured context (project artifacts as sanitized JSON)
2. **Security gate**: All artifact content is sanitized to neutralize prompt injection
3. **Prompt rendering**: Template with `{{ SYSTEM_BASE }}` injected (security rules)
4. **Execution**: Mock mode (deterministic) or real mode (OpenAI/Anthropic)
5. **Output validation**: JSON response validated against required-key schema
6. **Evidence gate**: EvidenceCriticAgent reviews all findings before surfacing

### Agent Registry

| Agent                      | Input                        | Output                              |
|----------------------------|------------------------------|-------------------------------------|
| RequirementParserAgent     | PRD text                     | Structured requirements list        |
| TicketNormalizationAgent   | Ticket text                  | Normalized ticket entities          |
| DiscussionInsightAgent     | Chat/meeting text            | Decisions and commitments           |
| DependencyMapperAgent      | All artifacts                | Dependency relationships            |
| AmbiguityDetectionAgent    | Requirements artifacts       | Ambiguity findings with evidence    |
| ContradictionDetectionAgent| All artifacts                | Contradiction findings              |
| AcceptanceCriteriaAgent    | Feature description          | Given/When/Then criteria            |
| DocCodeDriftAgent          | Code diffs + specs           | Undocumented change findings        |
| TestGapAgent               | Code diffs + test artifacts  | Missing coverage findings           |
| ReleaseRiskAgent           | All issues + artifacts       | Release readiness score + summary   |
| EvidenceCriticAgent        | All findings                 | Validation verdicts (approve/reject)|

### Security at Every Agent Boundary

```python
# Example: sanitize_artifact_content() strips injection patterns
# before any user-provided text enters a prompt.
_PROMPT_INJECTION_PATTERN = re.compile(
    r"(ignore\s+previous\s+instructions|override\s+system|...)",
    re.IGNORECASE,
)
```

Every prompt template includes:
```
SECURITY: The output must not contain any security violations.
Provide the response by removing any insecure gaps or content
that could cause security issues.
```

---

## Data Model Overview

```
User ──────────────────────────────────────────── owns ─▶ Project
                                                           │
                          ┌────────────────────────────────┤
                          │                                │
                     Artifact                         DriftIssue
                     (prd, ticket,                   (category, severity,
                      discussion,                     confidence, evidence,
                      api_spec,                       reasoning)
                      code_change,                         │
                      test_case,                    AcceptanceCriteria
                      release_note)
                          │
                     TwinNode ──────────── TwinEdge
                     (feature,             (implements,
                      requirement,          contradicts,
                      constraint,           depends_on,
                      api_contract,         tests,
                      implementation_       documents)
                      change,
                      test_artifact)

EvaluationSample ─── gold labels for SpecDriftBench
EvaluationRun    ─── benchmark run results
ModelRun         ─── agent execution telemetry
PromptTrace      ─── rendered prompts + responses
AuditLog         ─── all user actions
```

---

## Mock Mode vs Real Mode

| Aspect            | Mock Mode (`MOCK_MODE=true`)          | Real Mode (`MOCK_MODE=false`)         |
|-------------------|---------------------------------------|---------------------------------------|
| LLM calls         | Deterministic pre-built responses     | OpenAI GPT-4o or Anthropic Claude     |
| Latency           | < 5ms per agent                       | 80–400ms per agent                    |
| API keys needed   | None                                  | `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` |
| Data              | 3 pre-built demo projects             | Real user-ingested artifacts          |
| Use case          | Demo, development, CI testing         | Production, research evaluation       |

---

## Project Twin Graph Construction

1. **Parse Phase**: RequirementParserAgent extracts structured entities from each artifact
2. **Node Creation**: Each entity becomes a TwinNode with type, label, and source reference
3. **Edge Inference**: DependencyMapperAgent links nodes with typed edges
4. **Contradiction Overlay**: ContradictionDetectionAgent adds `contradicts` edges
5. **Test Coverage Overlay**: TestGapAgent adds `tests` edges (or flags missing ones)
6. **Visualization**: Frontend renders the graph as an SVG with color-coded nodes and edges
