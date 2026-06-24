import uuid
from datetime import datetime
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import enum

class ProjectStatus(str, enum.Enum):
    draft = "draft"
    ingesting = "ingesting"
    analyzing = "analyzing"
    ready = "ready"
    archived = "archived"

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.draft)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    release_readiness_score: Mapped[float] = mapped_column(Float, nullable=True)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0)
    artifact_count: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    artifacts: Mapped[list["Artifact"]] = relationship("Artifact", back_populates="project", lazy="selectin")
    twin_nodes: Mapped[list["TwinNode"]] = relationship("TwinNode", back_populates="project", lazy="selectin")
    twin_edges: Mapped[list["TwinEdge"]] = relationship("TwinEdge", back_populates="project", lazy="selectin")
    issues: Mapped[list["DriftIssue"]] = relationship("DriftIssue", back_populates="project", lazy="selectin")
