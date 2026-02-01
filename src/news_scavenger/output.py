"""Output formatting for trends."""

import json
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
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

    def to_markdown(self, trends: List[TrendOutput], source_name: str = "GameMeca") -> str:
        """
        Convert trends to Markdown string.

        Args:
            trends: List of TrendOutput objects
            source_name: Name of the news source

        Returns:
            Markdown string
        """
        lines = []
        now = datetime.now()

        lines.append(f"# {source_name} 뉴스 트렌드")
        lines.append("")
        lines.append(f"**생성 시각**: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**정렬 기준**: 조회수 (높은 순)")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 트렌드 목록")
        lines.append("")
        lines.append("| 순위 | 조회수 | 제목 | 발행일 |")
        lines.append("|:---:|-------:|------|--------|")

        for trend in trends:
            total_views = sum(a.view_count or 0 for a in trend.articles)
            article = trend.articles[0] if trend.articles else None
            if article:
                pub_date = article.published_at.strftime('%m/%d %H:%M')
                title_link = f"[{trend.headline}]({article.url})"
                lines.append(f"| {trend.rank} | {total_views:,} | {title_link} | {pub_date} |")

        lines.append("")
        return "\n".join(lines)


def json_to_markdown(json_path: str, markdown_path: str) -> None:
    """
    Parse JSON file and convert to Markdown format.

    Args:
        json_path: Path to input JSON file
        markdown_path: Path to output Markdown file
    """
    json_file = Path(json_path)
    md_file = Path(markdown_path)

    with json_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    lines = []
    generated_at = data.get("generated_at", datetime.now().isoformat())

    # Parse generated_at to datetime
    try:
        gen_dt = datetime.fromisoformat(generated_at)
        gen_str = gen_dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        gen_str = generated_at

    lines.append("# GameMeca 뉴스 트렌드")
    lines.append("")
    lines.append(f"**생성 시각**: {gen_str}")
    lines.append(f"**정렬 기준**: 조회수 (높은 순)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 트렌드 목록")
    lines.append("")
    lines.append("| 순위 | 조회수 | 제목 | 발행일 |")
    lines.append("|:---:|-------:|------|--------|")

    for trend in data.get("trends", []):
        rank = trend.get("rank", 0)
        total_views = trend.get("total_views", 0)
        headline = trend.get("headline", "")
        articles = trend.get("articles", [])

        if articles:
            first_article = articles[0]
            url = first_article.get("url", "")
            pub_at = first_article.get("published_at", "")
            try:
                pub_dt = datetime.fromisoformat(pub_at)
                pub_str = pub_dt.strftime('%m/%d %H:%M')
            except ValueError:
                pub_str = pub_at[:10] if pub_at else ""

            title_link = f"[{headline}]({url})"
            lines.append(f"| {rank} | {total_views:,} | {title_link} | {pub_str} |")

    lines.append("")

    md_file.parent.mkdir(parents=True, exist_ok=True)
    md_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown 저장 완료: {md_file}")
