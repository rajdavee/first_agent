from openai import OpenAI
import os
import logging
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class PromptGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)
        logging.info("OpenAI API key loaded successfully")
    
    def generate_prompt(self, trend: Dict) -> Dict:
        """Generate creative prompts for YouTube Shorts based on trending topics"""
        try:
            # Validate trend data
            if not trend or 'topic' not in trend:
                raise ValueError("Invalid trend data")

            system_prompt = """
            You are a creative YouTube Shorts content strategist. Generate an engaging concept
            for a short-form video (under 60 seconds) based on the trending topic provided.
            Focus on creating viral-worthy content that's both entertaining and informative.
            """
            
            user_prompt = f"""
            Create a YouTube Shorts concept for this trending topic: {trend['topic']}
            
            Requirements:
            1. Hook: Attention-grabbing first 3 seconds
            2. Story: Clear narrative structure
            3. Format: Visual-first approach suitable for AI generation
            4. Duration: 30-60 seconds
            5. Style: Engaging and shareable
            
            Please provide the concept in this format:
            HOOK: [Opening hook]
            CONTENT: [Main content description]
            VISUALS: [Visual direction]
            DURATION: [Estimated duration]
            """
            
            logging.info(f"Generating prompt for trend: {trend['topic']}")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            logging.info(f"Successfully generated prompt for: {trend['topic']}")
            
            return {
                'original_trend': trend,
                'content_prompt': content,
                'status': 'success'
            }
        except Exception as e:

            logging.error(f"Error generating prompt for {trend.get('topic', 'Unknown')}: {str(e)}")
            return {
                'original_trend': trend,
                'content_prompt': None,
                'status': 'error',
                'error': str(e)
            }
    
    def generate_batch_prompts(self, trends: List[Dict]) -> List[Dict]:
        """Generate prompts for multiple trends"""
        prompts = []
        for trend in trends:
            prompt = self.generate_prompt(trend)
            prompts.append(prompt)
            if prompt['status'] == 'error':
                logging.error(f"Failed to generate prompt for trend: {trend.get('topic', 'Unknown')}")
        return prompts
    
    def filter_best_prompts(self, prompts: List[Dict], limit: int = 5) -> List[Dict]:
        """Filter and return the best prompts based on engagement potential"""
        valid_prompts = [p for p in prompts if p['status'] == 'success']
        
        if not valid_prompts:
            logging.error("No valid prompts found after filtering")
            return []
            
        valid_prompts.sort(
            key=lambda x: x['original_trend'].get('volume', 0) or 0,
            reverse=True
        )
        
        return valid_prompts[:limit]