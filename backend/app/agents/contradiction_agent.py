"""
ContradictionDetectionAgent
Detects statements that directly contradict each other across project artifacts.

Security: All artifact content is sanitized before prompt insertion.
Output is validated as JSON. No user content escapes the evidence fields.
"""
from __future__ import annotations

from app.agents.base import BaseAgent


class ContradictionDetectionAgent(BaseAgent):
    name = "ContradictionDetectionAgent"
    _prompt_file = "contradiction_detection.txt"
    required_output_keys = ["agent", "findings", "total_found"]

    def build_context(self, project_id: str, artifacts: list[dict]) -> dict:
        return {
            "project_id": project_id,
            "artifacts_json": artifacts,
        }

    def get_mock_output(self, context: dict) -> dict:
        """
        Deterministic mock output for demo mode.
        Reflects the Payments Platform v3 contradiction scenario.
        """
        pid = context.get("project_id", "unknown")
        return {
            "agent": self.name,
            "project_id": pid,
            "findings": [
                {
                    "title": "Instant settlement scope contradicts PRD (4 artifacts)",
                    "description": (
                        "PRD REQ-004 restricts instant settlement to Premium tier. "
                        "Ticket PAY-1042, PR #887, and the API spec all expand it to all tiers. "
                        "The release note reverts to the original Premium-only claim."
                    ),
                    "category": "contradictory_requirement",
                    "severity": "critical",
                    "confidence": 0.97,
                    "evidence": {
                        "artifact_a_source": "PRD",
                        "artifact_a_statement": "Instant settlement SHALL be available to merchants on the Premium tier only. (REQ-004)",
                        "artifact_b_source": "PR #887 / API Spec",
                        "artifact_b_statement": "Removed tier restriction. All merchants now eligible. API: 'All tiers now support instant'.",
                    },
                    "suggested_action": (
                        "Resolve scope: update PRD to all-tier or revert PR #887. "
                        "Either way, align release notes."
                    ),
                    "reasoning": (
                        "Four artifacts make mutually exclusive claims about the same "
                        "business rule. Code has shipped the expanded behavior but "
                        "PRD and release notes have not been updated."
                    ),
                },
            ],
            "total_found": 1,
            "analysis_notes": "Mock output — reflects demo project data.",
        }
