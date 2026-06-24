#!/usr/bin/env python3
"""
SpecDriftBench Sample Generator
Generates synthetic cross-artifact alignment samples for the SpecDriftBench dataset.

Security note: All template strings are statically defined. No user input is
interpolated into generated content without sanitization. Output is written only
to the explicitly specified --output path.

Usage:
    python generate_samples.py --count 50 --output samples.json
    python generate_samples.py --count 20 --label contradictory --output contradictions.json
"""

import argparse
import json
import random
import uuid
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Seed feature ideas (domain, feature_name, owner_a, owner_b)
# ---------------------------------------------------------------------------
FEATURE_IDEAS = [
    {
        "domain": "payments",
        "feature": "Instant Settlement",
        "req_id": "REQ-PAY-001",
        "owner": "Jordan L.",
        "tier_gate": "Premium",
        "sla": "90 seconds",
    },
    {
        "domain": "auth",
        "feature": "MFA Enforcement",
        "req_id": "REQ-AUTH-002",
        "owner": "Dana W.",
        "tier_gate": "admin role",
        "sla": "N/A",
    },
    {
        "domain": "search",
        "feature": "Query Autocomplete",
        "req_id": "REQ-SEARCH-007",
        "owner": "(unassigned)",
        "tier_gate": "N/A",
        "sla": "50ms p99",
    },
    {
        "domain": "notifications",
        "feature": "Bulk Campaign Send",
        "req_id": "REQ-NOTIF-007",
        "owner": "Sam R.",
        "tier_gate": "N/A",
        "sla": "10 minutes for 100k",
    },
    {
        "domain": "billing",
        "feature": "Prorated Downgrade Refund",
        "req_id": "REQ-BILL-007",
        "owner": "Chris T.",
        "tier_gate": "N/A",
        "sla": "24 hours",
    },
    {
        "domain": "export",
        "feature": "CSV Column Selection",
        "req_id": "REQ-EXPORT-001",
        "owner": "Lee P.",
        "tier_gate": "N/A",
        "sla": "N/A",
    },
    {
        "domain": "onboarding",
        "feature": "Email Verification",
        "req_id": "REQ-ONBOARD-001",
        "owner": "Dana W.",
        "tier_gate": "N/A",
        "sla": "24h link expiry",
    },
    {
        "domain": "analytics",
        "feature": "Real-Time Dashboard",
        "req_id": "REQ-ANAL-004",
        "owner": "Morgan K.",
        "tier_gate": "Enterprise",
        "sla": "5 second refresh",
    },
    {
        "domain": "api_gateway",
        "feature": "Request Rate Limiting",
        "req_id": "REQ-GW-003",
        "owner": "Alex R.",
        "tier_gate": "N/A",
        "sla": "< 1ms overhead",
    },
    {
        "domain": "storage",
        "feature": "File Retention Policy",
        "req_id": "REQ-STORE-005",
        "owner": "Riley J.",
        "tier_gate": "N/A",
        "sla": "90 days",
    },
    {
        "domain": "webhooks",
        "feature": "Webhook Delivery Retry",
        "req_id": "REQ-WH-002",
        "owner": "Sam R.",
        "tier_gate": "N/A",
        "sla": "3 retries, 5 minutes",
    },
    {
        "domain": "compliance",
        "feature": "Audit Log Retention",
        "req_id": "REQ-COMP-001",
        "owner": "Morgan K.",
        "tier_gate": "N/A",
        "sla": "365 days",
    },
]

# ---------------------------------------------------------------------------
# Template builders (pure functions, no external input interpolation)
# ---------------------------------------------------------------------------

