"""Output formatting for trends."""

import json
from typing import List
from datetime import datetime
from .models import EventCluster, TrendOutput


class TrendFormatter:
    """Formats trend data for output."""

    def format_top_trends(
        self,
        clusters: List[EventCluster],
        top_n: int = 10
    ) -> List[TrendOutput]:
        """
        Format top N trends.

        Args:
            clusters: List of event clusters (should be sorted by frequency)
            top_n: Number of top trends to return

        Returns:
            List of TrendOutput objects
        """
        trends = []

        for rank, cluster in enumerate(clusters[:top_n], start=1):
            trend = TrendOutput(
                rank=rank,
                headline=cluster.representative_headline,
                articles=cluster.articles
            )
            trends.append(trend)

        return trends

    def to_json(
        self,
        trends: List[TrendOutput],
        indent: int = 2
    ) -> str:
        """
        Convert trends to JSON string.

        Args:
            trends: List of TrendOutput objects
            indent: JSON indentation level

        Returns:
            JSON string
        """
        data = {
            "generated_at": datetime.now().isoformat(),
            "trends": [
                {
                    "rank": trend.rank,
                    "headline": trend.headline,
                    "frequency": len(trend.articles),
                    "total_views": sum(a.view_count or 0 for a in trend.articles),
                    "articles": [
                        {
                            "title": article.title,
                            "url": article.url,
                            "published_at": article.published_at.isoformat(),
                            "source": article.source,
                            "view_count": article.view_count
                        }
                        for article in trend.articles
                    ]
                }
                for trend in trends
            ]
        }

        return json.dumps(data, ensure_ascii=False, indent=indent)

    def print_summary(self, trends: List[TrendOutput]) -> None:
        """
        Print a human-readable summary of trends.

        Args:
            trends: List of TrendOutput objects
        """
        print("\n" + "=" * 80)
        print(f"일일 AI·게임 뉴스 트렌드 Top {len(trends)}")
        print(f"생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        for trend in trends:
            total_views = sum(a.view_count or 0 for a in trend.articles)
            print(f"\n[{trend.rank}위] {trend.headline}")
            print(f"관련 기사: {len(trend.articles)}건 | 총 조회수: {total_views:,}")

            for idx, article in enumerate(trend.articles[:3], start=1):
                view_str = f" ({article.view_count:,} views)" if article.view_count else ""
                print(f"  {idx}. {article.title[:50]}...{view_str}")
                print(f"     {article.url}")

            if len(trend.articles) > 3:
                print(f"  ... 외 {len(trend.articles) - 3}건")

        print("\n" + "=" * 80)
