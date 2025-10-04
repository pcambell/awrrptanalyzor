"""Report Management API Routes"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import os
import logging

from app.models.database import get_db
from app.schemas.report import ReportResponse, ReportListResponse, ReportDetail
from app.models.awr_report import AWRReport, ReportStatus
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/upload", response_model=ReportResponse, status_code=201)
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload AWR HTML report

    - **file**: AWR report HTML file
    """
    logger.info(f"Uploading file: {file.filename}")

    # Validate file type
    if not file.filename.endswith('.html'):
        raise HTTPException(status_code=400, detail="Only HTML files are supported")

    # Validate file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit ({settings.MAX_UPLOAD_SIZE} bytes)"
        )

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generate unique filename
    import uuid
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    safe_filename = f"{timestamp}_{unique_id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    # Save file
    try:
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)

        logger.info(f"File saved to: {file_path}")

    except Exception as e:
        logger.error(f"Error saving file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Create database record
    report = AWRReport(
        filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        status=ReportStatus.PENDING
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    logger.info(f"Created report record with ID: {report.id}")

    # Trigger async parsing task
    try:
        from app.tasks.parse_tasks import parse_awr_report_task
        task = parse_awr_report_task.delay(report.id)
        logger.info(f"Triggered parsing task: {task.id}")
    except Exception as e:
        logger.warning(f"Failed to trigger parsing task: {e}")
        # Don't fail the upload if task queue is unavailable

    return report


@router.get("", response_model=ReportListResponse)
def list_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of AWR reports with pagination and filtering

    - **page**: Page number (starting from 1)
    - **size**: Number of items per page
    - **db_name**: Filter by database name
    - **date_from**: Filter by upload date (YYYY-MM-DD)
    - **date_to**: Filter by upload date (YYYY-MM-DD)
    """
    logger.info(f"Listing reports: page={page}, size={size}, db_name={db_name}")

    # Build query
    query = db.query(AWRReport)

    # Apply filters
    if db_name:
        query = query.filter(AWRReport.db_name.ilike(f"%{db_name}%"))

    if date_from:
        try:
            from datetime import datetime
            date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AWRReport.upload_time >= date_from_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_from format (use YYYY-MM-DD)")

    if date_to:
        try:
            from datetime import datetime, timedelta
            date_to_dt = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(AWRReport.upload_time < date_to_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date_to format (use YYYY-MM-DD)")

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * size
    reports = query.order_by(AWRReport.upload_time.desc()).offset(offset).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": reports
    }


@router.get("/{report_id}", response_model=ReportDetail)
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific report

    - **report_id**: Report ID
    """
    logger.info(f"Getting report detail: {report_id}")

    report = db.query(AWRReport).filter(AWRReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.delete("/{report_id}", status_code=204)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a report

    - **report_id**: Report ID
    """
    logger.info(f"Deleting report: {report_id}")

    report = db.query(AWRReport).filter(AWRReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Delete file
    try:
        if os.path.exists(report.file_path):
            os.remove(report.file_path)
            logger.info(f"Deleted file: {report.file_path}")
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)

    # Delete database record (cascade will delete related records)
    db.delete(report)
    db.commit()

    logger.info(f"Deleted report {report_id}")

    return None
