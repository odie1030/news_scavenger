"""Article processing: filtering and deduplication."""

import re
from typing import List, Set
from .models import Article


class ArticleProcessor:
    """Processes articles: filters and deduplicates."""

    # AI/게임 관련 키워드 (주제 필터용)
    TOPIC_KEYWORDS = [
        "AI", "인공지능", "게임", "모바일", "출시", "업데이트",
        "매출", "규제", "소송", "시장", "이슈", "e스포츠",
        "게이머", "플레이", "콘솔", "PC", "RPG", "MMORPG",
        "넥슨", "엔씨소프트", "크래프톤", "넷마블", "스마일게이트"
    ]

    def __init__(self, enable_topic_filter: bool = True):
        """
        Initialize processor.

        Args:
            enable_topic_filter: Whether to filter articles by topic keywords
        """
        self.enable_topic_filter = enable_topic_filter

    def process(self, articles: List[Article]) -> List[Article]:
        """
        Process articles: filter and deduplicate.

        Args:
            articles: List of articles to process

        Returns:
            Filtered and deduplicated list of articles
        """
        # Apply topic filter if enabled
        if self.enable_topic_filter:
            articles = self._filter_by_topic(articles)

        # Deduplicate by URL
        articles = self._deduplicate_by_url(articles)

        # Deduplicate by normalized title
        articles = self._deduplicate_by_title(articles)

        return articles

    def _filter_by_topic(self, articles: List[Article]) -> List[Article]:
        """
        Filter articles that contain AI/game related keywords.

        Args:
            articles: List of articles

        Returns:
            Filtered list of articles
        """
        filtered = []
        for article in articles:
            if self._has_topic_keyword(article.title):
                filtered.append(article)

        return filtered

    def _has_topic_keyword(self, text: str) -> bool:
        """
        Check if text contains any topic keyword.

        Args:
            text: Text to check

        Returns:
            True if text contains at least one topic keyword
        """
        text_lower = text.lower()
        for keyword in self.TOPIC_KEYWORDS:
            if keyword.lower() in text_lower:
                return True
        return False

    def _deduplicate_by_url(self, articles: List[Article]) -> List[Article]:
        """
        Remove duplicate articles by URL.

        Args:
            articles: List of articles

        Returns:
            Deduplicated list of articles
        """
        seen_urls: Set[str] = set()
        unique_articles = []

        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles

    def _deduplicate_by_title(self, articles: List[Article]) -> List[Article]:
        """
        Remove duplicate articles by normalized title.

        Args:
            articles: List of articles

        Returns:
            Deduplicated list of articles
        """
        seen_titles: Set[str] = set()
        unique_articles = []

        for article in articles:
            normalized_title = self._normalize_title(article.title)
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)

        return unique_articles

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison.

        Removes special characters, extra whitespace, and converts to lowercase.

        Args:
            title: Original title

        Returns:
            Normalized title
        """
        # Remove special characters except Korean, alphanumeric, and spaces
        title = re.sub(r'[^\w\s가-힣]', '', title)

        # Remove extra whitespace
        title = ' '.join(title.split())

        # Convert to lowercase
        title = title.lower()

        return title
