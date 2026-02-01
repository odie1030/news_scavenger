"""RSS feed collector for news articles."""

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Optional
from dateutil import parser as date_parser

from ..models import Article


class RSSCollector:
    """Collects articles from RSS feeds."""

    def __init__(self, source_name: str, rss_url: str):
        """
        Initialize RSS collector.

        Args:
            source_name: Name of the news source (e.g., "This Is Game")
            rss_url: URL of the RSS feed
        """
        self.source_name = source_name
        self.rss_url = rss_url

    def fetch_articles(
        self,
        max_articles: int = 100,
        hours_back: int = 24
    ) -> List[Article]:
        """
        Fetch articles from RSS feed.

        Args:
            max_articles: Maximum number of articles to fetch
            hours_back: Only fetch articles from this many hours ago

        Returns:
            List of Article objects
        """
        try:
            # Fetch RSS feed with proper headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(self.rss_url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse RSS feed
            feed = feedparser.parse(response.content)

            print(f"DEBUG: Feed 제목: {feed.feed.get('title', 'N/A')}")
            print(f"DEBUG: 총 엔트리 수: {len(feed.entries)}")

            articles = []
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            print(f"DEBUG: 기준 시각: {cutoff_time}")

            for i, entry in enumerate(feed.entries[:max_articles]):
                try:
                    article = self._parse_entry(entry)
                    if article:
                        is_recent = article.published_at >= cutoff_time
                        if i < 3:  # Show details for first 3 entries
                            print(f"DEBUG: Entry {i+1}: {article.title[:50]}...")
                            print(f"  발행 시각: {article.published_at}, 최근 기사? {is_recent}")
                        if is_recent:
                            articles.append(article)
                except Exception as e:
                    print(f"Error parsing entry: {e}")
                    continue

            return articles

        except Exception as e:
            print(f"Error fetching RSS feed from {self.rss_url}: {e}")
            return []

    def _parse_entry(self, entry) -> Optional[Article]:
        """
        Parse a single RSS entry into an Article.

        Args:
            entry: RSS feed entry

        Returns:
            Article object or None if parsing fails
        """
        # Extract title
        title = entry.get("title", "").strip()
        if not title:
            return None

        # Extract URL
        url = entry.get("link", "").strip()
        if not url:
            return None

        # Extract published date
        published_at = self._parse_date(entry)
        if not published_at:
            published_at = datetime.now()

        return Article(
            title=title,
            url=url,
            published_at=published_at,
            source=self.source_name
        )

    def _parse_date(self, entry) -> Optional[datetime]:
        """
        Parse date from RSS entry.

        Args:
            entry: RSS feed entry

        Returns:
            datetime object or None if parsing fails
        """
        # Try different date fields
        date_fields = ["published", "updated", "created"]

        for field in date_fields:
            date_str = entry.get(field)
            if date_str:
                try:
                    return date_parser.parse(date_str)
                except Exception:
                    continue

        # Try parsed date fields
        for field in date_fields:
            parsed_field = f"{field}_parsed"
            if hasattr(entry, parsed_field):
                time_struct = getattr(entry, parsed_field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except Exception:
                        continue

        return None
