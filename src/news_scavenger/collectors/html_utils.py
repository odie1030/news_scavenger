"""Utility functions for HTML scraping."""

from datetime import datetime
from typing import Optional
from urllib.parse import urljoin, urlparse
import re


def parse_korean_date(date_str: str) -> Optional[datetime]:
    """Parse Korean date string to datetime object.

    Supports formats:
    - "YYYY.MM.DD HH:MM" (e.g., "2026.02.01 14:30")
    - "YYYY-MM-DD HH:MM"
    - "YYYY.MM.DD"
    - "YYYY-MM-DD"

    Args:
        date_str: Date string to parse

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Pattern 1: YYYY.MM.DD HH:MM
    pattern1 = r"(\d{4})\.(\d{1,2})\.(\d{1,2})\s+(\d{1,2}):(\d{1,2})"
    match = re.match(pattern1, date_str)
    if match:
        year, month, day, hour, minute = match.groups()
        try:
            return datetime(int(year), int(month), int(day), int(hour), int(minute))
        except ValueError:
            pass

    # Pattern 2: YYYY-MM-DD HH:MM
    pattern2 = r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})"
    match = re.match(pattern2, date_str)
    if match:
        year, month, day, hour, minute = match.groups()
        try:
            return datetime(int(year), int(month), int(day), int(hour), int(minute))
        except ValueError:
            pass

    # Pattern 3: YYYY.MM.DD
    pattern3 = r"(\d{4})\.(\d{1,2})\.(\d{1,2})"
    match = re.match(pattern3, date_str)
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            pass

    # Pattern 4: YYYY-MM-DD
    pattern4 = r"(\d{4})-(\d{1,2})-(\d{1,2})"
    match = re.match(pattern4, date_str)
    if match:
        year, month, day = match.groups()
        try:
            return datetime(int(year), int(month), int(day))
        except ValueError:
            pass

    return None


def normalize_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute URL.

    Args:
        url: URL to normalize (can be relative or absolute)
        base_url: Base URL to use for relative URLs

    Returns:
        Absolute URL
    """
    if not url:
        return ""

    # If URL already has a scheme, return as is
    parsed = urlparse(url)
    if parsed.scheme:
        return url

    # Join with base URL
    return urljoin(base_url, url)


def extract_text_safe(element, default: str = "") -> str:
    """Safely extract text from BeautifulSoup element.

    Args:
        element: BeautifulSoup element or None
        default: Default value if element is None or has no text

    Returns:
        Extracted text or default value
    """
    if element is None:
        return default

    text = element.get_text(strip=True)
    return text if text else default
