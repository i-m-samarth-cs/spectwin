from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.twin import NodeType, EdgeType

class TwinNodeResponse(BaseModel):
    id: UUID
    project_id: UUID
    node_type: NodeType
    label: str
    description: Optional[str]
    confidence: float
    properties: dict
    created_at: datetime
    model_config = {"from_attributes": True}

class TwinEdgeResponse(BaseModel):
    id: UUID
    project_id: UUID
    source_node_id: UUID
    target_node_id: UUID
    edge_type: EdgeType
    confidence: float
    properties: dict
    created_at: datetime
    model_config = {"from_attributes": True}

class TwinGraphResponse(BaseModel):
    nodes: list[TwinNodeResponse]
    edges: list[TwinEdgeResponse]
    node_count: int
    edge_count: int
