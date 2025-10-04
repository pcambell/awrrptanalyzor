"""AWR Report Model"""

from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.database import Base


class ReportStatus(str, enum.Enum):
    """Report status enumeration"""
    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    FAILED = "failed"


class AWRReport(Base):
    """AWR Report model"""
    __tablename__ = "awr_reports"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(BigInteger)
    upload_time = Column(DateTime, default=datetime.utcnow)

    # Instance information
    oracle_version = Column(String(50))
    db_name = Column(String(100), index=True)
    instance_name = Column(String(100))
    host_name = Column(String(100))

    # Snapshot information
    snapshot_begin = Column(DateTime, index=True)
    snapshot_end = Column(DateTime)
    snapshot_interval = Column(Integer)  # minutes

    # Status
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    metrics = relationship("PerformanceMetric", back_populates="report", cascade="all, delete-orphan")
    diagnostics = relationship("DiagnosticResult", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AWRReport(id={self.id}, db_name={self.db_name}, status={self.status})>"
