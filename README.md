# Tech Stack Trend Analyzer

Real-time technology trend analysis platform that aggregates data from GitHub, Stack Overflow, and Hacker News to identify emerging tech trends and developer sentiment.

## Features

- **GitHub Metrics:** Repository count and star velocity for trending repos (past 7 days)
- **Stack Overflow Activity:** Question volume and community engagement for each tech
- **Hacker News Sentiment:** Mention frequency in top stories (community interest signal)
- **Momentum Score:** Composite metric (40% GitHub + 40% Stack Overflow + 20% HN) for trend ranking
- **REST API:** FastAPI with endpoints for trends, rankings, and detailed tech analysis
- **Live Endpoints:** Deployed on Render with real-time data refresh

## Tech Stack

- **ETL Pipeline:** Python (requests, pandas)
- **API:** FastAPI + Uvicorn
- **Data Sources:** GitHub API, Stack Overflow API, Hacker News API
- **Database:** PostgreSQL (Supabase) - optional integration
- **Deployment:** Render (free tier)

## Local Setup

### Prerequisites
- Python 3.9+
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/SaivenkatReddy18/tech-stack-analyzer.git
cd tech-stack-analyzer

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run pipeline
python pipeline/main.py

# Start API server
python -m uvicorn api.app:app --reload
```

API available at: http://localhost:8000

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and available endpoints |
| `/trends` | GET | All technologies with metrics (sortable) |
| `/trends/{tech_name}` | GET | Detailed trend for specific technology |
| `/top` | GET | Top 5 technologies by momentum score |
| `/health` | GET | API health check |
| `/docs` | GET | Interactive API documentation (Swagger UI) |

## Example Usage

```bash
# Get top 5 technologies
curl https://api.example.com/top

# Get Python trend details
curl https://api.example.com/trends/python

# Get all trends sorted by GitHub activity
curl "https://api.example.com/trends?sort_by=github_stars_gained"
```

## Response Format

```json
{
  "status": "success",
  "count": 10,
  "last_update": "2026-06-24T21:37:32",
  "data": [
    {
      "tech_name": "python",
      "github_stars_gained": 15506,
      "stackoverflow_questions": 2219816,
      "hn_mentions": 2,
      "momentum_score": 6291.59
    }
  ]
}
```

## Project Architecture