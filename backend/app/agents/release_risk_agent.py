"""
ReleaseRiskAgent
Evaluates release readiness based on open issues.
"""
from __future__ import annotations
from app.agents.base import BaseAgent

class ReleaseRiskAgent(BaseAgent):
    name = "ReleaseRiskAgent"
    _prompt_file = "release_risk.txt"
    required_output_keys = ["agent", "score", "grade", "executive_summary", "risk_items"]

    def build_context(self, project_id: str, issues: list[dict], artifacts_summary: str) -> dict:
        return {
            "project_id": project_id,
            "issues_json": issues,
            "artifacts_summary": artifacts_summary,
        }

    def get_mock_output(self, context: dict) -> dict:
        pid = context.get("project_id", "unknown")
        return {
            "agent": self.name,
            "project_id": pid,
            "score": 32.0,
            "grade": "F",
            "unresolved_critical": 3,
            "unresolved_high": 4,
            "missing_tests": 1,
            "missing_docs": 2,
            "api_mismatches": 2,
            "scope_drift_count": 3,
            "executive_summary": "Payments Platform v3 is NOT ready for release. Three critical issues require resolution...",
            "risk_items": [
                {"title": "Fraud accuracy below compliance floor", "severity": "critical", "blocker": True},
                {"title": "Release notes contain false accuracy claim", "severity": "critical", "blocker": True},
            ]
        }
