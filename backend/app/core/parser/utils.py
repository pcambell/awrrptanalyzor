"""Parser Utility Functions"""

import re
from typing import Union, Optional


def parse_value(text: str) -> Union[float, int, str]:
    """
    Parse metric value with units

    Examples:
        "1,234.56" -> 1234.56
        "12.34M" -> 12340000.0
        "99.99%" -> 99.99
        "00:12:34.56" -> 754.56 (seconds)
    """
    if not text or not isinstance(text, str):
        return 0

    text = text.strip()

    # Remove thousand separators
    text = text.replace(',', '')

    # Handle percentage
    if '%' in text:
        try:
            return float(text.replace('%', ''))
        except:
            return 0

    # Handle unit suffixes (K, M, G, T)
    multipliers = {
        'K': 1e3,
        'M': 1e6,
        'G': 1e9,
        'T': 1e12
    }

    for suffix, mult in multipliers.items():
        if text.upper().endswith(suffix):
            try:
                return float(text[:-1]) * mult
            except:
                return 0

    # Handle time format HH:MM:SS or HH:MM:SS.ms
    if ':' in text:
        try:
            parts = text.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
        except:
            return 0

    # Handle regular numbers
    try:
        # Try integer first
        if '.' not in text:
            return int(text)
        else:
            return float(text)
    except:
        return 0


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_sql_id(text: str) -> Optional[str]:
    """Extract SQL ID from text"""
    # SQL ID pattern: 13 characters alphanumeric
    pattern = r'\b([a-z0-9]{13})\b'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None
