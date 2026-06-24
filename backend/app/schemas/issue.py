from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.issue import IssueSeverity, IssueCategory, IssueStatus

class DriftIssueResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str
    category: IssueCategory
    severity: IssueSeverity
    status: IssueStatus
    confidence: float
    evidence: dict
    suggested_action: Optional[str]
    linked_artifact_ids: list
    reasoning: Optional[str]
    agent_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class IssueStatusUpdate(BaseModel):
    status: IssueStatus
