#!/usr/bin/env python3
"""
SpecDriftBench Evaluation Script
Computes precision, recall, F1, accuracy, and confusion matrix
for a set of model predictions against a gold-labeled dataset.

Security note:
  - All file I/O uses explicit paths validated at startup.
  - No shell commands are executed; no user-controlled strings are eval()'d.
  - Output is written only to the explicitly specified --output path.
  - Input JSON is parsed with json.load() — no arbitrary code execution.

Usage:
    python evaluate.py --gold gold.json --predictions preds.json --output results.json
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# All valid labels — hardcoded, not derived from user input
VALID_LABELS = [
    "aligned",
    "ambiguous",
    "contradictory",
    "undocumented_change",
    "missing_acceptance_criteria",
    "missing_test",
    "missing_dependency",
    "unclear_owner",
    "release_mismatch",
    "discussed_not_implemented",
]


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def load_json_file(path: Path) -> dict:
    """Load and parse a JSON file. Raises with a clear message on failure."""
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_samples(data: dict) -> List[dict]:
    """Handle both wrapped ({samples: [...]}) and bare ([...]) formats."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "samples" in data:
        return data["samples"]
    print("[ERROR] Unrecognized data format. Expected list or {samples: [...]}.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Metric computation (no external dependencies)
# ---------------------------------------------------------------------------

def compute_metrics(
    gold_labels: List[str],
    pred_labels: List[str],
    labels: List[str],
) -> Dict:
    """
    Compute per-class precision, recall, F1, macro averages, and accuracy.
    Returns a structured dict suitable for JSON serialization.
    """
    # Confusion matrix: matrix[true][pred]
    matrix: Dict[str, Dict[str, int]] = {
        l: {l2: 0 for l2 in labels} for l in labels
    }
    for gold, pred in zip(gold_labels, pred_labels):
        if gold in matrix and pred in matrix:
            matrix[gold][pred] += 1

    # Per-class metrics
    per_class = {}
    for label in labels:
        tp = matrix[label][label]
        fp = sum(matrix[other][label] for other in labels if other != label)
        fn = sum(matrix[label][other] for other in labels if other != label)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        support = tp + fn

        per_class[label] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "support": support,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    # Macro averages (unweighted)
    active_labels = [l for l in labels if per_class[l]["support"] > 0]
    macro_precision = sum(per_class[l]["precision"] for l in active_labels) / max(len(active_labels), 1)
    macro_recall = sum(per_class[l]["recall"] for l in active_labels) / max(len(active_labels), 1)
    macro_f1 = sum(per_class[l]["f1"] for l in active_labels) / max(len(active_labels), 1)

    # Weighted averages
    total_support = sum(per_class[l]["support"] for l in labels)
    weighted_precision = (
        sum(per_class[l]["precision"] * per_class[l]["support"] for l in labels) / total_support
        if total_support > 0 else 0.0
    )
    weighted_recall = (
        sum(per_class[l]["recall"] * per_class[l]["support"] for l in labels) / total_support
        if total_support > 0 else 0.0
    )
    weighted_f1 = (
        sum(per_class[l]["f1"] * per_class[l]["support"] for l in labels) / total_support
        if total_support > 0 else 0.0
    )

    # Accuracy
    correct = sum(1 for g, p in zip(gold_labels, pred_labels) if g == p)
    accuracy = correct / len(gold_labels) if gold_labels else 0.0

    return {
        "accuracy": round(accuracy, 4),
        "macro": {
            "precision": round(macro_precision, 4),
            "recall": round(macro_recall, 4),
            "f1": round(macro_f1, 4),
        },
        "weighted": {
            "precision": round(weighted_precision, 4),
            "recall": round(weighted_recall, 4),
            "f1": round(weighted_f1, 4),
        },
        "per_class": per_class,
        "confusion_matrix": matrix,
        "total_samples": len(gold_labels),
        "correct_predictions": correct,
    }


# ---------------------------------------------------------------------------
# Report printer
# ---------------------------------------------------------------------------

def print_report(metrics: Dict, model_id: str) -> None:
    """Print a formatted classification report to stdout."""
    print("\n" + "=" * 65)
    print(f"  SpecDriftBench Evaluation Report")
    print(f"  Model: {model_id}")
    print("=" * 65)
    print(f"\n  Accuracy : {metrics['accuracy']:.4f}  ({metrics['correct_predictions']}/{metrics['total_samples']})")
    print(f"  Macro F1 : {metrics['macro']['f1']:.4f}")
    print(f"  Macro P  : {metrics['macro']['precision']:.4f}")
    print(f"  Macro R  : {metrics['macro']['recall']:.4f}")
    print(f"\n  {'Label':<35} {'P':>6} {'R':>6} {'F1':>6} {'Sup':>5}")
    print(f"  {'-'*35} {'------':>6} {'------':>6} {'------':>6} {'-----':>5}")

    per_class = metrics["per_class"]
    for label in VALID_LABELS:
        if label not in per_class:
            continue
        m = per_class[label]
        if m["support"] == 0:
            continue
        print(
            f"  {label:<35} {m['precision']:>6.4f} {m['recall']:>6.4f} {m['f1']:>6.4f} {m['support']:>5}"
        )

    print("\n  Confusion Matrix (rows=gold, cols=pred):")
    short = {l: l[:10] for l in VALID_LABELS}
    active = [l for l in VALID_LABELS if per_class.get(l, {}).get("support", 0) > 0]
    header = "  " + " " * 14 + "  ".join(f"{short[l]:>10}" for l in active)
    print(header)
    cm = metrics["confusion_matrix"]
    for gold_lbl in active:
        row = f"  {short[gold_lbl]:<14}" + "  ".join(
            f"{cm.get(gold_lbl, {}).get(pred_lbl, 0):>10}" for pred_lbl in active
        )
        print(row)
    print("=" * 65 + "\n")


# ---------------------------------------------------------------------------
# Alignment / joining gold and predictions
# ---------------------------------------------------------------------------

def align_samples(gold_samples: List[dict], pred_samples: List[dict]) -> Tuple[List[str], List[str], List[dict]]:
    """
    Join gold and prediction samples by 'id' field.
    Returns (gold_labels, pred_labels, mismatches).
    """
    pred_map = {s["id"]: s for s in pred_samples if "id" in s}
    gold_labels, pred_labels, mismatches = [], [], []

    for sample in gold_samples:
        sid = sample.get("id")
        gold_lbl = sample.get("label")
        if not sid or not gold_lbl:
            continue
        if sid not in pred_map:
            mismatches.append({"id": sid, "issue": "missing_prediction"})
            continue
        pred_lbl = pred_map[sid].get("predicted_label")
        if not pred_lbl:
            mismatches.append({"id": sid, "issue": "missing_predicted_label"})
            continue
        gold_labels.append(gold_lbl)
        pred_labels.append(pred_lbl)

    return gold_labels, pred_labels, mismatches


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate SpecDriftBench predictions against a gold dataset."
    )
    parser.add_argument("--gold", required=True, help="Path to gold-labeled JSON file")
    parser.add_argument("--predictions", required=True, help="Path to predictions JSON file (must include predicted_label per sample)")
    parser.add_argument("--output", default="eval_results.json", help="Path to write evaluation results JSON")
    parser.add_argument("--model", default="unknown", help="Model identifier for the report")
    args = parser.parse_args()

    # Security: resolve paths and validate they are files
    gold_path = Path(args.gold).resolve()
    pred_path = Path(args.predictions).resolve()
    output_path = Path(args.output).resolve()

    print(f"Loading gold dataset:   {gold_path}")
    print(f"Loading predictions:    {pred_path}")

    gold_data = load_json_file(gold_path)
    pred_data = load_json_file(pred_path)

    gold_samples = extract_samples(gold_data)
    pred_samples = extract_samples(pred_data)

    print(f"Gold samples:           {len(gold_samples)}")
    print(f"Prediction samples:     {len(pred_samples)}")

    gold_labels, pred_labels, mismatches = align_samples(gold_samples, pred_samples)
    print(f"Aligned pairs:          {len(gold_labels)}")

    if mismatches:
        print(f"[WARN] {len(mismatches)} samples could not be aligned:")
        for m in mismatches[:5]:
            print(f"  {m}")

    if not gold_labels:
        print("[ERROR] No aligned samples found. Check that both files use matching 'id' fields.", file=sys.stderr)
        sys.exit(1)

    metrics = compute_metrics(gold_labels, pred_labels, VALID_LABELS)
    print_report(metrics, args.model)

    result_output = {
        "meta": {
            "model": args.model,
            "gold_file": str(gold_path),
            "predictions_file": str(pred_path),
            "total_samples": len(gold_labels),
            "unaligned_samples": len(mismatches),
        },
        "metrics": metrics,
        "mismatches": mismatches,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_output, f, indent=2, ensure_ascii=True)

    print(f"Results saved → {output_path}")


if __name__ == "__main__":
    main()
