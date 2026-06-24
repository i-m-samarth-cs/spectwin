from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.project import ProjectStatus

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectSummary(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: ProjectStatus
    release_readiness_score: Optional[float]
    open_issues_count: int
    artifact_count: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class ProjectResponse(ProjectSummary):
    owner_id: UUID
    meta: dict
