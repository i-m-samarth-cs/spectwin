# SpecDriftBench — Dataset Documentation

## Overview

**SpecDriftBench** is a cross-artifact alignment benchmark for evaluating LLM-based
specification drift detection. Each sample contains a set of project artifacts representing
the same software feature from multiple viewpoints — PRD, ticket, discussion, API spec,
code change, test cases, and release note — along with a gold label describing the
alignment relationship between them.

The benchmark is designed to evaluate how well a system can detect when software
project artifacts disagree with each other, which is the core problem SpecTwin solves.

---

## Schema Definition

| Field              | Type   | Required | Description                                      |
|--------------------|--------|----------|--------------------------------------------------|
| `id`               | string | Yes      | Unique sample identifier (e.g., `sdb-001`)       |
| `project_id`       | string | Yes      | Logical project group (e.g., `proj-payments`)    |
| `feature_name`     | string | Yes      | Name of the feature being analyzed               |
| `prd_text`         | string | Yes      | PRD or requirements document excerpt             |
| `ticket_text`      | string | Yes      | Issue tracker ticket text (Jira/Linear style)    |
| `discussion_snippet` | string | Yes   | Slack/Teams/meeting excerpt about the feature    |
| `api_spec_excerpt` | string | No       | OpenAPI or prose API specification excerpt       |
| `code_diff_summary`| string | No       | Summary of code changes (PR description style)   |
| `test_case_text`   | string | No       | Test case descriptions and statuses              |
| `release_note`     | string | No       | Release notes entry for the feature              |
| `label`            | string | Yes      | Gold alignment label (see taxonomy below)        |
| `rationale`        | string | Yes      | Human-written explanation of the label           |

---

## Label Taxonomy

| Label                        | Definition                                                                                   |
|------------------------------|----------------------------------------------------------------------------------------------|
| `aligned`                    | All artifacts are consistent — feature is correctly implemented and documented               |
| `ambiguous`                  | PRD or ticket uses vague language without measurable acceptance criteria                     |
| `contradictory`              | Two or more artifacts make mutually exclusive factual claims about the same behavior         |
| `undocumented_change`        | Code introduces a behavioral change not reflected in PRD, API spec, or documentation        |
| `missing_acceptance_criteria`| Feature is partially specified — edge cases or success criteria are absent                  |
| `missing_test`               | Implemented behavior has no corresponding test coverage                                      |
| `missing_dependency`         | Feature depends on another feature or system that is not documented or implemented          |
| `unclear_owner`              | No clear owner assigned; multiple teams disclaim responsibility                             |
| `release_mismatch`           | Release notes make claims (metrics, features) that are contradicted by test evidence         |
| `discussed_not_implemented`  | Feature was discussed/committed to in planning but never implemented                        |

---

## Dataset Construction Methodology

SpecDriftBench is built in three layers:

### Layer 1: Synthetic Generation
Templates covering 12+ software domains (payments, auth, search, notifications, billing,
export, onboarding, analytics, API gateway, storage, webhooks, compliance) are combined
with mutation functions to produce controlled drift patterns. See `dataset/scripts/generate_samples.py`.

### Layer 2: Mutation Injection
Five mutation functions systematically inject specific drift patterns into aligned base samples:
- `inject_contradiction()` — scope expansion without PRD update
- `inject_ambiguity()` — replace precise language with vague alternatives
- `inject_undocumented_change()` — add silent behavioral change to code diff
- `inject_missing_test()` — add new code path without test coverage
- `inject_release_mismatch()` — insert false performance claims in release notes

### Layer 3: Human-Reviewed Gold
A subset of samples (target: 20% of dataset) is manually validated by domain experts.
The `human_reviewed: true` field marks these samples for use in calibration and reporting.

---

## Generating More Samples

```bash
# Generate 100 balanced samples
python dataset/scripts/generate_samples.py --count 100 --output my_samples.json

# Generate only contradiction samples (for targeted evaluation)
python dataset/scripts/generate_samples.py --count 50 --label contradictory --output contradictions.json

# Reproduce the original seed set
python dataset/scripts/generate_samples.py --count 50 --seed 42 --output reproduced.json
```

---

## Running Evaluation

Predictions file must contain the same `id` fields as the gold file, plus a `predicted_label` field:

```json
[
  { "id": "sdb-001", "predicted_label": "contradictory" },
  { "id": "sdb-002", "predicted_label": "release_mismatch" }
]
```

```bash
python dataset/scripts/evaluate.py \
  --gold dataset/seed/specdriftbench_seed.json \
  --predictions my_preds.json \
  --output results.json \
  --model gpt-4o
```

---

## Sample Statistics (Seed Set)

| Label                        | Count |
|------------------------------|-------|
| aligned                      | 2     |
| contradictory                | 2     |
| undocumented_change          | 2     |
| ambiguous                    | 1     |
| missing_test                 | 1     |
| release_mismatch             | 1     |
| missing_acceptance_criteria  | 1     |
| discussed_not_implemented    | 1     |
| unclear_owner                | 1     |
| **Total**                    | **12**|

Target full dataset: 500+ samples with balanced label distribution.

---

## Known Limitations

1. **Synthetic artifacts**: Templates produce structurally realistic but not organically generated text. Real-world artifacts have greater linguistic variety.
2. **Domain coverage**: Current templates cover 12 domains. Enterprise-specific domains (healthcare, finance, legal) are underrepresented.
3. **Label granularity**: Some samples exhibit multiple drift patterns simultaneously (e.g., `contradictory` + `missing_test`). Current schema supports only a single gold label.
4. **Discussion realism**: Synthetic discussion snippets may not fully capture the register and ambiguity of real Slack/Teams conversations.

---

## Citation

If you use SpecDriftBench in your work:

```
@dataset{spectwin2024,
  title     = {SpecDriftBench: A Cross-Artifact Alignment Benchmark for Specification Drift Detection},
  author    = {SpecTwin Team},
  year      = {2024},
  note      = {https://github.com/spectwin/spectwin},
}
```