def build_aligned_sample(feature: dict, idx: int) -> dict:
    """Generate a fully consistent aligned sample."""
    domain = feature["domain"]
    fname = feature["feature"]
    req_id = feature["req_id"]
    owner = feature["owner"]
    sla = feature["sla"]

    prd = (
        f"{req_id}: The {fname} feature SHALL be implemented as described. "
        f"Owner: {owner}. SLA: {sla}. "
        f"All edge cases SHALL be covered by acceptance tests prior to release."
    )
    ticket = (
        f"TICKET {domain.upper()}-{100 + idx}\n"
        f"Title: Implement {fname}\n"
        f"Status: Done\n"
        f"Assignee: {owner}\n"
        f"Description: Implemented per {req_id}. All acceptance criteria met. "
        f"Tests written and passing. Documentation updated."
    )
    discussion = (
        f"Teams #{domain}-dev\n"
        f"{owner}: {fname} shipped. All requirements from {req_id} implemented.\n"
        f"Alex: Looks good—tests green, docs updated?"
        f"\n{owner}: Yes, all done."
    )
    api_spec = (
        f"POST /v1/{domain}/{fname.lower().replace(' ', '-')}\n"
        f"Status: Stable\n"
        f"Description: '{fname} as defined in {req_id}. SLA: {sla}.'"
    )
    code_diff = (
        f"{domain}_service.py: {fname} fully implemented per {req_id}. "
        f"All paths covered. Documentation updated. Unit and integration tests added."
    )
    test_case = (
        f"TC-{req_id}-001: Core happy path: PASS\n"
        f"TC-{req_id}-002: Edge case handling: PASS\n"
        f"TC-{req_id}-003: Error path: PASS\n"
        f"TC-{req_id}-004: SLA validation ({sla}): PASS"
    )
    release_note = (
        f"{domain.capitalize()} release: {fname} now available. "
        f"Fully implemented per {req_id} with SLA {sla}."
    )
    return {
        "id": f"sdb-gen-{str(uuid.uuid4())[:8]}",
        "project_id": f"proj-{domain}",
        "feature_name": fname,
        "prd_text": prd,
        "ticket_text": ticket,
        "discussion_snippet": discussion,
        "api_spec_excerpt": api_spec,
        "code_diff_summary": code_diff,
        "test_case_text": test_case,
        "release_note": release_note,
        "label": "aligned",
        "rationale": (
            f"All artifacts consistently describe {fname} per {req_id}. "
            "No contradictions, ambiguities, or missing elements detected."
        ),
    }


def inject_contradiction(sample: dict) -> dict:
    """
    Mutation: introduce a scope contradiction between PRD and code/ticket.
    The PRD restricts a feature; the ticket expands it without PRD update.
    """
    s = deepcopy(sample)
    fname = s["feature_name"]
    domain = s["project_id"].replace("proj-", "")
    s["ticket_text"] += (
        f"\n\nNOTE: Scope expanded informally — {fname} now applies to ALL tiers, "
        f"not just the restricted set in the PRD. No PRD update made."
    )
    s["code_diff_summary"] += (
        f" ADDITIONAL: Tier restriction removed from {domain}_service.py "
        f"without documentation update."
    )
    s["release_note"] = (
        f"{domain.capitalize()} release: {fname} available with original restrictions only."
    )
    s["api_spec_excerpt"] += (
        f"\nNote: All tiers now supported (expanded from PRD definition)."
    )
    s["label"] = "contradictory"
    s["rationale"] = (
        f"PRD defines restricted scope. Ticket and code expand scope without PRD update. "
        f"Release note contradicts the expanded scope by referencing original restrictions. "
        f"Four artifacts are mutually inconsistent on the same feature boundary."
    )
    return s


def inject_ambiguity(sample: dict) -> dict:
    """
    Mutation: introduce vague/underspecified language in PRD that allows
    multiple valid interpretations.
    """
    s = deepcopy(sample)
    # Replace precise PRD text with ambiguous version
    s["prd_text"] = (
        f"The {s['feature_name']} feature should work in a reasonable timeframe "
        f"for most users under normal conditions. Edge cases should be handled "
        f"appropriately. The system should behave correctly."
    )
    s["discussion_snippet"] += (
        "\nAlex: What does 'reasonable timeframe' mean exactly?"
        "\nOwner: Not sure—we'll define it during implementation."
        "\nAlex: That needs to be in the PRD before we build it."
    )
    s["test_case_text"] = (
        f"TC-001: Feature works under normal conditions: PASS\n"
        f"TC-002: Performance under load: SKIPPED (no SLA defined)\n"
        f"TC-003: Edge case handling: PARTIAL (criteria undefined)"
    )
    s["label"] = "ambiguous"
    s["rationale"] = (
        f"PRD uses vague language ('reasonable', 'most users', 'appropriate') "
        f"with no measurable acceptance criteria. Discussion confirms the ambiguity "
        f"was not resolved before implementation. Tests are incomplete as a result."
    )
    return s


def inject_undocumented_change(sample: dict) -> dict:
    """
    Mutation: code introduces a behavioral change not present in PRD or docs.
    """
    s = deepcopy(sample)
    domain = s["project_id"].replace("proj-", "")
    s["code_diff_summary"] = (
        f"{domain}_service.py: ADDITIONAL CHANGE — "
        f"Default behavior modified from documented specification. "
        f"New behavior: stricter validation applied silently. "
        f"No PRD update, no ticket, no documentation change made. "
        f"Change introduced by {random.choice(['Jordan L.', 'Sam R.', 'Lee P.'])} "
        f"during refactor."
    )
    s["prd_text"] += " [Original PRD — not updated to reflect implementation changes]"
    s["release_note"] += " [Release note does not mention behavioral change]"
    s["label"] = "undocumented_change"
    s["rationale"] = (
        f"Code introduces a behavioral change (stricter validation) not present in PRD, "
        f"ticket, or release notes. The change has no documentation trail and no tests "
        f"specific to the new behavior."
    )
    return s


