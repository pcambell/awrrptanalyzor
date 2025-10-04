"""Base AWR Parser"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup, Tag
import re
import logging

from app.core.parser.utils import parse_value, clean_text

logger = logging.getLogger(__name__)


class BaseAWRParser(ABC):
    """Base class for AWR parsers"""

    def __init__(self, html_content: str):
        """
        Initialize parser with HTML content

        Args:
            html_content: AWR report HTML string
        """
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, 'lxml')
        self.data: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """
        Main parsing entry point

        Returns:
            Dictionary containing all parsed data
        """
        logger.info("Starting AWR report parsing")

        try:
            self.data = {
                'instance_info': self._parse_instance_info(),
                'snapshot_info': self._parse_snapshot_info(),
                'load_profile': self._parse_load_profile(),
                'wait_events': self._parse_wait_events(),
                'top_sql': self._parse_top_sql(),
                'memory_stats': self._parse_memory_stats(),
                'io_stats': self._parse_io_stats(),
                'instance_efficiency': self._parse_instance_efficiency(),
            }

            logger.info("AWR report parsing completed successfully")
            return self.data

        except Exception as e:
            logger.error(f"Error parsing AWR report: {e}", exc_info=True)
            raise

    @abstractmethod
    def _parse_instance_info(self) -> Dict[str, Any]:
        """Parse instance information (must be implemented by subclasses)"""
        pass

    @abstractmethod
    def _parse_snapshot_info(self) -> Dict[str, Any]:
        """Parse snapshot information (must be implemented by subclasses)"""
        pass

    @abstractmethod
    def _parse_load_profile(self) -> Dict[str, Any]:
        """Parse Load Profile section (must be implemented by subclasses)"""
        pass

    @abstractmethod
    def _parse_wait_events(self) -> Dict[str, Any]:
        """Parse wait events (must be implemented by subclasses)"""
        pass

    @abstractmethod
    def _parse_top_sql(self) -> Dict[str, Any]:
        """Parse Top SQL statistics (must be implemented by subclasses)"""
        pass

    def _parse_memory_stats(self) -> Dict[str, Any]:
        """Parse memory statistics (optional, can be overridden)"""
        logger.debug("Parsing memory statistics")
        return {}

    def _parse_io_stats(self) -> Dict[str, Any]:
        """Parse IO statistics (optional, can be overridden)"""
        logger.debug("Parsing IO statistics")
        return {}

    def _parse_instance_efficiency(self) -> Dict[str, Any]:
        """Parse instance efficiency percentages (optional, can be overridden)"""
        logger.debug("Parsing instance efficiency")
        return {}

    def _find_table_by_header(self, header_text: str, exact: bool = False) -> Optional[Tag]:
        """
        Find table by header text using multiple strategies

        Args:
            header_text: Text to search for in headers
            exact: If True, requires exact match; if False, uses substring match

        Returns:
            BeautifulSoup Tag object for the table, or None if not found
        """
        # Strategy 1: Search in <th> tags
        for th in self.soup.find_all('th'):
            th_text = clean_text(th.get_text())
            if exact:
                if th_text == header_text:
                    return th.find_parent('table')
            else:
                if header_text.lower() in th_text.lower():
                    return th.find_parent('table')

        # Strategy 2: Search in <a> tags with 'name' attribute (anchors)
        for a in self.soup.find_all('a', attrs={'name': True}):
            anchor_name = a['name'].lower()
            if header_text.lower().replace(' ', '') in anchor_name:
                # Find next table after this anchor
                next_table = a.find_next('table')
                if next_table:
                    return next_table

        # Strategy 3: Search in <h2>, <h3>, <b> tags (section headers)
        for tag in self.soup.find_all(['h2', 'h3', 'b']):
            tag_text = clean_text(tag.get_text())
            if header_text.lower() in tag_text.lower():
                next_table = tag.find_next('table')
                if next_table:
                    return next_table

        logger.warning(f"Table not found for header: {header_text}")
        return None

    def _parse_table_to_dict(self, table: Tag, key_col: int = 0, value_col: int = 1) -> Dict[str, Any]:
        """
        Parse a simple key-value table into dictionary

        Args:
            table: BeautifulSoup table Tag
            key_col: Column index for keys (0-based)
            value_col: Column index for values (0-based)

        Returns:
            Dictionary of key-value pairs
        """
        result = {}

        if not table:
            return result

        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all(['td', 'th'])

            if len(cells) > max(key_col, value_col):
                key = clean_text(cells[key_col].get_text())
                value_text = clean_text(cells[value_col].get_text())

                if key:
                    # Try to parse as number, fall back to string
                    result[key] = parse_value(value_text)

        return result

    def _parse_table_to_list(self, table: Tag, skip_header: bool = True) -> list:
        """
        Parse table into list of dictionaries

        Args:
            table: BeautifulSoup table Tag
            skip_header: Whether to skip the first row (header)

        Returns:
            List of dictionaries, each representing a row
        """
        result = []

        if not table:
            return result

        rows = table.find_all('tr')

        if not rows:
            return result

        # Extract headers
        header_row = rows[0]
        headers = [clean_text(th.get_text()) for th in header_row.find_all(['th', 'td'])]

        # Parse data rows
        start_index = 1 if skip_header else 0

        for row in rows[start_index:]:
            cells = row.find_all(['td', 'th'])

            if len(cells) >= len(headers):
                row_data = {}
                for i, header in enumerate(headers):
                    if i < len(cells):
                        cell_text = clean_text(cells[i].get_text())
                        row_data[header] = cell_text

                if row_data:
                    result.append(row_data)

        return result
