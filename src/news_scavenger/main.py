"""Main entry point for news scavenger."""

import argparse
from datetime import datetime
from pathlib import Path

from .collectors import RSSCollector, GameMecaHTMLCollector
from .processor import ArticleProcessor
from .clustering import EventClusterer
from .output import TrendFormatter


# This Is Game RSS feed URL
THIS_IS_GAME_RSS = "http://thisisgame.com/main/RSS.php"


def main():
    """Run the news scavenger pipeline."""
    parser = argparse.ArgumentParser(
        description="일일 AI·게임 뉴스 트렌드 수집 시스템"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="trends.json",
        help="출력 파일 경로 (기본값: trends.json)"
    )
    parser.add_argument(
        "--top-n",
        "-n",
        type=int,
        default=10,
        help="상위 N개 트렌드 출력 (기본값: 10)"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="수집할 기사의 시간 범위 (기본값: 24시간)"
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=100,
        help="수집할 최대 기사 수 (기본값: 100)"
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.3,
        help="이벤트 클러스터링 유사도 임계값 (기본값: 0.3)"
    )
    parser.add_argument(
        "--no-topic-filter",
        action="store_true",
        help="주제 필터 비활성화"
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["tig-rss", "gamemeca"],
        default="gamemeca",
        help="뉴스 소스 선택 (기본값: gamemeca)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("일일 AI·게임 뉴스 트렌드 수집 시스템")
    print("=" * 80)
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"뉴스 소스: {args.source}")
    print(f"수집 범위: 최근 {args.hours}시간")
    print(f"최대 기사: {args.max_articles}건")
    print()

    # Step 1: Collect articles
    print("[1/5] 기사 수집 중...")
    if args.source == "gamemeca":
        collector = GameMecaHTMLCollector("GameMeca", category="industry")
    else:  # tig-rss
        collector = RSSCollector("This Is Game", THIS_IS_GAME_RSS)

    articles = collector.fetch_articles(
        max_articles=args.max_articles,
        hours_back=args.hours
    )
    print(f"수집 완료: {len(articles)}건")

    if not articles:
        print("수집된 기사가 없습니다.")
        return

    # Step 2: Process articles (filter and deduplicate)
    print("\n[2/5] 기사 처리 중 (필터링 및 중복 제거)...")
    processor = ArticleProcessor(
        enable_topic_filter=not args.no_topic_filter
    )
    articles = processor.process(articles)
    print(f"처리 완료: {len(articles)}건")

    if not articles:
        print("필터링 후 남은 기사가 없습니다.")
        return

    # Step 3: Cluster articles into events
    print("\n[3/5] 이벤트 클러스터링 중...")
    clusterer = EventClusterer(
        similarity_threshold=args.similarity_threshold
    )
    clusters = clusterer.cluster(articles)
    print(f"클러스터링 완료: {len(clusters)}개 이벤트")

    # Step 4: Format top trends
    print(f"\n[4/5] 상위 {args.top_n}개 트렌드 생성 중...")
    formatter = TrendFormatter()
    trends = formatter.format_top_trends(clusters, top_n=args.top_n)
    print(f"트렌드 생성 완료: {len(trends)}개")

    # Step 5: Output results
    print(f"\n[5/5] 결과 저장 중: {args.output}")
    json_output = formatter.to_json(trends)

    output_path = Path(args.output)
    output_path.write_text(json_output, encoding="utf-8")
    print(f"저장 완료: {output_path.absolute()}")

    # Print summary
    formatter.print_summary(trends)


if __name__ == "__main__":
    main()
