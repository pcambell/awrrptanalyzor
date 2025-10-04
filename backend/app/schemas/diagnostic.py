"""Diagnostic Schemas"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class DiagnosticItem(BaseModel):
    """Schema for a single diagnostic item"""
    id: int
    rule_id: str
    severity: str
    category: str
    issue_title: str
    issue_description: str
    recommendation: str
    metric_values: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class DiagnosticSummary(BaseModel):
    """Schema for diagnostic summary"""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class DiagnosticResponse(BaseModel):
    """Schema for diagnostic response"""
    report_id: int
    summary: DiagnosticSummary
    diagnostics: List[DiagnosticItem]
