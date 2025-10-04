"""Oracle 19c AWR Parser"""

from typing import Dict, Any
import logging
from datetime import datetime

from app.core.parser.base import BaseAWRParser
from app.core.parser.utils import parse_value, clean_text

logger = logging.getLogger(__name__)


class Oracle19cParser(BaseAWRParser):
    """Parser for Oracle 19c AWR reports"""

    def _parse_instance_info(self) -> Dict[str, Any]:
        """Parse instance information from the report header"""
        logger.debug("Parsing instance information")

        info = {
            'oracle_version': None,
            'db_name': None,
            'instance_name': None,
            'host_name': None,
        }

        # Find the top summary table
        # Usually contains DB Name, DB Id, Instance, Instance Number, Release, etc.
        for table in self.soup.find_all('table'):
            rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all(['td', 'th'])

                for i in range(len(cells) - 1):
                    key = clean_text(cells[i].get_text())
                    value = clean_text(cells[i+1].get_text())

                    if 'DB Name' in key:
                        info['db_name'] = value
                    elif 'Instance' == key:
                        info['instance_name'] = value
                    elif 'Host' in key or 'Hostname' in key:
                        info['host_name'] = value
                    elif 'Release' in key or 'Version' in key:
                        info['oracle_version'] = value

            # If we found db_name, this is likely the right table
            if info['db_name']:
                break

        logger.debug(f"Instance info: {info}")
        return info

    def _parse_snapshot_info(self) -> Dict[str, Any]:
        """Parse snapshot time range and interval"""
        logger.debug("Parsing snapshot information")

        snapshot_info = {
            'begin_snap_id': None,
            'end_snap_id': None,
            'begin_time': None,
            'end_time': None,
            'elapsed_time': 0,  # in seconds
            'db_time': 0,  # in seconds
        }

        # Look for snapshot information in tables
        for table in self.soup.find_all('table'):
            rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all(['td', 'th'])
                row_text = ' '.join([clean_text(cell.get_text()) for cell in cells])

                if 'Begin Snap' in row_text or 'Snap Id' in row_text:
                    # Extract snap IDs and times
                    for i, cell in enumerate(cells):
                        text = clean_text(cell.get_text())

                        # Try to parse as datetime
                        try:
                            # Common format: 01-Jan-25 10:00:00
                            if '-' in text and ':' in text:
                                # This might be a timestamp
                                parsed_time = self._parse_datetime(text)
                                if parsed_time:
                                    if not snapshot_info['begin_time']:
                                        snapshot_info['begin_time'] = parsed_time
                                    else:
                                        snapshot_info['end_time'] = parsed_time
                        except:
                            pass

                        # Try to parse as snap ID
                        if text.isdigit():
                            snap_id = int(text)
                            if not snapshot_info['begin_snap_id']:
                                snapshot_info['begin_snap_id'] = snap_id
                            else:
                                snapshot_info['end_snap_id'] = snap_id

                # Look for Elapsed time
                if 'Elapsed' in row_text:
                    for cell in cells:
                        text = clean_text(cell.get_text())
                        if ':' in text:  # Time format
                            elapsed_seconds = parse_value(text)
                            if elapsed_seconds > 0:
                                snapshot_info['elapsed_time'] = elapsed_seconds

                # Look for DB Time
                if 'DB Time' in row_text and 'DB CPU' not in row_text:
                    for cell in cells:
                        text = clean_text(cell.get_text())
                        if ':' in text:  # Time format
                            db_time_seconds = parse_value(text)
                            if db_time_seconds > 0:
                                snapshot_info['db_time'] = db_time_seconds

        logger.debug(f"Snapshot info: {snapshot_info}")
        return snapshot_info

    def _parse_load_profile(self) -> Dict[str, Any]:
        """Parse Load Profile section"""
        logger.debug("Parsing Load Profile")

        load_profile = {}

        # Find Load Profile table
        table = self._find_table_by_header("Load Profile")

        if not table:
            logger.warning("Load Profile table not found")
            return load_profile

        rows = table.find_all('tr')

        for row in rows[1:]:  # Skip header
            cells = row.find_all(['td', 'th'])

            if len(cells) >= 3:
                metric_name = clean_text(cells[0].get_text())
                per_second = parse_value(cells[1].get_text())
                per_txn = parse_value(cells[2].get_text())

                if metric_name:
                    load_profile[metric_name] = {
                        'per_second': per_second,
                        'per_txn': per_txn
                    }

        logger.debug(f"Parsed {len(load_profile)} load profile metrics")
        return load_profile

    def _parse_wait_events(self) -> Dict[str, Any]:
        """Parse Top Wait Events"""
        logger.debug("Parsing wait events")

        wait_events = {
            'events': []
        }

        # Find Top 5 Timed Events or similar
        table = self._find_table_by_header("Top")
        if not table:
            table = self._find_table_by_header("Wait Events")

        if not table:
            logger.warning("Wait events table not found")
            return wait_events

        rows = table.find_all('tr')

        # Find header row to identify columns
        header_row = rows[0] if rows else None
        if not header_row:
            return wait_events

        headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]

        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])

            if len(cells) >= 3:
                event = {
                    'name': clean_text(cells[0].get_text()),
                    'waits': 0,
                    'time_waited': 0,
                    'avg_wait': 0,
                    'pct_db_time': 0
                }

                # Parse values based on available columns
                for i, cell in enumerate(cells[1:], 1):
                    if i < len(cells):
                        value = parse_value(cell.get_text())

                        # Map to appropriate field
                        if i == 1:
                            event['waits'] = value
                        elif i == 2:
                            event['time_waited'] = value
                        elif i == 3:
                            event['avg_wait'] = value
                        elif 'DB Time' in headers[i] if i < len(headers) else False:
                            event['pct_db_time'] = value

                if event['name']:
                    wait_events['events'].append(event)

        logger.debug(f"Parsed {len(wait_events['events'])} wait events")
        return wait_events

    def _parse_top_sql(self) -> Dict[str, Any]:
        """Parse Top SQL statistics"""
        logger.debug("Parsing Top SQL")

        top_sql = {
            'by_cpu': [],
            'by_elapsed': [],
            'by_gets': [],
            'by_reads': [],
            'by_executions': []
        }

        # Find SQL sections
        sql_sections = [
            ('SQL ordered by CPU', 'by_cpu'),
            ('SQL ordered by Elapsed', 'by_elapsed'),
            ('SQL ordered by Gets', 'by_gets'),
            ('SQL ordered by Reads', 'by_reads'),
            ('SQL ordered by Executions', 'by_executions'),
        ]

        for section_name, key in sql_sections:
            table = self._find_table_by_header(section_name)

            if table:
                sql_list = self._parse_sql_table(table)
                top_sql[key] = sql_list
                logger.debug(f"Parsed {len(sql_list)} SQL statements for {section_name}")

        return top_sql

    def _parse_sql_table(self, table) -> list:
        """Parse a SQL statistics table"""
        sql_list = []

        rows = table.find_all('tr')

        if len(rows) < 2:
            return sql_list

        # Get headers
        header_row = rows[0]
        headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]

        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])

            if len(cells) >= 2:
                sql_data = {}

                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header = headers[i]
                        value_text = clean_text(cell.get_text())

                        # Keep SQL ID and text as strings
                        if 'SQL Id' in header or 'SQL Text' in header:
                            sql_data[header] = value_text
                        else:
                            sql_data[header] = parse_value(value_text)

                if sql_data:
                    sql_list.append(sql_data)

        return sql_list[:10]  # Top 10

    def _parse_datetime(self, text: str) -> datetime:
        """Parse datetime from AWR report format"""
        try:
            # Try common formats
            formats = [
                '%d-%b-%y %H:%M:%S',  # 01-Jan-25 10:00:00
                '%d-%b-%Y %H:%M:%S',  # 01-Jan-2025 10:00:00
                '%Y-%m-%d %H:%M:%S',  # 2025-01-01 10:00:00
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(text, fmt)
                except:
                    continue

        except Exception as e:
            logger.debug(f"Failed to parse datetime '{text}': {e}")

        return None
