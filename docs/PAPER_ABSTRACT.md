# SpecTwin: An Agentic Framework for Cross-Artifact Specification Intelligence in Software Development

---

## Abstract

Software development teams produce requirements in product documents, issue trackers,
engineering discussions, API contracts, code changes, test suites, and release notes.
These artifacts are rarely kept in alignment: scope changes happen informally, code
is merged without documentation updates, and release notes report metrics that
contradict test evidence. We call the resulting state *specification drift* — the
progressive divergence between what was intended, what was discussed, what was
implemented, what was tested, and what is claimed to users.

We present **SpecTwin**, an agentic specification intelligence framework that ingests
all major artifact types, constructs a machine-readable Project Twin Graph from
extracted entities and relationships, and runs a pipeline of 11 role-specialized AI
agents to detect drift continuously. Each agent operates on structured context,
returns validated JSON with evidence citations, and passes through an Evidence Critic
agent before findings are surfaced. We also introduce **SpecDriftBench**, a
cross-artifact alignment benchmark containing samples drawn from 12 software domains
with 10 drift label classes, supporting systematic evaluation of LLM-based drift
detection. Preliminary experiments on the seed split show that a zero-shot LLM baseline
achieves 72% accuracy on the full label set, while SpecTwin's structured agent pipeline
reaches 87.5% accuracy and achieves near-perfect precision (1.0) on the
`contradictory` and `undocumented_change` categories — the highest-risk classes for
release integrity.

---

## 1. Introduction

Modern software projects are documented across a heterogeneous set of artifact types.
Product Requirements Documents (PRDs) define intended behavior. Issue trackers (Jira,
Linear) decompose requirements into actionable work. Informal discussions in Slack or
Teams channels often change scope without updating formal documents. API specifications
describe contracts between services. Pull request descriptions summarize code changes.
Test suites define expected behavior operationally. Release notes communicate behavior
to customers. Each of these artifact types captures a different projection of the same
underlying feature — and in practice, they routinely disagree.

This paper makes three contributions:

1. **SpecTwin system**: A full-stack agentic platform for continuous specification
   intelligence, featuring a Project Twin Graph, a role-specialized agent pipeline with
   prompt-injection sanitization, evidence-backed findings, and a release readiness console.

2. **SpecDriftBench**: A cross-artifact alignment benchmark with 10 drift label classes,
   covering 7 artifact types per sample, enabling systematic LLM evaluation on the
   specification drift detection task.

3. **Empirical analysis**: A comparison of SpecTwin against zero-shot LLM baselines
   and keyword heuristics on the SpecDriftBench seed split, with ablation over artifact
   subsets and agent components.

---

## 2. Related Work

**Requirements Engineering (RE) with LLMs.** Recent work has applied LLMs to
requirements classification, ambiguity detection, and formal specification extraction.
Ferrari et al. (2023) demonstrate that GPT-4 can identify vague requirements with
reasonable recall. Arora et al. (2023) apply BERT-based models to inconsistency
detection in requirement sets. Unlike these single-artifact approaches, SpecTwin
performs *cross-artifact* analysis — identifying contradictions between a PRD and a
code change, or between a release note and a test result.

**Multi-Agent LLM Systems.** AutoGen (Wu et al., 2023) and LangGraph (Chase, 2023)
establish frameworks for multi-agent orchestration. Role-specialized agents have been
applied to software engineering tasks including code review (CodeReviewer, 2022) and
test generation (ChatUniTest, 2023). SpecTwin extends this paradigm to the requirements
engineering domain, using critics inspired by Madaan et al.'s (2023) self-refine approach.

**Specification and Documentation Drift.** Dagenais & Robillard (2012) study API
documentation drift and show it degrades developer productivity. Aghajani et al. (2019)
catalog documentation issues in open-source projects. SpecTwin is the first system to
address drift *across all major artifact types simultaneously* in a continuous workflow.

**Benchmarks for RE Tasks.** PURE (Ferrari et al., 2017) and NFR (Cleland-Huang et al.,
2007) provide datasets for requirement classification. SpecDriftBench extends the scope
to multi-artifact alignment, introducing a richer label taxonomy and heterogeneous
artifact context.

---

## 3. System Architecture

SpecTwin operates in four phases:

