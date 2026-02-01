"""Event clustering for grouping related articles."""

import re
from typing import List, Set
from .models import Article, EventCluster


class EventClusterer:
    """Clusters articles by event similarity."""

    def __init__(self, similarity_threshold: float = 0.3):
        """
        Initialize clusterer.

        Args:
            similarity_threshold: Minimum similarity score to cluster articles
                                  (0.0 to 1.0, higher is more strict)
        """
        self.similarity_threshold = similarity_threshold

    def cluster(self, articles: List[Article]) -> List[EventCluster]:
        """
        Cluster articles into events.

        Args:
            articles: List of articles to cluster

        Returns:
            List of event clusters, sorted by frequency (descending)
        """
        if not articles:
            return []

        # Initialize clusters with first article
        clusters: List[List[Article]] = [[articles[0]]]

        # Process remaining articles
        for article in articles[1:]:
            # Find best matching cluster
            best_cluster_idx = -1
            best_similarity = 0.0

            for idx, cluster in enumerate(clusters):
                similarity = self._calculate_cluster_similarity(article, cluster)
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_cluster_idx = idx

            # Add to existing cluster or create new one
            if best_similarity >= self.similarity_threshold:
                clusters[best_cluster_idx].append(article)
            else:
                clusters.append([article])

        # Convert to EventCluster objects
        event_clusters = [
            EventCluster(articles=cluster_articles)
            for cluster_articles in clusters
        ]

        # Sort by frequency (descending)
        event_clusters.sort(key=lambda c: c.frequency, reverse=True)

        return event_clusters

    def _calculate_cluster_similarity(
        self,
        article: Article,
        cluster: List[Article]
    ) -> float:
        """
        Calculate similarity between an article and a cluster.

        Uses maximum similarity with any article in the cluster.

        Args:
            article: Article to compare
            cluster: List of articles in cluster

        Returns:
            Similarity score (0.0 to 1.0)
        """
        max_similarity = 0.0

        for cluster_article in cluster:
            similarity = self._calculate_article_similarity(article, cluster_article)
            max_similarity = max(max_similarity, similarity)

        return max_similarity

    def _calculate_article_similarity(
        self,
        article1: Article,
        article2: Article
    ) -> float:
        """
        Calculate similarity between two articles.

        Uses Jaccard similarity on title tokens.

        Args:
            article1: First article
            article2: Second article

        Returns:
            Similarity score (0.0 to 1.0)
        """
        tokens1 = self._tokenize(article1.title)
        tokens2 = self._tokenize(article2.title)

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity: intersection / union
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _tokenize(self, text: str) -> Set[str]:
        """
        Tokenize text into meaningful tokens.

        Extracts Korean words, English words, and numbers.
        Filters out very short tokens.

        Args:
            text: Text to tokenize

        Returns:
            Set of tokens
        """
        # Extract Korean words (2+ characters), English words, and numbers
        korean_pattern = r'[가-힣]{2,}'
        english_pattern = r'[a-zA-Z]{2,}'
        number_pattern = r'\d+'

        tokens = set()

        # Find Korean words
        tokens.update(re.findall(korean_pattern, text))

        # Find English words
        tokens.update(re.findall(english_pattern, text.lower()))

        # Find numbers
        tokens.update(re.findall(number_pattern, text))

        return tokens
