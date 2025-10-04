"""Analysis API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from app.models.database import get_db
from app.models.awr_report import AWRReport
from app.models.performance_metric import PerformanceMetric
from app.models.diagnostic_result import DiagnosticResult, Severity
from app.schemas.metric import MetricResponse
from app.schemas.diagnostic import DiagnosticResponse, DiagnosticSummary, DiagnosticItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["analysis"])


@router.get("/{report_id}/metrics/{category}", response_model=MetricResponse)
def get_metrics(
    report_id: int,
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for a specific category

    - **report_id**: Report ID
    - **category**: Metric category (load_profile, wait_events, sql_stats, io_stats, memory_stats, instance_efficiency)
    """
    logger.info(f"Getting metrics: report_id={report_id}, category={category}")

    # Verify report exists
    report = db.query(AWRReport).filter(AWRReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Get metrics
    metric = db.query(PerformanceMetric).filter(
        PerformanceMetric.report_id == report_id,
        PerformanceMetric.metric_category == category
    ).first()

    if not metric:
        raise HTTPException(status_code=404, detail=f"Metrics not found for category: {category}")

    return {
        "category": category,
        "data": metric.metric_data
    }


@router.post("/{report_id}/analyze")
def analyze_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Trigger analysis for a report

    - **report_id**: Report ID
    """
    logger.info(f"Triggering analysis for report: {report_id}")

    # Verify report exists
    report = db.query(AWRReport).filter(AWRReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # TODO: Trigger async analysis task
    # from app.tasks.analysis_tasks import analyze_report_task
    # task = analyze_report_task.delay(report_id)

    return {
        "message": "Analysis started",
        "report_id": report_id
    }


@router.get("/{report_id}/diagnostics", response_model=DiagnosticResponse)
def get_diagnostics(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get diagnostic results for a report

    - **report_id**: Report ID
    """
    logger.info(f"Getting diagnostics for report: {report_id}")

    # Verify report exists
    report = db.query(AWRReport).filter(AWRReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Get all diagnostics
    diagnostics = db.query(DiagnosticResult).filter(
        DiagnosticResult.report_id == report_id
    ).order_by(
        DiagnosticResult.severity,
        DiagnosticResult.created_at
    ).all()

    # Calculate summary
    summary = DiagnosticSummary()
    for diag in diagnostics:
        if diag.severity == Severity.CRITICAL:
            summary.critical += 1
        elif diag.severity == Severity.HIGH:
            summary.high += 1
        elif diag.severity == Severity.MEDIUM:
            summary.medium += 1
        elif diag.severity == Severity.LOW:
            summary.low += 1

    return {
        "report_id": report_id,
        "summary": summary,
        "diagnostics": diagnostics
    }