def inject_missing_test(sample: dict) -> dict:
    """
    Mutation: key code behavior has no test coverage.
    """
    s = deepcopy(sample)
    fname = s["feature_name"]
    s["code_diff_summary"] += (
        f" NEW PATH: Added {fname.lower()} fast-path for premium accounts. "
        f"No unit tests written for this path."
    )
    s["test_case_text"] = (
        f"TC-001: Standard path: PASS\n"
        f"TC-002: Premium fast-path: NOT WRITTEN\n"
        f"TC-003: Error handling: PASS"
    )
    s["label"] = "missing_test"
    s["rationale"] = (
        f"Code adds a new execution path for premium accounts but no test covers it. "
        f"PRD implies this path exists; ticket mentions it was implemented; "
        f"but the test suite has a gap for this behavior."
    )
    return s


def inject_release_mismatch(sample: dict) -> dict:
    """
    Mutation: release notes claim a metric or feature that tests contradict.
    """
    s = deepcopy(sample)
    fname = s["feature_name"]
    domain = s["project_id"].replace("proj-", "")
    s["test_case_text"] = (
        f"TC-001: Core functionality: PASS\n"
        f"TC-002: Performance SLA validation: FAIL (actual 340ms vs claimed 50ms)\n"
        f"TC-003: Edge case: PASS"
    )
    s["release_note"] = (
        f"{domain.capitalize()} release: {fname} delivers industry-leading performance "
        f"with sub-50ms response times and 99.99% accuracy."
    )
    s["label"] = "release_mismatch"
    s["rationale"] = (
        f"Release note claims sub-50ms performance and 99.99% accuracy. "
        f"Test TC-002 shows actual latency of 340ms. Release note contains "
        f"performance claims that are directly contradicted by test evidence."
    )
    return s


# ---------------------------------------------------------------------------
# Label -> mutation mapping
# ---------------------------------------------------------------------------
MUTATIONS = {
    "aligned": None,
    "contradictory": inject_contradiction,
    "undocumented_change": inject_undocumented_change,
    "ambiguous": inject_ambiguity,
    "missing_test": inject_missing_test,
    "release_mismatch": inject_release_mismatch,
}

LABELS = list(MUTATIONS.keys())


def generate_sample(feature: dict, label: Optional[str], idx: int) -> dict:
    """Generate one sample for the given feature and label."""
    if label is None:
        label = random.choice(LABELS)
    base = build_aligned_sample(feature, idx)
    mutation_fn = MUTATIONS[label]
    if mutation_fn is not None:
        return mutation_fn(base)
    return base


def generate_dataset(count: int, label_filter: Optional[str] = None) -> list:
    """Generate `count` samples, cycling through features."""
    samples = []
    for i in range(count):
        feature = FEATURE_IDEAS[i % len(FEATURE_IDEAS)]
        chosen_label = label_filter if label_filter else LABELS[i % len(LABELS)]
        sample = generate_sample(feature, chosen_label, i)
        samples.append(sample)
    return samples


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic SpecDriftBench samples. "
                    "Output is plain JSON — no code execution, no external calls."
    )
    parser.add_argument("--count", type=int, default=50, help="Number of samples to generate")
    parser.add_argument(
        "--label",
        choices=LABELS + ["all"],
        default="all",
        help="Generate only samples with this label (default: balanced across all)",
    )
    parser.add_argument("--output", type=str, default="samples.json", help="Output JSON file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    # Security: validate output path stays within allowed directory
    output_path = Path(args.output).resolve()
    random.seed(args.seed)

    label_filter = None if args.label == "all" else args.label
    samples = generate_dataset(args.count, label_filter)

    output = {
        "meta": {
            "dataset": "SpecDriftBench",
            "version": "1.0.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_samples": len(samples),
            "seed": args.seed,
            "label_distribution": {
                lbl: sum(1 for s in samples if s["label"] == lbl) for lbl in LABELS
            },
        },
        "samples": samples,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=True)

    print(f"Generated {len(samples)} samples → {output_path}")
    for lbl, cnt in output["meta"]["label_distribution"].items():
        print(f"  {lbl:30s}: {cnt}")


if __name__ == "__main__":
    main()
