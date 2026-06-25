import psycopg
from psycopg import sql
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class PostgresLoader:
    """Load metrics to PostgreSQL database"""
    
    def __init__(self, db_url):
        self.db_url = db_url
    
    def get_connection(self):
        """Create database connection"""
        try:
            conn = psycopg.connect(self.db_url)
            return conn
        except Exception as e:
            print(f"[Loader] ✗ Connection failed: {str(e)}")
            return None
    
    def load_metrics(self, df):
        """Load tech metrics to PostgreSQL"""
        if df.empty:
            print("[Loader] No data to load")
            return 0
        
        conn = self.get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            print(f"[Loader] Loading {len(df)} records...")
            
            # Group by tech_name and metric_date
            grouped = df.groupby(['tech_name', 'metric_date']).first().reset_index()
            
            records_inserted = 0
            
            for _, row in grouped.iterrows():
                try:
                    cursor.execute("""
                        INSERT INTO tech_metrics 
                        (tech_name, metric_date, github_repo_count, github_stars_gained, stackoverflow_questions)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (tech_name, metric_date) 
                        DO UPDATE SET
                            github_repo_count = EXCLUDED.github_repo_count,
                            github_stars_gained = EXCLUDED.github_stars_gained,
                            stackoverflow_questions = EXCLUDED.stackoverflow_questions
                    """, (
                        row.get('tech_name'),
                        row.get('metric_date'),
                        row.get('github_repo_count'),
                        row.get('github_stars_gained'),
                        row.get('stackoverflow_questions')
                    ))
                    records_inserted += 1
                
                except Exception as e:
                    print(f"  ✗ Error inserting {row.get('tech_name')}: {str(e)}")
            
            conn.commit()
            print(f"[Loader] ✓ Loaded {records_inserted} records successfully")
            
            # Log the pipeline run
            self.log_pipeline_run('success', len(df), records_inserted, conn)
            
            cursor.close()
            conn.close()
            
            return records_inserted
        
        except Exception as e:
            print(f"[Loader] ✗ Error: {str(e)}")
            self.log_pipeline_run('failed', 0, 0, conn, str(e))
            return 0
    
    def log_pipeline_run(self, status, fetched, inserted, conn, error=None):
        """Log pipeline execution"""
        try:
            if not conn:
                conn = self.get_connection()
                close_conn = True
            else:
                close_conn = False
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pipeline_logs 
                (source_name, records_fetched, records_inserted, pipeline_status, error_message)
                VALUES (%s, %s, %s, %s, %s)
            """, ('api_extractors', fetched, inserted, status, error))
            conn.commit()
            
            if close_conn:
                cursor.close()
                conn.close()
        
        except Exception as e:
            print(f"[Logger] Error: {str(e)}")


# Test
if __name__ == '__main__':
    import sys
    import os
    
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from extractors.github_extractor import GitHubExtractor
    from extractors.stackoverflow_extractor import StackOverflowExtractor
    
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("✗ DATABASE_URL not set in .env")
        exit(1)
    
    # Fetch data
    print("\n[TEST] Fetching GitHub data...")
    github = GitHubExtractor()
    github_df = github.fetch_trending_repos()
    
    print("\n[TEST] Fetching Stack Overflow data...")
    so = StackOverflowExtractor()
    so_df = so.fetch_tag_metrics()
    
    # Merge
    print("\n[TEST] Merging data...")
    metrics_df = pd.merge(
        github_df[['tech_name', 'metric_date', 'github_repo_count', 'github_stars_gained']],
        so_df[['tech_name', 'metric_date', 'stackoverflow_questions']],
        on=['tech_name', 'metric_date'],
        how='outer'
    )
    
    print(f"\n=== Merged Data ({len(metrics_df)} rows) ===")
    print(metrics_df.head())
    
    # Load to database
    print("\n[TEST] Loading to Supabase...")
    loader = PostgresLoader(db_url)
    loaded = loader.load_metrics(metrics_df)
    print(f"\n✓ Successfully loaded {loaded} records to Supabase")