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

### Actual Module Structure

```
src/news_scavenger/
├── __init__.py              # Package initialization
├── main.py                  # Entry point, CLI args, pipeline orchestration
├── models.py                # Article, EventCluster, TrendOutput dataclasses
├── processor.py             # ArticleProcessor (filtering, deduplication)
├── clustering.py            # EventClusterer (Jaccard similarity)
├── output.py                # TrendFormatter (JSON output, console summary)
└── collectors/
    ├── __init__.py
    └── rss_collector.py     # RSSCollector (feedparser wrapper)
```

**Key Files:**
- `main.py:14` - Hardcoded RSS URL (update here to change source)
- `models.py` - Article/EventCluster data structures
- `clustering.py` - Token overlap similarity algorithm
- `processor.py` - Topic filtering keywords defined here

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

## Configuration

**Current Setup (v0.1):**
- RSS URL is hardcoded in `src/news_scavenger/main.py:14`
- Only This Is Game RSS feed is active
- To change RSS source, edit `THIS_IS_GAME_RSS` variable

**Future Configuration:**
- See `config.example.json` for planned config file structure
- Will support multiple sources with per-source settings
- Config file feature not yet implemented

**Verifying RSS URLs:**
```bash
# Test RSS feed manually
uv run python -c "import feedparser; print(feedparser.parse('YOUR_RSS_URL').entries[:3])"
```

## Korean Text Handling

- All sources and outputs use Korean language
- Ensure proper UTF-8 encoding throughout
- Use Korean-aware text processing for:
  - Tokenization (consider using KoNLPy or similar)
  - Normalization (whitespace, punctuation)
  - Keyword matching

## Current Implementation

**Tech Stack:**
- **Language**: Python 3.9+
- **Package Manager**: uv (configured in pyproject.toml)
- **RSS parsing**: feedparser 6.0.12+
- **HTTP requests**: requests 2.32.5+
- **Date handling**: python-dateutil 2.9.0+
- **Text similarity**: Token-based overlap (Jaccard coefficient)
- **Storage**: JSON file output (no database)

**Implementation Status:**
- ✅ RSS collection (This Is Game only)
- ✅ Time filtering and topic filtering
- ✅ Deduplication by URL
- ✅ Event clustering with configurable threshold
- ✅ Top N trend ranking and JSON output
- ⏳ Naver News API (planned)
- ⏳ GameMeca RSS (planned)
- ⏳ HTML scraping fallback (planned)
- ⏳ Scheduling automation (manual cron setup required)

## Development Workflow

**IMPORTANT**: This project uses `uv` for all Python operations. Always prefix Python commands with `uv run` and use `uv` for package management. Never use `pip`, `python`, or `pytest` directly.

### Setup
```bash
# uv is already installed and configured
uv sync                          # Install/sync dependencies
uv pip install <package>         # Add new dependencies
uv pip list                      # List installed packages
```

### Running
```bash
# Run with default settings (collect last 24h, output Top 10)
uv run news-scavenger

# Customize output file
uv run news-scavenger -o output/daily_trends.json

# Adjust parameters
uv run news-scavenger --hours 48 --top-n 20

# Show all options
uv run news-scavenger --help
```

### Common Options
- `--output, -o`: Output file path (default: trends.json)
- `--top-n, -n`: Number of top trends (default: 10)
- `--hours`: Time range in hours (default: 24)
- `--max-articles`: Max articles to collect (default: 100)
- `--similarity-threshold`: Clustering threshold 0.0-1.0 (default: 0.3)
- `--no-topic-filter`: Disable AI/game keyword filtering

### Testing
```bash
# Tests not yet implemented
# To add tests: create tests/ directory and install pytest
# uv pip install pytest
# uv run pytest tests/

# For now, manual testing:
uv run news-scavenger --hours 1 --max-articles 5  # Quick test with small dataset
```

### Running Python Scripts
```bash
# Run a Python script
uv run python script.py

# Run a Python module
uv run python -m module_name

# Interactive Python shell with project dependencies
uv run python
```

## Output Validation

Each trend in the Top 10 must include:
- Rank (1-10)
- Representative headline (most common or earliest)
- List of related articles with:
  - Title
  - URL
  - Publish time (ISO 8601 format)

## Troubleshooting

**No articles collected:**
- Verify RSS URL is accessible: `curl -I <RSS_URL>`
- Check if feed has recent articles (within --hours window)
- Try increasing `--hours` or `--max-articles`

**All articles filtered out:**
- Use `--no-topic-filter` to disable keyword filtering
- Check if topic keywords in `processor.py` match your content

**Korean text encoding issues:**
- Ensure terminal supports UTF-8: `export LANG=en_US.UTF-8`
- Output files are always UTF-8 encoded

**RSS feed parsing errors:**
- Some feeds may have malformed XML - check feedparser warnings
- Hardcoded URL in `main.py:14` may need updating if feed moves

## Out of Scope for v1

- Real-time monitoring
- Sentiment analysis
- Long-term narrative tracking
- Dashboard/visualization
- Embedding-based semantic analysis

Keep implementation simple and focused on the core clustering and ranking logic.
