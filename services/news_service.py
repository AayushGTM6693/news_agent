import requests
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class NewsService:
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
    
    def get_random_news(self, count: int = 5) -> List[Dict]:
        """Fetch random news articles"""
        url = f"{self.base_url}/everything"
        params = {
            'apiKey': self.api_key,
            'sortBy': 'publishedAt',
            'pageSize': count,
            'language': 'en',
            'q': 'technology OR health OR science OR business'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'content': article.get('content', '')
                })
            
            return articles
            
        except requests.RequestException as e:
            print(f"❌ Error fetching news: {e}")
            return []