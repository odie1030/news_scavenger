"""Data models for news articles and trends."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Article:
    """Represents a single news article."""

    title: str
    url: str
    published_at: datetime
    source: str = ""

    def __hash__(self):
        """Hash based on URL for deduplication."""
        return hash(self.url)

    def __eq__(self, other):
        """Equality based on URL."""
        if not isinstance(other, Article):
            return False
        return self.url == other.url


@dataclass
class EventCluster:
    """Represents a cluster of articles about the same event."""

    articles: List[Article]
    representative_headline: str = ""

    @property
    def frequency(self) -> int:
        """Number of articles in this cluster."""
        return len(self.articles)

    def __post_init__(self):
        """Set representative headline if not provided."""
        if not self.representative_headline and self.articles:
            # Use the earliest article's title as representative
            self.representative_headline = min(
                self.articles,
                key=lambda a: a.published_at
            ).title


@dataclass
class TrendOutput:
    """Represents the final trend output."""

    rank: int
    headline: str
    articles: List[Article]
