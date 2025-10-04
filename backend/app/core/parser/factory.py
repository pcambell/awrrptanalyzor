"""AWR Parser Factory"""

import logging
from typing import Type

from app.core.parser.base import BaseAWRParser
from app.core.parser.oracle19c import Oracle19cParser
from app.core.parser.version_detector import detect_oracle_version

logger = logging.getLogger(__name__)


class AWRParserFactory:
    """Factory for creating appropriate AWR parser based on Oracle version"""

    @staticmethod
    def create_parser(html_content: str) -> BaseAWRParser:
        """
        Create appropriate parser based on detected Oracle version

        Args:
            html_content: AWR report HTML string

        Returns:
            Instance of appropriate parser

        Raises:
            ValueError: If unsupported Oracle version
        """
        version = detect_oracle_version(html_content)
        logger.info(f"Creating parser for Oracle version: {version}")

        # Extract major version
        major_version = version.split('.')[0]

        if major_version in ['19', '21', '23']:
            return Oracle19cParser(html_content)
        elif major_version == '12':
            # For now, use 19c parser as 12c has similar structure
            # TODO: Implement dedicated Oracle12cParser
            logger.warning("Using Oracle19cParser for version 12c")
            return Oracle19cParser(html_content)
        elif major_version == '11':
            # TODO: Implement dedicated Oracle11gParser
            logger.warning("Using Oracle19cParser for version 11g")
            return Oracle19cParser(html_content)
        else:
            raise ValueError(f"Unsupported Oracle version: {version}")
