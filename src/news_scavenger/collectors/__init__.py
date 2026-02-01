"""Collectors for fetching news articles from various sources."""

from .rss_collector import RSSCollector
from .base_collector import BaseCollector
from .gamemeca_html_collector import GameMecaHTMLCollector

__all__ = ["RSSCollector", "BaseCollector", "GameMecaHTMLCollector"]
