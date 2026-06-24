from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.artifact import ArtifactType, ArtifactStatus

class ArtifactCreate(BaseModel):
    artifact_type: ArtifactType
    title: str
    raw_content: str
    source_url: Optional[str] = None
    author: Optional[str] = None
    version: Optional[str] = None

class IngestRequest(BaseModel):
    artifacts: list[ArtifactCreate]

class ArtifactResponse(BaseModel):
    id: UUID
    project_id: UUID
    artifact_type: ArtifactType
    title: str
    raw_content: str
    parsed_content: dict
    status: ArtifactStatus
    source_url: Optional[str]
    author: Optional[str]
    version: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}
