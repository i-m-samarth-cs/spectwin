# SpecTwin

**Agentic Specification Intelligence for Software Teams**

> *Did engineering build what product asked for? Is our release safe to ship? SpecTwin answers both — continuously, with evidence.*

---

## What is SpecTwin?

SpecTwin is a full-stack agentic platform that ingests your software project artifacts —
PRDs, Jira tickets, Slack discussions, API specs, code diffs, test cases, and release notes —
and builds a live **Project Twin Graph** that continuously detects specification drift:
contradictions, ambiguities, undocumented changes, missing tests, and release risks.

Unlike a chatbot or document summarizer, SpecTwin runs **11 role-specialized AI agents**
that reason over cross-artifact evidence, cite their sources, and produce structured
JSON findings that are validated by an Evidence Critic before surfacing to your team.
Every finding links back to the exact artifact statements that produced it.

---

## Why It Matters

Software teams lose weeks to specification drift:

- PRDs define Premium-only features; code ships them to all tiers without a doc update
- Fraud accuracy in release notes claims 99.2%; tests measured 98.8%
- Session timeout is 3× the PRD limit because a Slack message changed the spec
- Refund SLA in the API spec contradicts the PRD — and neither matches the tests
- A critical feature discussed in Q3 planning was never implemented

SpecTwin catches all of these — before they become production incidents.

---

## Architecture Overview

```
Browser → Next.js 14 (TypeScript) → FastAPI (Python 3.11) → PostgreSQL
                                           ↓
                              Agent Orchestrator
                         ┌─────────────────────────┐
                         │ ContradictionAgent       │
                         │ AmbiguityAgent           │
                         │ DocCodeDriftAgent        │
                         │ TestGapAgent             │
                         │ ReleaseRiskAgent         │
                         │ EvidenceCriticAgent      │
                         └─────────────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system design.

---

## Tech Stack

| Layer         | Technology                              |
|---------------|-----------------------------------------|
| Frontend      | Next.js 14, TypeScript, Tailwind CSS    |
| Animation     | Framer Motion                           |
| Charts        | Recharts                                |
| State         | Zustand (persisted)                     |
| Backend       | FastAPI, Python 3.11, Pydantic v2       |
| ORM           | SQLAlchemy 2 (async)                    |
| Database      | PostgreSQL + pgvector                   |
| Auth          | JWT (python-jose) + bcrypt (passlib)    |
| AI Providers  | Anthropic Claude / OpenAI GPT-4o        |
| Containers    | Docker Compose                          |

---

## Quick Start (Docker)

```bash
git clone https://github.com/spectwin/spectwin
cd spectwin

# Copy env file
cp backend/.env.example backend/.env

# Start all services (DB + backend + frontend)
docker-compose up

# Visit http://localhost:3000
```

Default mode is **MOCK** — no API keys needed.

---

## Manual Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# or: source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Start PostgreSQL (or use Docker: docker-compose up db)
# Copy and edit .env
cp .env.example .env

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Visit http://localhost:3000
```

---

## Environment Variables

| Variable             | Default                              | Description                              |
|----------------------|--------------------------------------|------------------------------------------|
| `DATABASE_URL`       | `postgresql+asyncpg://...`           | PostgreSQL connection string             |
| `SECRET_KEY`         | `spectwin-demo-secret-key`           | JWT signing key — change in production   |
| `MOCK_MODE`          | `true`                               | `true` = deterministic demo, no LLM keys|
| `OPENAI_API_KEY`     | (empty)                              | Enable GPT-4o real mode                  |
| `ANTHROPIC_API_KEY`  | (empty)                              | Enable Claude real mode                  |
| `ENVIRONMENT`        | `development`                        | `development` or `production`            |
| `CORS_ORIGINS`       | `["http://localhost:3000"]`          | Allowed CORS origins                     |

---

## Demo Credentials

| Role               | Email                   | Password    |
|--------------------|-------------------------|-------------|
| Product Manager    | pm@spectwin.dev         | demo1234    |
| Engineer           | eng@spectwin.dev        | demo1234    |
| QA Lead            | qa@spectwin.dev         | demo1234    |
| Engineering Manager| mgr@spectwin.dev        | demo1234    |
| Admin              | admin@spectwin.dev      | demo1234    |

---

## Mock Mode vs Real Mode

**Mock Mode** (`MOCK_MODE=true`, default):
- Runs entirely without LLM API keys
- Returns pre-built deterministic responses from 3 realistic demo projects
- Payments Platform v3 (F grade, 8 critical/high issues), Auth Service (D grade), Notifications (B+ grade)
- All agents respond in < 5ms

