import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class AcceptanceCriteria(Base):
    __tablename__ = "acceptance_criteria"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    artifact_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("artifacts.id"), nullable=True)
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria: Mapped[list] = mapped_column(JSONB, default=list)
    edge_cases: Mapped[list] = mapped_column(JSONB, default=list)
    negative_cases: Mapped[list] = mapped_column(JSONB, default=list)
    test_ideas: Mapped[list] = mapped_column(JSONB, default=list)
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
