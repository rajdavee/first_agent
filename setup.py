import os
import sys
from pathlib import Path

def create_project_structure():
    base_path = Path(__file__).parent
    directories = [
        'src',
        'config',
        'data',
        'src/trend_detection',
        'src/prompt_generation',
        'src/content_creation',
        'src/uploading'
    ]
    
    for directory in directories:
        (base_path / directory).mkdir(parents=True, exist_ok=True)
    
    # Create requirement.txt with necessary dependencies
    requirements = """
google-api-python-client
google-auth-oauthlib
openai
pytube
Pillow
moviepy
tweepy
pandas
requests
python-dotenv
schedule
"""
    
    with open(base_path / 'requirements.txt', 'w') as f:
        f.write(requirements.strip())

if __name__ == '__main__':
    create_project_structure()