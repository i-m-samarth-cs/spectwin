from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    artifact_ids: Optional[list[str]] = None

class ReleaseReadinessResponse(BaseModel):
    score: float
    grade: str
    unresolved_critical: int
    unresolved_high: int
    missing_tests: int
    missing_docs: int
    api_mismatches: int
    scope_drift_count: int
    executive_summary: str
    risk_items: list[dict]

class TestGapResponse(BaseModel):
    implemented_without_tests: list[dict]
    tests_without_requirements: list[dict]
    requirements_without_tests: list[dict]
    coverage_score: float
