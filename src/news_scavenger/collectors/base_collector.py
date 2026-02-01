"""Base collector class for news article collection."""

from abc import ABC, abstractmethod
from typing import List
import time
import requests

from ..models import Article


class BaseCollector(ABC):
    """Abstract base class for article collectors."""

    DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    DEFAULT_TIMEOUT = 10
    REQUEST_DELAY = 1.5  # Seconds between requests for rate limiting

    def __init__(self, source_name: str):
        """Initialize collector with source name.

        Args:
            source_name: Name of the news source
        """
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.DEFAULT_USER_AGENT})
        self._last_request_time = 0

    @abstractmethod
    def fetch_articles(self, max_articles: int = 100, hours_back: int = 24) -> List[Article]:
        """Fetch articles from the news source.

        Args:
            max_articles: Maximum number of articles to fetch
            hours_back: Only fetch articles from the last N hours

        Returns:
            List of Article objects
        """
        pass

    def _make_request(self, url: str, max_retries: int = 3) -> requests.Response:
        """Make HTTP request with retry logic and rate limiting.

        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts

        Returns:
            requests.Response object

        Raises:
            requests.RequestException: If all retry attempts fail
        """
        # Rate limiting: ensure minimum delay between requests
        current_time = time.time()
        time_since_last_request = current_time - self._last_request_time
        if time_since_last_request < self.REQUEST_DELAY:
            time.sleep(self.REQUEST_DELAY - time_since_last_request)

        last_exception = None
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=self.DEFAULT_TIMEOUT)
                response.raise_for_status()
                self._last_request_time = time.time()
                return response
            except requests.RequestException as e:
                last_exception = e
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                continue

        # All retries failed
        raise last_exception
