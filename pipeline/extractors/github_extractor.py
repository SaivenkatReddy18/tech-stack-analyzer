import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class GitHubExtractor:
    """Fetch trending repositories and metrics from GitHub API"""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.languages = [
            'python', 'javascript', 'typescript', 'go', 'rust',
            'java', 'c++', 'c#', 'kotlin', 'swift'
        ]
        self.headers = {'Accept': 'application/vnd.github.v3+json'}
    
    def fetch_trending_repos(self):
        """Fetch trending repos from past 7 days"""
        print("[GitHub] Fetching trending repositories...")
        trending_data = []
        
        for lang in self.languages:
            try:
                # Query: repos of language created in last 7 days
                query = f"language:{lang} created:>={(datetime.now() - timedelta(days=7)).date()}"
                params = {
                    'q': query,
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 100
                }
                
                response = requests.get(
                    f"{self.base_url}/search/repositories",
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    repos = data.get('items', [])
                    
                    # Calculate metrics
                    star_gain = sum(r.get('stargazers_count', 0) for r in repos[:50])
                    repo_count = len(repos)
                    
                    trending_data.append({
                        'tech_name': lang,
                        'metric_date': datetime.now().date(),
                        'github_repo_count': repo_count,
                        'github_stars_gained': star_gain,
                        'source': 'github'
                    })
                    
                    print(f"  ✓ {lang}: {repo_count} repos, {star_gain} stars")
                    time.sleep(0.5)  # Rate limiting
                
                else:
                    print(f"  ✗ {lang}: API error {response.status_code}")
                    time.sleep(1)
            
            except Exception as e:
                print(f"  ✗ {lang}: {str(e)}")
                time.sleep(1)
        
        return pd.DataFrame(trending_data)


# Test the extractor
if __name__ == '__main__':
    extractor = GitHubExtractor()
    df = extractor.fetch_trending_repos()
    print("\n=== GitHub Data ===")
    print(df)
    print(f"\nFetched {len(df)} languages")