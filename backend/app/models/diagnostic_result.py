"""Diagnostic Result Model"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.database import Base


class Severity(str, enum.Enum):
    """Severity levels for diagnostic issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DiagnosticResult(Base):
    """Diagnostic result model"""
    __tablename__ = "diagnostic_results"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    report_id = Column(Integer, ForeignKey("awr_reports.id", ondelete="CASCADE"), nullable=False, index=True)

    # Rule information
    rule_id = Column(String(50), nullable=False)
    severity = Column(Enum(Severity), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # cpu, io, memory, sql, wait_event

    # Issue details
    issue_title = Column(String(255), nullable=False)
    issue_description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)

    # Related metric values
    metric_values = Column(JSONB)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    report = relationship("AWRReport", back_populates="diagnostics")

    def __repr__(self):
        return f"<DiagnosticResult(id={self.id}, rule_id={self.rule_id}, severity={self.severity})>"
