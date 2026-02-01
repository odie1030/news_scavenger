"""GameMeca HTML collector for scraping news articles."""

from typing import List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

from .base_collector import BaseCollector
from .html_utils import parse_korean_date, normalize_url, extract_text_safe
from ..models import Article


class GameMecaHTMLCollector(BaseCollector):
    """Collector for GameMeca news articles using HTML scraping."""

    BASE_URL = "https://www.gamemeca.com"
    NEWS_URL = "https://www.gamemeca.com/news.php"

    CATEGORIES = {
        "industry": "I",  # 산업 뉴스
        "online": "O",    # 온라인 게임
        "pc": "P",        # PC 게임
        "mobile": "M",    # 모바일 게임
    }

    def __init__(self, source_name: str = "GameMeca", category: str = "industry"):
        """Initialize GameMeca collector.

        Args:
            source_name: Name of the source (default: "GameMeca")
            category: News category to fetch (default: "industry")
        """
        super().__init__(source_name)
        self.category = category

    def fetch_articles(self, max_articles: int = 100, hours_back: int = 24) -> List[Article]:
        """Fetch articles from GameMeca news page.

        Args:
            max_articles: Maximum number of articles to fetch
            hours_back: Only fetch articles from the last N hours

        Returns:
            List of Article objects
        """
        articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        # Build URL with category parameter
        category_code = self.CATEGORIES.get(self.category, "I")
        url = f"{self.NEWS_URL}?ca={category_code}"

        page = 1
        should_continue = True

        while should_continue and len(articles) < max_articles:
            # Add pagination parameter for pages beyond the first
            page_url = url if page == 1 else f"{url}&p={page}"

            try:
                response = self._make_request(page_url)
                soup = BeautifulSoup(response.text, "lxml")

                # Parse articles from current page
                page_articles = self._parse_page(soup, cutoff_time)

                if not page_articles:
                    # No more articles found, stop pagination
                    should_continue = False
                    break

                # Check if we've gone past the time window
                if page_articles and page_articles[-1].published_at < cutoff_time:
                    # Filter out articles older than cutoff
                    page_articles = [a for a in page_articles if a.published_at >= cutoff_time]
                    articles.extend(page_articles)
                    should_continue = False
                else:
                    articles.extend(page_articles)

                page += 1

            except Exception as e:
                print(f"Warning: Failed to fetch page {page}: {e}")
                should_continue = False

        # Limit to max_articles
        articles = articles[:max_articles]

        # Fetch view counts for each article
        print(f"조회수 수집 중... ({len(articles)}건)")
        for i, article in enumerate(articles):
            view_count = self._fetch_view_count(article.url)
            article.view_count = view_count
            if (i + 1) % 5 == 0:
                print(f"  {i + 1}/{len(articles)} 완료")

        return articles

    def _parse_page(self, soup: BeautifulSoup, cutoff_time: datetime) -> List[Article]:
        """Parse articles from a single page.

        Args:
            soup: BeautifulSoup object of the page
            cutoff_time: Minimum publish time for articles

        Returns:
            List of Article objects from this page
        """
        articles = []

        # Find article list container
        # GameMeca typically uses a list structure for articles
        # We'll try multiple selectors to find the right one
        article_elements = []

        # Try common patterns for article lists
        selectors = [
            "ul.list_news li",  # Primary selector for GameMeca
            "div.news_list li",
            "ul.news_list li",
            "div.list_article li",
            "ul.list_article li",
            "div.article_list li",
            "tr.article",  # Sometimes in table format
        ]

        for selector in selectors:
            article_elements = soup.select(selector)
            if article_elements:
                break

        # If no specific list found, try finding all links to view.php
        if not article_elements:
            article_links = soup.find_all("a", href=re.compile(r"/view\.php\?gid=\d+"))
            for link in article_links:
                article = self._parse_article_from_link(link)
                if article and article.published_at >= cutoff_time:
                    articles.append(article)
            return articles

        # Parse each article element
        for element in article_elements:
            article = self._parse_article_element(element)
            if article:
                articles.append(article)

        return articles

    def _parse_article_element(self, element) -> Optional[Article]:
        """Parse a single article from HTML element.

        Args:
            element: BeautifulSoup element containing article info

        Returns:
            Article object or None if parsing fails
        """
        try:
            # Find title link in <strong class="tit_thumb"><a>
            # This is the primary way to get the article title and URL
            title_strong = element.find("strong", class_="tit_thumb")
            if title_strong:
                title_link = title_strong.find("a", href=re.compile(r"/view\.php\?gid=\d+"))
            else:
                # Fallback: find any link to view.php
                title_link = element.find("a", href=re.compile(r"/view\.php\?gid=\d+"))

            if not title_link:
                return None

            # Extract URL
            relative_url = title_link.get("href")
            if not relative_url:
                return None
            url = normalize_url(relative_url, self.BASE_URL)

            # Extract title
            title = extract_text_safe(title_link)
            if not title:
                return None

            # Extract date from <div class="day_news">
            date_div = element.find("div", class_="day_news")
            published_at = None

            if date_div:
                date_str = extract_text_safe(date_div)
                published_at = parse_korean_date(date_str)

            # Fallback: look for date pattern anywhere in element
            if not published_at:
                date_pattern = r"\d{4}\.\d{1,2}\.\d{1,2}\s+\d{1,2}:\d{1,2}"
                element_text = element.get_text()
                date_match = re.search(date_pattern, element_text)

                if date_match:
                    date_str = date_match.group(0)
                    published_at = parse_korean_date(date_str)

            # If date parsing failed, use current time as fallback
            if not published_at:
                published_at = datetime.now()

            return Article(
                title=title,
                url=url,
                published_at=published_at,
                source=self.source_name
            )

        except Exception as e:
            # Skip articles that fail to parse
            return None

    def _parse_article_from_link(self, link) -> Optional[Article]:
        """Parse article from a direct link element.

        Args:
            link: BeautifulSoup link element

        Returns:
            Article object or None if parsing fails
        """
        try:
            # Extract URL
            relative_url = link.get("href")
            if not relative_url:
                return None
            url = normalize_url(relative_url, self.BASE_URL)

            # Extract title
            title_elem = link.find("strong")
            if title_elem:
                title = extract_text_safe(title_elem)
            else:
                title = extract_text_safe(link)

            if not title:
                return None

            # Try to find date in parent or sibling elements
            parent = link.parent
            published_at = None

            if parent:
                date_pattern = r"\d{4}\.\d{1,2}\.\d{1,2}\s+\d{1,2}:\d{1,2}"
                parent_text = parent.get_text()
                date_match = re.search(date_pattern, parent_text)

                if date_match:
                    date_str = date_match.group(0)
                    published_at = parse_korean_date(date_str)

            # Fallback to current time
            if not published_at:
                published_at = datetime.now()

            return Article(
                title=title,
                url=url,
                published_at=published_at,
                source=self.source_name
            )

        except Exception:
            return None

    def _fetch_view_count(self, url: str) -> Optional[int]:
        """Fetch view count from article detail page.

        Args:
            url: Article URL

        Returns:
            View count or None if parsing fails
        """
        try:
            response = self._make_request(url)
            soup = BeautifulSoup(response.text, "lxml")

            # Look for "게임메카 / 제휴처 통합 XXX,XXX View" pattern
            page_text = soup.get_text()

            # Pattern: "통합" followed by number with commas, then "View"
            view_pattern = r"통합\s+([\d,]+)\s*View"
            match = re.search(view_pattern, page_text)

            if match:
                view_str = match.group(1).replace(",", "")
                return int(view_str)

            return None

        except Exception:
            return None