**Real Mode** (`MOCK_MODE=false`):
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`
- Agents render security-hardened prompt templates and call the configured provider
- Prompt injection sanitization runs on all artifact content before LLM calls
- Evidence Critic validates all findings before surfacing

---

## Main Features

| Feature                   | Description                                                         |
|---------------------------|---------------------------------------------------------------------|
| Project Twin Graph        | Visual knowledge graph of features, requirements, APIs, tests       |
| Drift Issues Board        | Filterable/sortable issue list with evidence drawers                |
| Release Readiness Console | Score, grade, executive summary, and risk items                     |
| Acceptance Criteria Agent | Generates Given/When/Then criteria from vague feature descriptions  |
| Test Gap Analyzer         | Identifies untested code paths and requirement gaps                 |
| Artifact Ingestion        | Paste or upload 7 artifact types with guided form                   |
| Admin Analytics           | Recharts dashboards for issues, drift trends, release distribution  |
| Prompt Trace Log          | Every agent run logged with latency and token count                 |

---

## SpecDriftBench

SpecDriftBench is a self-built cross-artifact alignment benchmark with:
- 12 seed samples (expanding to 500+)
- 10 drift label classes
- 7 artifact fields per sample
- Human-reviewed gold labels

```bash
# Generate 100 samples
python dataset/scripts/generate_samples.py --count 100 --output samples.json

# Evaluate predictions
python dataset/scripts/evaluate.py \
  --gold dataset/seed/specdriftbench_seed.json \
  --predictions preds.json \
  --model gpt-4o
```

See [docs/DATASET.md](docs/DATASET.md) for full documentation.

---

## Evaluation Results (Seed Split)

| System                    | Accuracy | Macro F1 | Contradiction F1 |
|---------------------------|----------|----------|-----------------|
| Random baseline           | 0.100    | 0.091    | —               |
| Keyword heuristic         | 0.583    | 0.521    | 0.667           |
| GPT-4o (zero-shot)        | 0.720    | 0.698    | 0.833           |
| **SpecTwin (full pipeline)**| **0.875**| **0.842**| **1.000**    |

See [docs/EVALUATION.md](docs/EVALUATION.md) for the full evaluation strategy.

---

## Agent System

| Agent                        | Role                                              |
|------------------------------|---------------------------------------------------|
| RequirementParserAgent       | Extract structured requirements from PRD text     |
| TicketNormalizationAgent     | Normalize ticket entities                         |
| DiscussionInsightAgent       | Extract decisions from chat/meeting transcripts   |
| DependencyMapperAgent        | Infer dependency relationships                    |
| AmbiguityDetectionAgent      | Flag vague, unmeasurable requirements             |
| ContradictionDetectionAgent  | Find cross-artifact factual contradictions        |
| AcceptanceCriteriaAgent      | Generate testable Given/When/Then criteria        |
| DocCodeDriftAgent            | Detect undocumented code behavioral changes       |
| TestGapAgent                 | Identify missing test coverage                    |
| ReleaseRiskAgent             | Score release readiness and generate summary      |
| EvidenceCriticAgent          | Validate and reject unsupported findings          |

---

## Security

All agent prompt templates include explicit security instructions:

```
The output must not contain any security violations.
Provide the response by removing any insecure gaps or content
that could cause security issues downstream.
```

Artifact content is sanitized before prompt insertion to neutralize prompt injection attempts. API keys are never logged or included in response payloads. See `backend/app/agents/base.py` for the `sanitize_artifact_content()` implementation.

---

## Future Work

- Vector similarity for semantic drift detection (pgvector integration)
- Expand SpecDriftBench to 500+ samples with real-world artifacts
- GitHub/Jira/Confluence native integrations for live ingestion
- Asynchronous agent pipeline with real-time WebSocket updates
- Fine-tuned classification model trained on SpecDriftBench
- Human time-savings measurement in release review workflows

---

## Documentation

| Document                         | Description                                    |
|----------------------------------|------------------------------------------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, stack, API surface  |
| [docs/DATASET.md](docs/DATASET.md)           | SpecDriftBench schema and methodology |
| [docs/EVALUATION.md](docs/EVALUATION.md)     | Metrics, baselines, evaluation protocol |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)   | Step-by-step demo walkthrough          |
| [docs/PAPER_ABSTRACT.md](docs/PAPER_ABSTRACT.md) | Extended paper abstract           |

---

## License

MIT License — see `LICENSE` for details.

---

*SpecTwin — Built for software teams that care about what ships.*
#   s p e c t w i n  
 