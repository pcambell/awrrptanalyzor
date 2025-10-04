"""Metric Schemas"""

from pydantic import BaseModel
from typing import Dict, Any


class MetricResponse(BaseModel):
    """Schema for metric response"""
    category: str
    data: Dict[str, Any]
