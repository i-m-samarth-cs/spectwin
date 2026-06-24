"""
AmbiguityDetectionAgent
Detects vague, unmeasurable, or temporal requirements.
"""
from __future__ import annotations
from app.agents.base import BaseAgent

class AmbiguityDetectionAgent(BaseAgent):
    name = "AmbiguityDetectionAgent"
    _prompt_file = "ambiguity_detection.txt"
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
                    "title": "REQ-NOTIF-006: Delivery receipt retention period ambiguous",
                    "description": "REQ-NOTIF-006 states receipts SHALL be stored for 90 days but does not specify whether this is calendar days, business days, or rolling window.",
                    "category": "ambiguous_requirement",
                    "severity": "low",
                    "confidence": 0.82,
                    "evidence": {
                        "source": "PRD",
                        "ambiguous_statement": "Delivery receipts SHALL be stored for 90 days (REQ-NOTIF-006)",
                        "ambiguity_type": "temporal"
                    },
                    "suggested_action": "Clarify REQ-NOTIF-006: specify calendar days, define retention window trigger.",
                    "reasoning": "Requirement uses vague temporal language that could lead to implementation disagreements."
                }
            ],
            "total_found": 1
        }