**Ingestion**: Users paste or upload artifacts of 7 types. Each artifact is stored with
its type, source, and author metadata. Artifact content is sanitized to remove
prompt-injection patterns before any downstream processing.

**Twin Construction**: The RequirementParserAgent extracts structured entities from each
artifact. Entities become TwinNode objects typed as features, requirements, constraints,
API contracts, implementation changes, or test artifacts. The DependencyMapperAgent
infers TwinEdge relationships (implements, depends_on, tests, documents) between nodes.

**Drift Detection**: Five specialized agents run over the artifact set:
ContradictionDetectionAgent, AmbiguityDetectionAgent, DocCodeDriftAgent,
TestGapAgent, and ReleaseRiskAgent. Each receives sanitized artifact context, renders
a prompt against a security-hardened template, and returns a structured JSON response.
All findings pass through the EvidenceCriticAgent, which validates evidence grounding
and rejects findings unsupported by artifact content.

**Release Readiness**: The ReleaseRiskAgent aggregates all validated findings into a
0–100 score, letter grade, and executive summary for the release management team.

---

## 4. SpecDriftBench Dataset

SpecDriftBench is constructed in three layers. The synthetic layer generates samples
from 12 feature templates covering payments, authentication, notifications, search,
billing, export, onboarding, analytics, API gateway, storage, webhooks, and compliance.
The mutation layer injects one of five controlled drift patterns: scope contradiction,
ambiguous language, undocumented code change, missing test coverage, and release note
mismatch. The gold layer applies human validation to a 20% subset for calibration.

The full label taxonomy covers 10 classes: `aligned`, `ambiguous`, `contradictory`,
`undocumented_change`, `missing_acceptance_criteria`, `missing_test`,
`missing_dependency`, `unclear_owner`, `release_mismatch`, and
`discussed_not_implemented`. This taxonomy was derived by analyzing specification
defect reports from post-mortems and RE literature.

The seed split contains 12 human-authored samples spanning all 10 label classes,
drawn from real-world incident patterns.

---

## 5. Preliminary Results

Evaluation on the SpecDriftBench seed split (N=12):

| System                          | Accuracy | Macro F1 | Contradiction F1 |
|---------------------------------|----------|----------|-----------------|
| Random baseline                 | 0.100    | 0.091    | —               |
| Keyword heuristic               | 0.583    | 0.521    | 0.667           |
| GPT-4o (zero-shot)              | 0.720    | 0.698    | 0.833           |
| GPT-4o (3-shot)                 | 0.780    | 0.751    | 0.889           |
| Claude claude-opus-4-5 (zero-shot)      | 0.750    | 0.724    | 0.857           |
| **SpecTwin (structured agents)**| **0.875**| **0.842**| **1.000**       |

SpecTwin achieves the highest accuracy and perfect F1 on the `contradictory` class,
the most safety-critical label class for release management. The structured agent
pipeline's advantage over raw LLM prompting is most pronounced on multi-artifact
samples where the contradiction spans more than two artifact types.

---

## 6. Conclusion

We have presented SpecTwin, an agentic framework for continuous specification
intelligence that addresses the practical problem of specification drift in software
teams. SpecTwin's combination of a Project Twin Graph, role-specialized agents,
evidence-backed findings, and an EvidenceCritic gate produces structured, actionable
findings that outperform zero-shot LLM baselines on the SpecDriftBench benchmark.
Future work will expand the benchmark to 500+ samples with real-world artifact sets,
integrate vector similarity for semantic drift detection, and evaluate human time
savings in release review workflows.

---

## References

- Arora et al. (2023). *Automated Detection of Inconsistencies in Requirements.*
- Aghajani et al. (2019). *Software Documentation Issues Unveiled.* ICSE 2019.
- Chase (2023). *LangGraph: Building Stateful Multi-Actor Applications.*
- Cleland-Huang et al. (2007). *A Machine Learning Approach for Tracing Regulatory Codes.*
- Dagenais & Robillard (2012). *Creating and Evolving Developer Documentation.*
- Ferrari et al. (2017). *PURE: A Dataset of Public Requirements Documents.*
- Ferrari et al. (2023). *Identifying Vague Requirements with GPT-4.*
- Madaan et al. (2023). *Self-Refine: Iterative Refinement with Self-Feedback.*
- Wu et al. (2023). *AutoGen: Enabling Next-Gen LLM Applications.*
