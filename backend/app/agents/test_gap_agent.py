"""
TestGapAgent
Identifies requirements and shipped behaviors that lack test coverage.

Security: Only references test artifact content present in the provided inputs.
Does not suggest tests that could expose secrets, credentials, or bypass security controls.
"""
from __future__ import annotations

from app.agents.base import BaseAgent


class TestGapAgent(BaseAgent):
    name = "TestGapAgent"
    _prompt_file = "test_gap.txt"
    required_output_keys = ["agent", "findings", "total_found"]

    def build_context(self, project_id: str, artifacts: list[dict]) -> dict:
        return {
            "project_id": project_id,
            "artifacts_json": artifacts,
        }

    def get_mock_output(self, context: dict) -> dict:
        pid = context.get("project_id", "unknown")
        return {
            "agent": self.name,
            "project_id": pid,
            "findings": [
                {
                    "title": "All-tier instant settlement has no test coverage",
                    "description": (
                        "PR #887 enabled instant settlement for Basic and Standard tiers. "
                        "TC-PAY-005 (Basic tier) and TC-PAY-006 (Standard tier) are listed as NOT WRITTEN. "
                        "Only the pre-existing Premium tier test (TC-PAY-004) is present."
                    ),
                    "category": "missing_test",
                    "severity": "high",
                    "confidence": 0.98,
                    "evidence": {
                        "behavior_or_requirement": "All-tier instant settlement (PR #887)",
                        "source_artifact": "Test suite",
                        "test_status": "not_written",
                    },
                    "suggested_action": "Write TC-PAY-005 (Basic tier instant settlement) and TC-PAY-006 (Standard tier) before release.",
                    "reasoning": "New code path added by PR #887 has no corresponding test cases.",
                },
                {
                    "title": "REQ-002: 3 of 50 required currencies untested",
                    "description": "TC-002 shows IRR, MMK, and SYP currencies are not implemented. REQ-002 requires minimum 50 currencies.",
                    "category": "missing_test",
                    "severity": "medium",
                    "confidence": 0.93,
                    "evidence": {
                        "behavior_or_requirement": "REQ-PAY-002: 50 currency minimum",
                        "source_artifact": "Test suite — TC-002",
                        "test_status": "partial",
                    },
                    "suggested_action": "Implement and test IRR, MMK, and SYP currency support.",
                    "reasoning": "Test explicitly lists 3 unimplemented currencies against a SHALL requirement.",
                },
            ],
            "coverage_estimate": 71.4,
            "total_found": 2,
            "analysis_notes": "Mock output — reflects demo project data.",
        }
