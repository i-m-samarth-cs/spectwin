# SpecTwin

> Agentic specification intelligence for software teams. Did engineering build what product asked for? Is your release safe to ship? SpecTwin answers both — continuously, with evidence.

SpecTwin ingests your project artifacts (PRDs, tickets, Slack discussions, API specs, code diffs, test cases, release notes) and runs **11 role-specialized AI agents** to detect specification drift: contradictions, ambiguities, undocumented changes, missing tests, and release risks — all before they become production incidents.

---

## Features

- **Project Twin Graph** — visual knowledge graph of features, requirements, APIs, and tests
- **Drift Issue Board** — filterable findings with evidence drawers and source citations
- **Release Readiness Console** — 0–100 score, letter grade, and executive summary
- **Acceptance Criteria Agent** — generates Given/When/Then criteria from vague descriptions
- **Test Gap Analyzer** — identifies missing coverage across code paths and requirements
- **Artifact Ingestion** — supports 7 artifact types via paste or upload
- **Admin Analytics** — issue trends, drift distribution, and prompt trace logs
- **Mock Mode** — fully deterministic demo with no API keys required

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Animation | Framer Motion |
| Charts | Recharts |
| State | Zustand |
| Backend | FastAPI, Python 3.11, Pydantic v2 |
| ORM | SQLAlchemy 2 (async) |
| Database | PostgreSQL |
| Auth | JWT (python-jose) + bcrypt |
| AI | OpenAI GPT-4o / Anthropic Claude |

---

## Quick Start

Requires [Docker](https://www.docker.com/) and Docker Compose.

```bash
git clone https://github.com/your-username/spectwin
cd spectwin

cp backend/.env.example backend/.env

docker-compose up
```

Visit `http://localhost:3000`. No API keys needed — Mock Mode is on by default.

---

## Manual Setup

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `SECRET_KEY` | `spectwin-demo-secret-key` | JWT signing key — change in production |
| `MOCK_MODE` | `true` | `true` = no LLM keys needed |
| `OPENAI_API_KEY` | — | Required for real mode with GPT-4o |
| `ANTHROPIC_API_KEY` | — | Required for real mode with Claude |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## Demo Credentials

| Role | Email | Password |
|---|---|---|
| Product Manager | pm@spectwin.dev | demo1234 |
| Engineer | eng@spectwin.dev | demo1234 |
| QA Lead | qa@spectwin.dev | demo1234 |
| Engineering Manager | mgr@spectwin.dev | demo1234 |
| Admin | admin@spectwin.dev | demo1234 |

---

## Mock Mode vs Real Mode

**Mock Mode** (`MOCK_MODE=true`, default)
- No LLM API keys needed
- Returns deterministic responses from 3 pre-built demo projects:
  - Payments Platform v3 — F grade, 8 critical issues
  - Auth Service — D grade
  - Notifications — B+ grade
- All agents respond in < 5ms

**Real Mode** (`MOCK_MODE=false`)
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`
- Agents call the configured LLM provider with security-hardened prompts
- Artifact content is sanitized before prompt insertion to prevent prompt injection
- Evidence Critic validates all findings before they surface

---

## Agent Pipeline

| Agent | Role |
|---|---|
| RequirementParserAgent | Extract structured requirements from PRDs |
| TicketNormalizationAgent | Normalize ticket entities |
| DiscussionInsightAgent | Extract decisions from chat/meeting transcripts |
| DependencyMapperAgent | Infer dependency relationships |
| AmbiguityDetectionAgent | Flag vague or unmeasurable requirements |
| ContradictionDetectionAgent | Find cross-artifact contradictions |
| AcceptanceCriteriaAgent | Generate Given/When/Then criteria |
| DocCodeDriftAgent | Detect undocumented code behavior changes |
| TestGapAgent | Identify missing test coverage |
| ReleaseRiskAgent | Score release readiness and generate summary |
| EvidenceCriticAgent | Validate and reject unsupported findings |

---

## SpecDriftBench

A self-built cross-artifact alignment benchmark for evaluating drift detection.

- 12 seed samples (expanding to 500+)
- 10 drift label classes
- 7 artifact fields per sample
- Human-reviewed gold labels

```bash
# Generate samples
python dataset/scripts/generate_samples.py --count 100 --output samples.json

# Evaluate predictions
python dataset/scripts/evaluate.py \
  --gold dataset/seed/specdriftbench_seed.json \
  --predictions preds.json \
  --model gpt-4o
```

### Benchmark Results (Seed Split)

| System | Accuracy | Macro F1 | Contradiction F1 |
|---|---|---|---|
| Random baseline | 0.100 | 0.091 | — |
| Keyword heuristic | 0.583 | 0.521 | 0.667 |
| GPT-4o zero-shot | 0.720 | 0.698 | 0.833 |
| **SpecTwin (full pipeline)** | **0.875** | **0.842** | **1.000** |

---

## Deployment

See the [`render.yaml`](render.yaml) for one-click deployment to [Render](https://render.com) (backend + frontend + PostgreSQL).

Detailed instructions in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Documentation

| Doc | Description |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, API surface, data model |
| [docs/DATASET.md](docs/DATASET.md) | SpecDriftBench schema and methodology |
| [docs/EVALUATION.md](docs/EVALUATION.md) | Metrics, baselines, evaluation protocol |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | Step-by-step demo walkthrough |
| [docs/PAPER_ABSTRACT.md](docs/PAPER_ABSTRACT.md) | Extended abstract |

---

## License

MIT
