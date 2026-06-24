import uuid
from datetime import datetime
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import enum

class NodeType(str, enum.Enum):
    feature = "feature"
    requirement = "requirement"
    constraint = "constraint"
    decision = "decision"
    dependency = "dependency"
    owner = "owner"
    api_contract = "api_contract"
    implementation_change = "implementation_change"
    test_artifact = "test_artifact"
    release_issue = "release_issue"

class EdgeType(str, enum.Enum):
    implements = "implements"
    depends_on = "depends_on"
    contradicts = "contradicts"
    tests = "tests"
    documents = "documents"
    owned_by = "owned_by"
    introduced_in = "introduced_in"
    related_to = "related_to"

class TwinNode(Base):
    __tablename__ = "twin_nodes"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    node_type: Mapped[NodeType] = mapped_column(Enum(NodeType), nullable=False)
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    source_artifact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    project: Mapped["Project"] = relationship("Project", back_populates="twin_nodes")

class TwinEdge(Base):
    __tablename__ = "twin_edges"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    source_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("twin_nodes.id"), nullable=False)
    target_node_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("twin_nodes.id"), nullable=False)
    edge_type: Mapped[EdgeType] = mapped_column(Enum(EdgeType), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    project: Mapped["Project"] = relationship("Project", back_populates="twin_edges")
