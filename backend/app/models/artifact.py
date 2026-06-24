import uuid
from datetime import datetime
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import enum

class ArtifactType(str, enum.Enum):
    prd = "prd"
    ticket = "ticket"
    discussion = "discussion"
    api_spec = "api_spec"
    code_change = "code_change"
    test_case = "test_case"
    release_note = "release_note"
    meeting_summary = "meeting_summary"

class ArtifactStatus(str, enum.Enum):
    pending = "pending"
    parsed = "parsed"
    indexed = "indexed"
    failed = "failed"

class Artifact(Base):
    __tablename__ = "artifacts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    artifact_type: Mapped[ArtifactType] = mapped_column(Enum(ArtifactType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_content: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[ArtifactStatus] = mapped_column(Enum(ArtifactStatus), default=ArtifactStatus.pending)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    author: Mapped[str] = mapped_column(String(255), nullable=True)
    version: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project: Mapped["Project"] = relationship("Project", back_populates="artifacts")
