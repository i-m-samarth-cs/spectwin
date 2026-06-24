from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class GenerateCriteriaRequest(BaseModel):
    feature_description: str
    artifact_id: Optional[UUID] = None

class AcceptanceCriteriaResponse(BaseModel):
    id: UUID
    project_id: UUID
    artifact_id: Optional[UUID]
    feature_name: str
    criteria: list
    edge_cases: list
    negative_cases: list
    test_ideas: list
    is_reviewed: bool
    created_at: datetime
    model_config = {"from_attributes": True}
