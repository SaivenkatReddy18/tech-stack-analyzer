from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.main import run_pipeline

app = FastAPI(
    title="Tech Stack Trend Analyzer API",
    description="Real-time tech trend analytics from GitHub, Stack Overflow, and Hacker News",
    version="1.0.0"
)

# CORS - allow all origins (safe for public API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store latest metrics in memory
latest_metrics = None
last_update = None

@app.on_event("startup")
async def startup_event():
    """Fetch metrics on startup"""
    global latest_metrics, last_update
    print("[API] Starting up, fetching initial data...")
    latest_metrics = run_pipeline()
    last_update = datetime.now()
    print("[API] Ready to serve requests")

@app.get("/")
def root():
    """Root endpoint with API info"""
    return {
        "message": "Tech Stack Trend Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "trends": "/trends - Get all tech trends",
            "trends/{tech}": "/trends/{tech} - Get specific tech trend",
            "top": "/top - Get top 5 technologies",
            "health": "/health - API health check",
            "docs": "/docs - Interactive API documentation"
        },
        "last_update": last_update.isoformat() if last_update else None
    }

@app.get("/trends")
def get_trends(sort_by: str = Query("momentum_score", enum=["momentum_score", "github_stars_gained", "stackoverflow_questions", "hn_mentions"])):
    """Get all technologies with trends, sorted by specified metric"""
    if latest_metrics is None:
        return {"status": "error", "message": "Data not available yet"}
    
    sorted_df = latest_metrics.sort_values(sort_by, ascending=False)
    
    return {
        "status": "success",
        "count": len(sorted_df),
        "last_update": last_update.isoformat(),
        "data": sorted_df.to_dict('records')
    }

@app.get("/trends/{tech_name}")
def get_tech_trend(tech_name: str):
    """Get specific technology trend details"""
    if latest_metrics is None:
        return {"status": "error", "message": "Data not available yet"}
    
    tech = tech_name.lower()
    result = latest_metrics[latest_metrics['tech_name'] == tech]
    
    if result.empty:
        return {
            "status": "not_found",
            "message": f"No data for {tech_name}",
            "available_techs": latest_metrics['tech_name'].unique().tolist()
        }
    
    row = result.iloc[0]
    
    return {
        "status": "success",
        "tech_name": tech_name,
        "data": {
            "github_stars_gained": int(row['github_stars_gained']),
            "stackoverflow_questions": int(row['stackoverflow_questions']),
            "hn_mentions": int(row['hn_mentions']),
            "momentum_score": float(row['momentum_score']),
            "metric_date": row['metric_date'].isoformat()
        },
        "interpretation": interpret_trend(row)
    }

@app.get("/top")
def get_top_technologies(limit: int = Query(5, ge=1, le=10)):
    """Get top N technologies by momentum score"""
    if latest_metrics is None:
        return {"status": "error", "message": "Data not available yet"}
    
    top_df = latest_metrics.nlargest(limit, 'momentum_score')
    
    return {
        "status": "success",
        "count": len(top_df),
        "last_update": last_update.isoformat(),
        "rankings": [
            {
                "rank": i + 1,
                "tech_name": row['tech_name'],
                "momentum_score": float(row['momentum_score']),
                "github_stars": int(row['github_stars_gained']),
                "stackoverflow_activity": int(row['stackoverflow_questions']),
                "hacker_news_mentions": int(row['hn_mentions'])
            }
            for i, (_, row) in enumerate(top_df.iterrows())
        ]
    }

@app.get("/health")
def health_check():
    """API health check"""
    return {
        "status": "healthy" if latest_metrics is not None else "initializing",
        "last_update": last_update.isoformat() if last_update else None,
        "timestamp": datetime.now().isoformat()
    }

def interpret_trend(row):
    """Generate human-readable interpretation of trend"""
    tech = row['tech_name']
    momentum = float(row['momentum_score'])
    gh_stars = int(row['github_stars_gained'])
    so_questions = int(row['stackoverflow_questions'])
    hn_mentions = int(row['hn_mentions'])
    
    interpretations = []
    
    if gh_stars > 1000:
        interpretations.append(f"Strong GitHub activity ({gh_stars:,} stars)")
    
    if so_questions > 100000:
        interpretations.append(f"Huge Stack Overflow community ({so_questions:,} questions)")
    elif so_questions > 50000:
        interpretations.append(f"Mature Stack Overflow presence ({so_questions:,} questions)")
    
    if hn_mentions > 10:
        interpretations.append(f"Trending on Hacker News ({hn_mentions} mentions)")
    elif hn_mentions > 5:
        interpretations.append(f"Notable Hacker News interest ({hn_mentions} mentions)")
    
    if momentum > 5000:
        interpretations.append("🔥 Explosive momentum")
    elif momentum > 2000:
        interpretations.append("📈 Strong upward trend")
    elif momentum > 500:
        interpretations.append("→ Stable popularity")
    else:
        interpretations.append("📊 Emerging technology")
    
    return " | ".join(interpretations) if interpretations else "Niche technology"

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')