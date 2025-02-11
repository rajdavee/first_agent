import os
from typing import Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class YouTubeUploader:
    def __init__(self):
        self.credentials_path = Path(__file__).parent.parent.parent / 'config' / 'credentials.json'
        self.token_path = Path(__file__).parent.parent.parent / 'config' / 'token.json'
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.youtube = self._authenticate()
    
    def _authenticate(self):
        """Handle YouTube API authentication"""
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.scopes)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('youtube', 'v3', credentials=creds)
    
    def upload_short(self, video_path: str, content_data: Dict) -> Dict:
        """Upload a YouTube Short"""
        try:
            # Extract title and description from the content data
            trend = content_data['prompt']['original_trend']['topic']
            title = f"🔥 {trend} #Shorts"
            description = f"""
            Trending topic: {trend}
            
            #Shorts #Trending #{trend.replace(' ', '')}
            """
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload the video
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            response = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            ).execute()
            
            return {
                'status': 'success',
                'video_id': response['id'],
                'url': f'https://youtube.com/shorts/{response["id"]}',
                'content_data': content_data
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'content_data': content_data
            }

    def get_upload_status(self, video_id: str) -> Dict:
        """Check the status of an uploaded video"""
        try:
            response = self.youtube.videos().list(
                part='status',
                id=video_id
            ).execute()
            
            if response['items']:
                return {
                    'status': 'success',
                    'upload_status': response['items'][0]['status'],
                    'video_id': video_id
                }
            return {
                'status': 'error',
                'error': 'Video not found',
                'video_id': video_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'video_id': video_id
            }