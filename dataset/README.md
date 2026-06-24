# SpecDriftBench

Cross-artifact alignment benchmark for evaluating specification drift detection in software projects.

## Quick Start

```bash
# Generate 100 synthetic samples
cd scripts
python generate_samples.py --count 100 --output samples_100.json

# Evaluate predictions against gold labels
python evaluate.py \
  --gold seed/specdriftbench_seed.json \
  --predictions my_predictions.json \
  --output results.json \
  --model my-model-name
```

## Structure

```
dataset/
  seed/
    specdriftbench_seed.json     12 gold-labeled seed samples
  scripts/
    generate_samples.py          Synthetic sample generator
    evaluate.py                  Precision / recall / F1 evaluator
  README.md                      This file
```

## Labels

| Label                        | Meaning                                               |
|------------------------------|-------------------------------------------------------|
| `aligned`                    | All artifacts consistent                              |
| `ambiguous`                  | Vague/unmeasurable requirement language               |
| `contradictory`              | Mutually exclusive claims across artifacts            |
| `undocumented_change`        | Code changed without doc update                       |
| `missing_acceptance_criteria`| No testable acceptance criteria defined               |
| `missing_test`               | Implemented behavior has no test coverage             |
| `missing_dependency`         | Undocumented dependency on another feature            |
| `unclear_owner`              | No assigned owner for a feature or decision           |
| `release_mismatch`           | Release notes contradict tests or code                |
| `discussed_not_implemented`  | Scoped and discussed but never built                  |

Full documentation: [`../docs/DATASET.md`](../docs/DATASET.md)
