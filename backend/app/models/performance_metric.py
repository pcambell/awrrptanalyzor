"""Performance Metric Model"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.database import Base


class PerformanceMetric(Base):
    """Performance metric model with flexible JSONB storage"""
    __tablename__ = "performance_metrics"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key
    report_id = Column(Integer, ForeignKey("awr_reports.id", ondelete="CASCADE"), nullable=False, index=True)

    # Metric category
    # Categories: load_profile, wait_events, sql_stats, io_stats, memory_stats, instance_efficiency
    metric_category = Column(String(50), nullable=False, index=True)

    # Flexible JSONB storage for different Oracle versions
    metric_data = Column(JSONB, nullable=False)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    report = relationship("AWRReport", back_populates="metrics")

    def __repr__(self):
        return f"<PerformanceMetric(id={self.id}, report_id={self.report_id}, category={self.metric_category})>"
