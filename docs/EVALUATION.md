# SpecTwin — Evaluation Strategy

## Metrics

### Primary Classification Metrics (SpecDriftBench)

| Metric                    | Definition                                                  | Target    |
|---------------------------|-------------------------------------------------------------|-----------|
| Accuracy                  | % samples with correct label prediction                     | ≥ 80%     |
| Macro F1                  | Unweighted average F1 across all 10 label classes           | ≥ 0.75    |
| Contradiction Precision   | True positives / (TP + FP) for `contradictory` label        | ≥ 0.90    |
| Contradiction Recall      | True positives / (TP + FN) for `contradictory` label        | ≥ 0.85    |
| Ambiguity Accuracy        | Accuracy on `ambiguous` subset only                         | ≥ 0.75    |
| Release Mismatch F1       | F1 for `release_mismatch` label (high-stakes)               | ≥ 0.85    |
| False Positive Rate       | FP / (FP + TN) — how often clean artifacts are flagged      | ≤ 10%     |

### Secondary Quality Metrics

| Metric                           | Method                                               |
|----------------------------------|------------------------------------------------------|
| Evidence grounding coverage      | % findings with at least one verbatim artifact quote |
| Acceptance criteria quality       | Expert rating (1–5) on Given/When/Then specificity   |
| Doc-code alignment score         | % of undocumented changes correctly identified       |
| Inter-annotator agreement (IAA)  | Cohen's κ on human-reviewed gold samples             |
| Latency per agent run            | p50/p99 wall-clock time for mock and real modes      |

---

## SpecDriftBench Evaluation Protocol

### Step 1: Generate predictions
Run your model against the benchmark samples. Each sample provides 5–7 artifact fields
as context. The model must output a single `predicted_label` from the 10-label taxonomy.

### Step 2: Run evaluation script
```bash
python dataset/scripts/evaluate.py \
  --gold dataset/seed/specdriftbench_seed.json \
  --predictions preds.json \
  --model my-model-name \
  --output results.json
```

### Step 3: Review results
The script outputs:
- Overall accuracy and macro F1
- Per-class precision, recall, F1, support
- Confusion matrix
- JSON results file for downstream analysis

### Step 4: Ablation analysis
Re-run with subsets of artifact fields to measure the contribution of each:
```bash
# Omit code_diff_summary — measure degradation
# Omit discussion_snippet — measure impact of informal context
# PRD + ticket only — simulate minimal artifact scenario
```

---

## Baseline Comparisons

| Baseline                        | Description                                               |
|---------------------------------|-----------------------------------------------------------|
| Random                          | Uniform random label selection — expected ~10% accuracy   |
| Majority class                  | Always predict most common label in training set          |
| Keyword heuristic               | Flag if "not implemented", "verbal approval", "TBD" found |
| GPT-4o (zero-shot)              | GPT-4o with system prompt only, no few-shot examples      |
| GPT-4o (few-shot, 3 examples)   | GPT-4o with 3 SpecDriftBench examples in context          |
| Claude claude-opus-4-5 (zero-shot)      | Anthropic Claude claude-opus-4-5 with system prompt only      |
| SpecTwin (mock)                 | Deterministic rule-based responses from mock agent        |
| SpecTwin (real)                 | Full agent pipeline with LLM calls                        |

---

## Human Evaluation Design

### Task
Annotators are given the same artifact set as the model and asked to:
1. Select a label from the 10-class taxonomy
2. Highlight the evidence that supports their label
3. Rate their confidence (Low / Medium / High)

### Guidelines
- Label based **only** on the provided artifact text (no external knowledge)
- If multiple labels apply, choose the **primary** drift type
- Mark ambiguous samples with a flag for adjudication

### Inter-Annotator Agreement
- Target: Cohen's κ ≥ 0.70 (substantial agreement)
- Disagreements resolved by majority vote among 3 annotators
- Edge cases escalated to a domain expert for final label

---

## False Positive Analysis

A false positive occurs when SpecTwin flags a drift issue on an artifact set that is
actually fully aligned (`aligned` label). To minimize false positives:

1. **EvidenceCriticAgent** reviews all findings and rejects those without verbatim evidence
2. Confidence threshold: issues below 0.70 confidence are suppressed in the UI by default
3. Periodic calibration: compare false positive rate across projects and adjust thresholds

---

## Ablation Study Design

To understand which components of SpecTwin contribute most to performance:

| Ablation                           | What it measures                                    |
|------------------------------------|-----------------------------------------------------|
| Remove EvidenceCriticAgent         | Value of the validation/critic step                 |
| Remove discussion artifacts        | Value of informal communication context             |
| Remove code diff artifacts         | Value of implementation evidence                    |
| Single agent vs multi-agent        | Value of role-specialized orchestration             |
| Mock mode vs real LLM              | Gap between deterministic and generative outputs    |
| With vs without security hardening | Impact of prompt injection sanitization on accuracy |

---

## Reporting Template

When reporting SpecTwin results in a paper or technical report:

```
Model:          [model name + version]
Dataset:        SpecDriftBench v1.0 (N samples)
Artifacts used: [list artifact fields included]
Mode:           [mock | real | gpt-4o | claude-opus-4-5]

Accuracy:       X.XX
Macro F1:       X.XX
Contradiction P/R/F1: X.XX / X.XX / X.XX
False Positive Rate:  X.XX
```
