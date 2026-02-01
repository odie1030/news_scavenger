# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**News Scavenger** is a daily AI & game industry news trend detection system. It collects articles from Korean game media sources and Naver News, clusters them by event similarity, and produces a Top 10 daily trends report based on mention frequency.

Key characteristics:
- Focus on **trend velocity** (what's being talked about now), not analysis
- Target: Last 24 hours of articles only
- Output: Daily Top 10 trends at 10 AM KST
- No real-time monitoring, sentiment analysis, or dashboards in v1

## Architecture

### Core Components

The system should be organized into these main modules:

1. **Data Collection Layer**
   - RSS feed readers for This Is Game and GameMeca
   - Naver News API client (using official search API)
   - HTML scraping fallback when RSS unavailable
   - Collection limited to max 50-100 articles per keyword

2. **Processing Pipeline**
   - Time filtering (24h window from execution time)
   - Topic filtering (AI/game keyword presence in title/summary)
   - URL-based and normalized-title-based deduplication
   - Collect fields: title, URL, publish_time

3. **Event Clustering Engine**
   - Group articles about the same event using:
     - Title token overlap
     - Common keywords (company names, game titles, product names)
     - Medium similarity threshold (not strict matching)
   - No embeddings or advanced NLP required in v1

4. **Trend Ranking**
   - Sort event clusters by article frequency
   - May consider source diversity internally
   - **Do not** include source count in output

5. **Output Generator**
   - Format: JSON or CSV
   - Structure: Top 10 trends with rank, representative headline, article list (title, URL, timestamp)

### Data Flow

```
Keywords → [RSS/API/Scraping] → Raw Articles
  ↓
Time Filter (24h) → Topic Filter → Deduplication
  ↓
Event Clustering (by title similarity)
  ↓
Frequency Ranking → Top 10
  ↓
JSON/CSV Output
```

## Keywords

Predefined list (query individually):
- AI, 인공지능, 게임, 모바일, 출시, 업데이트, 매출, 규제, 소송, 시장, 이슈

Each keyword is queried separately; duplicate articles across keywords are expected and handled in deduplication.

## Data Sources

### Primary
- **This Is Game (TIG)**: Prefer RSS, fallback to scraping
  - High relevance and reliability for game news

### Secondary
- **GameMeca**: Prefer RSS, fallback to scraping
- **Naver News**: Use official search API for broader coverage

## Execution Schedule

- **Frequency**: Once per day
- **Time**: 10:00 AM KST (UTC+9)
- **Window**: Previous 24 hours from execution time

Implement as scheduled job (cron, systemd timer, cloud scheduler, etc.)

## Korean Text Handling

- All sources and outputs use Korean language
- Ensure proper UTF-8 encoding throughout
- Use Korean-aware text processing for:
  - Tokenization (consider using KoNLPy or similar)
  - Normalization (whitespace, punctuation)
  - Keyword matching

## Technology Considerations

Since no code exists yet, consider:

- **Language**: Python recommended for web scraping, text processing, and simple NLP
- **RSS parsing**: feedparser library
- **HTTP requests**: requests or httpx with rate limiting
- **HTML scraping**: BeautifulSoup4 or scrapy
- **Text similarity**: Simple token overlap (Jaccard, cosine) sufficient for v1
- **Storage**: File-based (JSON) or SQLite for article cache; no complex DB needed initially
- **Scheduling**: cron (Unix) or APScheduler (Python)

## Development Workflow

### Building
No build step needed for Python. If using TypeScript/JavaScript:
```bash
npm install
npm run build
```

### Testing
Structure tests by component:
```bash
pytest tests/                    # All tests
pytest tests/test_collectors.py # Specific module
pytest -k "test_rss"            # Specific pattern
```

### Running
```bash
python main.py                   # Manual execution
python main.py --date 2026-01-31 # Test with specific date
```

## Output Validation

Each trend in the Top 10 must include:
- Rank (1-10)
- Representative headline (most common or earliest)
- List of related articles with:
  - Title
  - URL
  - Publish time (ISO 8601 format)

## Out of Scope for v1

- Real-time monitoring
- Sentiment analysis
- Long-term narrative tracking
- Dashboard/visualization
- Embedding-based semantic analysis

Keep implementation simple and focused on the core clustering and ranking logic.
