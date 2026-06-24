import uuid
from datetime import datetime
from sqlalchemy import String, Text, Enum, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base
import enum

class DriftLabel(str, enum.Enum):
    aligned = "aligned"
    ambiguous = "ambiguous"
    contradictory = "contradictory"
    undocumented_change = "undocumented_change"
    missing_acceptance_criteria = "missing_acceptance_criteria"
    missing_test = "missing_test"
    missing_dependency = "missing_dependency"
    unclear_owner = "unclear_owner"
    release_mismatch = "release_mismatch"
    discussed_not_implemented = "discussed_not_implemented"

class EvaluationSample(Base):
    __tablename__ = "evaluation_samples"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[str] = mapped_column(String(100), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prd_text: Mapped[str] = mapped_column(Text, nullable=False)
    ticket_text: Mapped[str] = mapped_column(Text, nullable=False)
    discussion_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    api_spec_excerpt: Mapped[str] = mapped_column(Text, nullable=True)
    code_diff_summary: Mapped[str] = mapped_column(Text, nullable=True)
    test_case_text: Mapped[str] = mapped_column(Text, nullable=True)
    release_note: Mapped[str] = mapped_column(Text, nullable=True)
    label: Mapped[DriftLabel] = mapped_column(Enum(DriftLabel), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    human_reviewed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    total_samples: Mapped[int] = mapped_column(Integer, default=0)
    correct_predictions: Mapped[int] = mapped_column(Integer, default=0)
    accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    precision: Mapped[float] = mapped_column(Float, nullable=True)
    recall: Mapped[float] = mapped_column(Float, nullable=True)
    f1_score: Mapped[float] = mapped_column(Float, nullable=True)
    results: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
