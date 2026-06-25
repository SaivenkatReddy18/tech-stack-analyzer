import os
import sys
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.extractors.github_extractor import GitHubExtractor
from pipeline.extractors.stackoverflow_extractor import StackOverflowExtractor
from pipeline.extractors.hackernews_extractor import HackerNewsExtractor

def run_pipeline():
    """Main ETL pipeline - orchestrates all extractors"""
    
    print("="*70)
    print(f"[PIPELINE] Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        # Step 1: Extract from GitHub
        print("\n[STEP 1/3] Extracting GitHub data...")
        github = GitHubExtractor()
        github_df = github.fetch_trending_repos()
        print(f"  ✓ Got {len(github_df)} languages from GitHub")
        
        # Step 2: Extract from Stack Overflow
        print("\n[STEP 2/3] Extracting Stack Overflow data...")
        stackoverflow = StackOverflowExtractor()
        so_df = stackoverflow.fetch_tag_metrics()
        print(f"  ✓ Got {len(so_df)} tags from Stack Overflow")
        
        # Step 3: Extract from Hacker News
        print("\n[STEP 3/3] Extracting Hacker News data...")
        hackernews = HackerNewsExtractor()
        hn_df = hackernews.extract_tech_mentions()
        print(f"  ✓ Got {len(hn_df)} mentions from Hacker News")
        
        # Step 4: Transform - merge all data
        print("\n[TRANSFORM] Merging data from all sources...")
        
        # Merge GitHub + Stack Overflow first
        metrics_df = pd.merge(
            github_df[['tech_name', 'metric_date', 'github_repo_count', 'github_stars_gained']],
            so_df[['tech_name', 'metric_date', 'stackoverflow_questions']],
            on=['tech_name', 'metric_date'],
            how='outer'
        )
        
        # Merge with Hacker News
        if not hn_df.empty:
            metrics_df = pd.merge(
                metrics_df,
                hn_df[['tech_name', 'metric_date', 'hn_mentions']],
                on=['tech_name', 'metric_date'],
                how='left'
            )
        
        # Fill NaN values with 0
        metrics_df = metrics_df.fillna(0)
        
        print(f"  ✓ Merged {len(metrics_df)} records")
        
        # Calculate momentum score (combined metric)
        metrics_df['momentum_score'] = (
            metrics_df['github_stars_gained'] * 0.4 +
            (metrics_df['stackoverflow_questions'] / 10000) * 0.4 +
            metrics_df['hn_mentions'] * 0.2
        )
        
        # Step 5: Display summary
        print("\n" + "="*70)
        print("[SUMMARY] Top Technologies by Momentum")
        print("="*70)
        summary = metrics_df[['tech_name', 'github_stars_gained', 'stackoverflow_questions', 'hn_mentions', 'momentum_score']].copy()
        summary = summary.sort_values('momentum_score', ascending=False)
        print(summary.to_string(index=False))
        
        print("\n" + "="*70)
        print(f"[PIPELINE] Completed successfully!")
        print(f"  - Total records processed: {len(metrics_df)}")
        print(f"  - Data sources: GitHub, Stack Overflow, Hacker News")
        print(f"  - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return metrics_df
    
    except Exception as e:
        print("\n" + "="*70)
        print(f"[PIPELINE] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*70)
        return None

if __name__ == '__main__':
    result_df = run_pipeline()
    if result_df is not None:
        # Save to CSV for debugging
        result_df.to_csv('latest_metrics.csv', index=False)
        print(f"\n✓ Data saved to latest_metrics.csv")