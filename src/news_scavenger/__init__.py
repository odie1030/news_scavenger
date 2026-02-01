"""News Scavenger - AI & Game news trend collection system."""

from .models import Article, EventCluster, TrendOutput
from .collectors import RSSCollector
from .processor import ArticleProcessor
from .clustering import EventClusterer
from .output import TrendFormatter

__version__ = "0.1.0"

__all__ = [
    "Article",
    "EventCluster",
    "TrendOutput",
    "RSSCollector",
    "ArticleProcessor",
    "EventClusterer",
    "TrendFormatter",
]
