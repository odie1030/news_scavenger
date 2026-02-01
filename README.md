# News Scavenger

일일 AI·게임 뉴스 트렌드 수집 시스템

최근 24시간 내 반복적으로 보도된 뉴스 이벤트를 탐지하여 일일 트렌드 Top 10을 도출하는 자동화 시스템입니다.

## 기능

- RSS 피드를 통한 뉴스 수집
- AI/게임 관련 키워드 필터링
- 중복 기사 제거
- 이벤트 클러스터링 (유사 기사 그룹화)
- Top 10 트렌드 출력 (JSON 형식)

## 설치

```bash
# uv 설치 (아직 설치하지 않은 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

## 사용법

```bash
# 기본 실행 (최근 24시간, Top 10)
uv run news-scavenger

# 출력 파일 지정
uv run news-scavenger -o output/trends.json

# 파라미터 조정
uv run news-scavenger --hours 48 --top-n 20

# 모든 옵션 보기
uv run news-scavenger --help
```

## 설정

현재 프로토타입은 하드코딩된 RSS URL을 사용합니다. 실제 사용을 위해서는 다음을 수행해야 합니다:

1. This Is Game의 실제 RSS 피드 URL 확인
2. `src/news_scavenger/main.py`의 `THIS_IS_GAME_RSS` 변수 업데이트
3. 또는 `config.example.json`을 참고하여 설정 파일 기능 구현

## 프로젝트 구조

```
src/news_scavenger/
├── __init__.py           # 패키지 초기화
├── main.py               # 메인 진입점
├── models.py             # 데이터 모델
├── processor.py          # 필터링 및 중복 제거
├── clustering.py         # 이벤트 클러스터링
├── output.py             # 출력 포맷팅
└── collectors/
    ├── __init__.py
    └── rss_collector.py  # RSS 수집기
```

## 개발

자세한 개발 가이드는 [CLAUDE.md](CLAUDE.md)를 참조하세요.

## 다음 단계

- [ ] 실제 RSS URL 확인 및 업데이트
- [ ] Naver News API 통합
- [ ] GameMeca RSS 추가
- [ ] 테스트 코드 작성
- [ ] 스케줄러 설정 (cron 또는 systemd timer)
- [ ] HTML 스크래핑 fallback 구현