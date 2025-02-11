import json
import os
from datetime import datetime
from pytrends.request import TrendReq
from typing import List, Dict
import praw
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

class TrendScraper:
    def __init__(self):
        # Google Trends API
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        # Reddit API
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID', 'DEFAULT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET', 'DEFAULT_CLIENT_SECRET'),
            user_agent='Trending Topics Bot 1.0'
        )
        
        # YouTube API
        self.youtube = build('youtube', 'v3', 
                           developerKey=os.getenv('YOUTUBE_API_KEY'))
        
        self.relevant_topics = [
            'ai', 'artificial intelligence', 'tech', 'technology',
            'news', 'breaking', 'trending', 'viral',
            'innovation', 'future', 'startup', 'business',
            'science', 'research', 'discovery'
        ]

    def is_relevant_trend(self, topic: str) -> bool:
        """Check if trend is relevant to our content focus"""
        topic_lower = topic.lower()
        # Check if topic contains any relevant keywords
        return any(keyword in topic_lower for keyword in self.relevant_topics)
    
    def get_reddit_trends(self) -> List[Dict]:
        """Get trending topics from Reddit"""
        try:
            # Get trending from r/popular and r/all
            trending_posts = []
            for subreddit in ['popular', 'all']:
                hot_posts = self.reddit.subreddit(subreddit).hot(limit=10)
                trending_posts.extend([{
                    'source': 'reddit',
                    'topic': post.title,
                    'volume': post.score,
                    'url': f'https://reddit.com{post.permalink}'
                } for post in hot_posts])
            
            # Sort by score and take top 10
            trending_posts.sort(key=lambda x: x['volume'], reverse=True)
            return trending_posts[:10]
        except Exception as e:
            print(f"Error fetching Reddit trends: {e}")
            return []

    def get_youtube_trends(self) -> List[Dict]:
        """Get trending videos from YouTube using the API"""
        try:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                chart="mostPopular",
                regionCode="US",
                maxResults=10
            )
            response = request.execute()
            
            return [{
                'source': 'youtube',
                'topic': item['snippet']['title'],
                'volume': int(item['statistics']['viewCount']),
                'url': f"https://youtube.com/watch?v={item['id']}"
            } for item in response['items']]
        except Exception as e:
            print(f"Error fetching YouTube trends: {e}")
            return []

    def get_google_trends(self) -> List[Dict]:
        """Get trending searches from Google Trends"""
        try:
            # Get real-time trending searches for US
            trending_searches = self.pytrends.realtime_trending_searches(pn='US')
            
            # Extract topics from the dataframe
            if not trending_searches.empty:
                trends = []
                for _, row in trending_searches.head(10).iterrows():
                    trends.append({
                        'source': 'google',
                        'topic': row['title'],
                        'volume': None,
                        'url': row.get('link', None)
                    })
                return trends
            return []
        except Exception as e:
            print(f"Error fetching Google trends: {e}")
            # Fallback to default trending searches
            try:
                daily_trends = self.pytrends.trending_searches(pn='united_states')
                return [{
                    'source': 'google',
                    'topic': topic,
                    'volume': None,
                    'url': None
                } for topic in daily_trends[:10]]
            except Exception as e2:
                print(f"Error fetching fallback Google trends: {e2}")
                return []

    def get_all_trends(self) -> List[Dict]:
        """Get and filter relevant trends"""
        all_trends = []
        all_trends.extend(self.get_google_trends())
        all_trends.extend(self.get_reddit_trends())
        all_trends.extend(self.get_youtube_trends())
        
        # Filter for relevant topics
        relevant_trends = [
            trend for trend in all_trends 
            if self.is_relevant_trend(trend['topic'])
        ]
        
        # Add timestamp
        timestamp = datetime.now().isoformat()
        for trend in relevant_trends:
            trend['timestamp'] = timestamp
        
        return relevant_trends

    def save_trends(self, trends: List[Dict], filename: str = None):
        """Save trends to a JSON file"""
        if filename is None:
            filename = f'trends_{datetime.now().strftime("%Y%m%d_%H%M")}.json'
        
        filepath = os.path.join(os.path.dirname(__file__), '..', '..', 'data', filename)
        with open(filepath, 'w') as f:
            json.dump(trends, f, indent=2)
        
        return filepath