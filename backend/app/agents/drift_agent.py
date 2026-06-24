"""
DocCodeDriftAgent
Detects code changes that were made without corresponding documentation updates.

Security: Artifact content is sanitized. Findings cite only content present in inputs.
No external system details or credentials are inferred or returned.
"""
from __future__ import annotations

from app.agents.base import BaseAgent


class DocCodeDriftAgent(BaseAgent):
    name = "DocCodeDriftAgent"
    _prompt_file = "doc_code_drift.txt"
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
                    "title": "PR #887: Instant settlement scope change — no documentation update",
                    "description": (
                        "PR #887 removed the Premium-tier restriction on instant settlement. "
                        "The PR itself notes: 'No documentation update made to PRD or product wiki'. "
                        "The behavioral change shipped without any specification update."
                    ),
                    "category": "undocumented_change",
                    "severity": "high",
                    "confidence": 0.96,
                    "evidence": {
                        "code_change_source": "PR #887",
                        "code_change_description": "Removed `if merchant.tier == 'premium'` check. All merchants now routed to instant path.",
                        "missing_doc_update": "PRD REQ-004, product wiki, release notes",
                        "affected_artifacts": ["PRD", "Release Notes", "Product Wiki"],
                    },
                    "suggested_action": "Update PRD REQ-004 and release notes to reflect all-tier instant settlement, or revert the change.",
                    "reasoning": "Code change note explicitly states no documentation was updated for a user-facing behavioral change.",
                },
            ],
            "total_found": 1,
            "analysis_notes": "Mock output — reflects demo project data.",
        }
