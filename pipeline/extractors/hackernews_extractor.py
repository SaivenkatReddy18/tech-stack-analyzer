import requests
import pandas as pd
from datetime import datetime
import time
from collections import Counter

class HackerNewsExtractor:
    """Fetch tech mentions from Hacker News top stories"""
    
    def __init__(self):
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.tech_keywords = {
            'python': ['python'],
            'javascript': ['javascript', 'js', 'node'],
            'typescript': ['typescript'],
            'go': ['golang', 'go'],
            'rust': ['rust'],
            'java': ['java'],
            'c++': ['c++', 'cpp'],
            'c#': ['c#', 'csharp'],
            'kotlin': ['kotlin'],
            'swift': ['swift']
        }
    
    def fetch_top_stories(self, limit=500):
        """Fetch top Hacker News story IDs"""
        try:
            response = requests.get(
                f"{self.base_url}/topstories.json",
                timeout=30
            )
            if response.status_code == 200:
                story_ids = response.json()[:limit]
                return story_ids
        except Exception as e:
            print(f"  ✗ Error fetching top stories: {str(e)}")
        return []
    
    def fetch_story_details(self, story_id):
        """Fetch individual story details"""
        try:
            response = requests.get(
                f"{self.base_url}/item/{story_id}.json",
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            pass
        return None
    
    def extract_tech_mentions(self):
        """Extract tech mentions from HN stories"""
        print("[Hacker News] Fetching top stories...")
        
        story_ids = self.fetch_top_stories(limit=300)
        print(f"  ✓ Fetched {len(story_ids)} story IDs")
        
        tech_mentions = Counter()
        stories_checked = 0
        
        for story_id in story_ids:
            story = self.fetch_story_details(story_id)
            if story:
                title = story.get('title', '').lower()
                text = story.get('text', '').lower() if story.get('text') else ''
                full_text = title + ' ' + text
                
                # Count mentions
                for tech, keywords in self.tech_keywords.items():
                    for keyword in keywords:
                        if keyword in full_text:
                            tech_mentions[tech] += 1
                            break
                
                stories_checked += 1
                time.sleep(0.1)  # Rate limiting
            
            if stories_checked % 50 == 0:
                print(f"  ... checked {stories_checked} stories")
        
        print(f"  ✓ Checked {stories_checked} stories")
        
        # Convert to DataFrame
        hn_data = []
        for tech, count in tech_mentions.items():
            hn_data.append({
                'tech_name': tech,
                'metric_date': datetime.now().date(),
                'hn_mentions': count,
                'source': 'hackernews'
            })
        
        return pd.DataFrame(hn_data)


# Test
if __name__ == '__main__':
    extractor = HackerNewsExtractor()
    df = extractor.extract_tech_mentions()
    print("\n=== Hacker News Data ===")
    print(df.sort_values('hn_mentions', ascending=False))
    print(f"\nFetched {len(df)} tech mentions")