import requests
import pandas as pd
from datetime import datetime
import time

class StackOverflowExtractor:
    """Fetch question counts and activity metrics from Stack Overflow API"""
    
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.tags = [
            'python', 'javascript', 'typescript', 'go', 'rust',
            'java', 'c++', 'c#', 'kotlin', 'swift'
        ]
    
    def fetch_tag_metrics(self):
        """Fetch question counts for each tag"""
        print("[Stack Overflow] Fetching tag metrics...")
        tag_data = []
        
        for tag in self.tags:
            try:
                params = {
                    'order': 'desc',
                    'sort': 'popular',
                    'site': 'stackoverflow',
                    'pagesize': 1
                }
                
                response = requests.get(
                    f"{self.base_url}/tags/{tag}/info",
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    items = response.json().get('items', [])
                    if items:
                        item = items[0]
                        tag_data.append({
                            'tech_name': tag,
                            'metric_date': datetime.now().date(),
                            'stackoverflow_questions': item.get('count', 0),
                            'source': 'stackoverflow'
                        })
                        
                        print(f"  ✓ {tag}: {item.get('count', 0):,} questions")
                        time.sleep(0.5)  # Rate limiting
                
                else:
                    print(f"  ✗ {tag}: API error {response.status_code}")
                    time.sleep(1)
            
            except Exception as e:
                print(f"  ✗ {tag}: {str(e)}")
                time.sleep(1)
        
        return pd.DataFrame(tag_data)


# Test
if __name__ == '__main__':
    extractor = StackOverflowExtractor()
    df = extractor.fetch_tag_metrics()
    print("\n=== Stack Overflow Data ===")
    print(df)
    print(f"\nFetched {len(df)} tags")