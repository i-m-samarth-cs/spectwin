import uuid
from datetime import datetime
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import enum

class IssueSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class IssueCategory(str, enum.Enum):
    ambiguous_requirement = "ambiguous_requirement"
    contradictory_requirement = "contradictory_requirement"
    undocumented_change = "undocumented_change"
    missing_acceptance_criteria = "missing_acceptance_criteria"
    missing_test = "missing_test"
    release_mismatch = "release_mismatch"
    unclear_ownership = "unclear_ownership"
    unresolved_dependency = "unresolved_dependency"
    missing_dependency = "missing_dependency"
    discussed_not_implemented = "discussed_not_implemented"

class IssueStatus(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    dismissed = "dismissed"

class DriftIssue(Base):
    __tablename__ = "drift_issues"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[IssueCategory] = mapped_column(Enum(IssueCategory), nullable=False)
    severity: Mapped[IssueSeverity] = mapped_column(Enum(IssueSeverity), nullable=False)
    status: Mapped[IssueStatus] = mapped_column(Enum(IssueStatus), default=IssueStatus.open)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, default=dict)
    suggested_action: Mapped[str] = mapped_column(Text, nullable=True)
    linked_artifact_ids: Mapped[list] = mapped_column(JSONB, default=list)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project: Mapped["Project"] = relationship("Project", back_populates="issues")
