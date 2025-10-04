"""Report Schemas"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ReportBase(BaseModel):
    """Base report schema"""
    filename: str
    db_name: Optional[str] = None
    instance_name: Optional[str] = None


class ReportCreate(ReportBase):
    """Schema for creating a report"""
    file_path: str
    file_size: int


class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    filename: str
    status: str
    db_name: Optional[str] = None
    instance_name: Optional[str] = None
    upload_time: datetime

    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    """Schema for detailed report information"""
    id: int
    filename: str
    file_size: Optional[int] = None
    upload_time: datetime
    oracle_version: Optional[str] = None
    db_name: Optional[str] = None
    instance_name: Optional[str] = None
    host_name: Optional[str] = None
    snapshot_begin: Optional[datetime] = None
    snapshot_end: Optional[datetime] = None
    snapshot_interval: Optional[int] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Schema for report list response"""
    total: int
    page: int
    size: int
    items: List[ReportResponse]
