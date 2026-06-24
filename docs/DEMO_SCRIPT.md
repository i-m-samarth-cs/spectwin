# SpecTwin — Demo Script

**Total runtime:** ~12 minutes  
**Audience:** Engineering managers, product leads, interviewers, conference reviewers  
**Credentials:** `pm@spectwin.dev` / `demo1234`

---

## Step 1 — Landing Page Tour (2 min)

**URL:** `http://localhost:3000`

**Click through:**
- Point out the hero headline: *"Your specs are drifting apart."*
- Show the problem statement section — read 2–3 bullet points aloud
- Point to the live drift detection preview card on the right side:
  - *"These are real findings from the demo project — notice the critical severity items"*
- Scroll to the Features section — briefly name each of the 6 feature cards
- Show the Agent Workflow section:
  - *"11 specialized agents run sequentially. Each gets structured context, returns validated JSON, and cites its evidence."*

**Say:** *"This is not a chatbot. It's a specification intelligence system — think of it as a continuous auditor for your entire project artifact stack."*

---

## Step 2 — Login as Product Manager (30 sec)

**URL:** `http://localhost:3000/login`

- Click the **Product Manager** quick-fill button
- Click **Sign In**
- You're now on the dashboard as `Alex Chen, Product Manager`

**Say:** *"We have 5 role types: PM, Engineer, QA Lead, Engineering Manager, and Admin. Each sees the same data but the dashboard is framed around their concerns."*

---

## Step 3 — Dashboard Overview (1 min)

**URL:** `/dashboard`

- Point to the 3 stat cards: **3 projects, 26 open issues, 53% avg readiness**
- *"That average readiness score — 53% — is a red flag. Let's find out why."*
- Click on **Payments Platform v3** — the worst scoring project

---

## Step 4 — Project Detail Page (1 min)

**URL:** `/dashboard/projects/[payments-id]`

- Point to the grade: **F — 32%**
- Point to the red critical issues banner:
  - *"Three critical issues must be resolved before this project can ship."*
- Scroll to the Recent Issues preview
- **Say:** *"Notice the first one: 'Fraud accuracy contradicts PRD and compliance requirements'. The model says 99.2% in the release notes. Tests show 98.8%. Compliance requires 99.0%. Three different numbers, three different sources — SpecTwin caught all of them."*

---

## Step 5 — Drift Issues Board (3 min) ← **The money shot**

**URL:** `/dashboard/projects/[id]/issues`

- Show the severity filter bar — click **Critical** to filter
- **Click to expand the fraud accuracy issue:**
  - Read the Description aloud (it's concise and damning)
  - Open the **Evidence** section:
    - *"PRD says 99.2%. Test says 98.8%. Release note claims 99.2%. Slack transcript shows someone suggested shipping it 'quietly'. All four artifacts are cited."*
  - Show the **Reasoning** field:
    - *"This is the agent explaining its logic — not just a flag, but a structured argument."*
  - Show the **Suggested Action** box:
    - *"It doesn't just find problems — it tells you what to do about them."*
- Click to expand the **Instant Settlement** contradiction:
  - *"Four artifacts contradict each other on the same business rule. PRD says Premium only. Code says all tiers. API spec says all tiers. Release note says Premium only again. This is exactly the kind of thing that causes production incidents."*

**Say:** *"Every finding is grounded in evidence. The EvidenceCriticAgent reviews all findings before they surface — if a finding can't be supported by a direct quote, it gets rejected."*

---

## Step 6 — Project Twin Graph (1.5 min)

**URL:** `/dashboard/projects/[id]/twin`

- Point to the graph:
  - *"This is the Project Twin — every entity extracted from artifacts as a node, with typed relationships as edges."*
- Point to the **red edges** (contradicts):
  - *"Red edges are contradictions. You can see the fraud accuracy requirement node connected to the test artifact and the release note with contradicts edges."*
- Click a node to show the detail panel
- Show the legend panels:
  - *"10 node types, 8 edge types. The graph gives you a machine-readable map of your project's truth."*

---

## Step 7 — Release Readiness Console (1.5 min)

**URL:** `/dashboard/projects/[id]/release`

- Point to the big grade: **F — 32/100**
- Walk through the metrics grid:
  - *"3 critical issues, 4 high issues, 1 missing test, 2 missing docs, 2 API mismatches."*
- Read the Executive Summary aloud:
  - *"This is AI-generated in 178ms based on the issues data. It's factual, cites specific problems, and tells the team exactly what to fix."*
- Show the Risk Items list:
  - Point to the `blocker: true` items: *"These are hard release blockers. The system won't let you ship past these."*

---

## Step 8 — Admin Analytics (1 min)

**URL:** `/dashboard/admin`

- Log out and log back in as `admin@spectwin.dev` / `demo1234`
- Navigate to Admin
- Show the bar charts:
  - *"Issues by category across all projects. Contradictory requirements are the most common — 5 of 12 issues."*
- Show the Drift Trend chart:
  - *"Issues are growing month-over-month. This is a signal that spec discipline is declining as velocity increases."*
- Show the Release Readiness bars:
  - *"Notification Engine is at 87% — clean. Payments is at 32% — release blocked."*
- Show the Prompt Traces table:
  - *"Every agent run is logged with latency and token count. In mock mode it's sub-5ms. In real mode with Claude it's 80–200ms per agent."*

---

## Step 9 — SpecDriftBench Evaluation (1 min)

**URL:** `/dashboard/admin` (Eval section if wired) or terminal

- Show the seed dataset file: `dataset/seed/specdriftbench_seed.json`
- Open one sample — point to the `label` and `rationale` fields
- Run the evaluation:
  ```bash
  python dataset/scripts/evaluate.py \
    --gold dataset/seed/specdriftbench_seed.json \
    --predictions my_preds.json \
    --model gpt-4o
  ```
- Show the formatted report output

**Say:** *"SpecDriftBench is a self-built benchmark for cross-artifact alignment detection. It's the first dataset we know of that combines all 7 artifact types in a single sample. We use it to measure how well the system performs and to compare against baselines like GPT-4o and keyword heuristics."*

---

## Closing Line

*"SpecTwin answers three questions that every engineering team struggles with: Did we build what we promised? Does what we shipped match what we tested? Is our release safe to make? The answer is now evidence-backed, automated, and continuous."*
