"""AWR Report Parsing Tasks"""

from celery import Task
import logging
from datetime import datetime

from app.tasks.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.awr_report import AWRReport, ReportStatus
from app.models.performance_metric import PerformanceMetric
from app.core.parser.factory import AWRParserFactory

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task class with database session management"""
    _db = None

    def after_return(self, *args, **kwargs):
        """Clean up database session after task completion"""
        if self._db is not None:
            self._db.close()
            self._db = None

    @property
    def db(self):
        """Get database session"""
        if self._db is None:
            self._db = SessionLocal()
        return self._db


@celery_app.task(base=DatabaseTask, bind=True, name="parse_awr_report")
def parse_awr_report_task(self, report_id: int):
    """
    Parse AWR HTML report and extract performance metrics

    Args:
        report_id: ID of the AWR report to parse

    Returns:
        dict: Parsing result with status and message
    """
    logger.info(f"Starting AWR report parsing task for report_id={report_id}")

    db = self.db

    try:
        # Get report from database
        report = db.query(AWRReport).filter(AWRReport.id == report_id).first()

        if not report:
            error_msg = f"Report not found: {report_id}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

        # Update status to parsing
        report.status = ReportStatus.PARSING
        report.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Reading file: {report.file_path}")

        # Read HTML file
        try:
            with open(report.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
        except Exception as e:
            error_msg = f"Failed to read file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            report.status = ReportStatus.FAILED
            report.error_message = error_msg
            db.commit()
            return {"status": "error", "message": error_msg}

        # Create parser and parse
        try:
            logger.info("Creating parser and parsing AWR report")
            parser = AWRParserFactory.create_parser(html_content)
            parsed_data = parser.parse()

            logger.info(f"Successfully parsed AWR report. Keys: {list(parsed_data.keys())}")

        except Exception as e:
            error_msg = f"Failed to parse AWR report: {str(e)}"
            logger.error(error_msg, exc_info=True)
            report.status = ReportStatus.FAILED
            report.error_message = error_msg
            db.commit()
            return {"status": "error", "message": error_msg}

        # Update report metadata
        try:
            instance_info = parsed_data.get('instance_info', {})
            snapshot_info = parsed_data.get('snapshot_info', {})

            report.oracle_version = instance_info.get('oracle_version')
            report.db_name = instance_info.get('db_name')
            report.instance_name = instance_info.get('instance_name')
            report.host_name = instance_info.get('host_name')
            report.snapshot_begin = snapshot_info.get('begin_time')
            report.snapshot_end = snapshot_info.get('end_time')

            # Calculate snapshot interval in minutes
            if report.snapshot_begin and report.snapshot_end:
                elapsed_seconds = snapshot_info.get('elapsed_time', 0)
                report.snapshot_interval = int(elapsed_seconds / 60) if elapsed_seconds > 0 else None

            logger.info(f"Updated report metadata: db_name={report.db_name}, version={report.oracle_version}")

        except Exception as e:
            logger.warning(f"Failed to update report metadata: {e}")

        # Store performance metrics
        try:
            metric_categories = [
                'load_profile',
                'wait_events',
                'top_sql',
                'memory_stats',
                'io_stats',
                'instance_efficiency'
            ]

            metrics_count = 0
            for category in metric_categories:
                if category in parsed_data and parsed_data[category]:
                    metric = PerformanceMetric(
                        report_id=report.id,
                        metric_category=category,
                        metric_data=parsed_data[category]
                    )
                    db.add(metric)
                    metrics_count += 1

            logger.info(f"Stored {metrics_count} performance metric categories")

        except Exception as e:
            error_msg = f"Failed to store performance metrics: {str(e)}"
            logger.error(error_msg, exc_info=True)
            report.status = ReportStatus.FAILED
            report.error_message = error_msg
            db.commit()
            return {"status": "error", "message": error_msg}

        # Update status to parsed
        report.status = ReportStatus.PARSED
        report.error_message = None
        report.updated_at = datetime.utcnow()
        db.commit()

        logger.info(f"Successfully completed parsing task for report_id={report_id}")

        return {
            "status": "success",
            "report_id": report_id,
            "db_name": report.db_name,
            "oracle_version": report.oracle_version
        }

    except Exception as e:
        error_msg = f"Unexpected error in parsing task: {str(e)}"
        logger.error(error_msg, exc_info=True)

        try:
            report.status = ReportStatus.FAILED
            report.error_message = error_msg
            db.commit()
        except:
            pass

        return {"status": "error", "message": error_msg}
