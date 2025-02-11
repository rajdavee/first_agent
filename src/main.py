import os
import schedule
import time
from pathlib import Path
from datetime import datetime
from trend_detection.scraper import TrendScraper
from prompt_generation.generator import PromptGenerator
from content_creation.creator import ContentCreator
from uploading.youtube_uploader import YouTubeUploader
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

class ContentAutomator:
    def __init__(self):
        load_dotenv()
        self.trend_scraper = TrendScraper()
        self.prompt_generator = PromptGenerator()
        self.content_creator = ContentCreator()
        self.youtube_uploader = YouTubeUploader()
    
    def run_pipeline(self):
        """Execute the full content automation pipeline"""
        try:
            # Step 1: Get trending topics
            logging.info("Fetching trending topics...")
            trends = self.trend_scraper.get_all_trends()
            if not trends:
                logging.error("No trends found. Skipping pipeline execution.")
                return
            
            # Log found trends
            logging.info(f"Found {len(trends)} trends")
            
            # Take only the top trend by volume
            top_trend = max(trends, key=lambda x: x.get('volume', 0) or 0)
            logging.info(f"Processing top trend: {top_trend['topic']} from {top_trend['source']}")
            
            # Step 2: Generate prompt for top trend
            logging.info("Generating prompt...")
            prompt = self.prompt_generator.generate_prompt(top_trend)
            
            if prompt['status'] != 'success':
                logging.error("Failed to generate prompt. Skipping further processing.")
                return
                
            logging.info(f"Successfully generated prompt for: {top_trend['topic']}")
            
            # Step 3: Create content
            logging.info("Creating content...")
            content_result = self.content_creator.create_content(prompt)
            if content_result['status'] != 'success':
                logging.error(f"Content creation failed: {content_result.get('error')}")
                return
            
            # Step 4: Upload to YouTube
            logging.info("Uploading to YouTube...")
            upload_result = self.youtube_uploader.upload_short(
                content_result['video_path'],
                content_result
            )
            
            if upload_result['status'] == 'success':
                logging.info(f"Successfully uploaded video: {upload_result['url']}")
            else:
                logging.error(f"Upload failed: {upload_result.get('error')}")
            
        except Exception as e:
            logging.error(f"Pipeline failed: {str(e)}")

def main():
    automator = ContentAutomator()
    
    # Schedule to run every 2 hours (to give more time for processing)
    schedule.every(2).hours.do(automator.run_pipeline)
    
    # Run once immediately
    automator.run_pipeline()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()