"""Data models for news articles and trends."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Article:
    """Represents a single news article."""

    title: str
    url: str
    published_at: datetime
    source: str = ""
    view_count: Optional[int] = None

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

    @property
    def total_views(self) -> int:
        """Total view count of all articles in this cluster."""
        return sum(a.view_count or 0 for a in self.articles)

    @property
    def max_views(self) -> int:
        """Maximum view count among articles in this cluster."""
        views = [a.view_count or 0 for a in self.articles]
        return max(views) if views else 0

    def __post_init__(self):
        """Set representative headline if not provided."""
        if not self.representative_headline and self.articles:
            # Use the article with highest view count as representative
            # Fall back to earliest article if no view counts
            articles_with_views = [a for a in self.articles if a.view_count]
            if articles_with_views:
                self.representative_headline = max(
                    articles_with_views,
                    key=lambda a: a.view_count or 0
                ).title
            else:
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
