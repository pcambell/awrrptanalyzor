"""Oracle Version Detector"""

import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def detect_oracle_version(html_content: str) -> str:
    """
    Detect Oracle version from AWR HTML report

    Args:
        html_content: AWR report HTML string

    Returns:
        Version string (e.g., "19.3.0", "12.2.0", "11.2.0")
    """
    soup = BeautifulSoup(html_content, 'lxml')

    # Strategy 1: Look for explicit version/release information
    for tag in soup.find_all(['td', 'th', 'p', 'div']):
        text = tag.get_text()

        # Pattern: Release 19.3.0.0.0 or Version 12.2.0.1.0
        match = re.search(r'Release\s+(\d+\.\d+\.\d+)', text, re.IGNORECASE)
        if match:
            version = match.group(1)
            logger.info(f"Detected Oracle version: {version}")
            return version

        match = re.search(r'Version\s+(\d+\.\d+\.\d+)', text, re.IGNORECASE)
        if match:
            version = match.group(1)
            logger.info(f"Detected Oracle version: {version}")
            return version

    # Strategy 2: Look for version-specific features
    full_text = soup.get_text()

    # Check for 19c features
    if 'Pluggable Database' in full_text or 'PDB' in full_text:
        if 'Automatic Indexing' in full_text or 'Real-Time Statistics' in full_text:
            logger.info("Detected Oracle 19c based on features")
            return "19.0.0"

    # Check for 12c features
    if 'Multitenant' in full_text or 'Container Database' in full_text:
        logger.info("Detected Oracle 12c based on features")
        return "12.2.0"

    # Check for 11g features
    if 'Automatic Workload Repository' in full_text:
        # 11g is the oldest supported version
        logger.info("Detected Oracle 11g based on features")
        return "11.2.0"

    # Default to 19c if cannot determine
    logger.warning("Could not determine Oracle version, defaulting to 19c")
    return "19.0.0"
