from openai import OpenAI
import os
from pathlib import Path
import requests
from PIL import Image
import subprocess
import numpy as np
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class ContentCreator:
    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / 'data' / 'content'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.audio_dir = Path(__file__).parent.parent.parent / 'data' / 'audio'
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def format_script(self, script: str) -> str:
        """Format script into shorter, more impactful sentences"""
        lines = script.split('\n')
        formatted_lines = []
        for line in lines:
            # Split long sentences into shorter ones
            if len(line) > 40:
                words = line.split()
                current_line = []
                for word in words:
                    if len(' '.join(current_line + [word])) > 40:
                        formatted_lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        current_line.append(word)
                if current_line:
                    formatted_lines.append(' '.join(current_line))
            else:
                formatted_lines.append(line)
        return '\n'.join(formatted_lines)

    def generate_video_script(self, prompt: Dict) -> str:
        """Generate engaging script for trending topics"""
        try:
            enhanced_prompt = """
            Create a viral YouTube Shorts script about this trending topic.
            Focus on:
            1. First 3 seconds hook
            2. Engaging storytelling
            3. Current trends and relevance
            4. Clear call-to-action
            5. Maximum 30-40 words
            
            Format:
            TITLE: [Attention-grabbing title]
            HOOK: [Opening line]
            MAIN: [Key points]
            CTA: [Call to action]
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a viral content creator specializing in trendy, engaging shorts."},
                    {"role": "user", "content": f"{enhanced_prompt}\n\nTopic: {prompt['content_prompt']}"}
                ],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating script: {e}")
            return None

    def generate_visuals(self, script: str) -> str:
        """Generate image using DALL-E"""
        try:
            response = self.client.images.generate(
                prompt=f"Create a vivid scene for a YouTube Short about: {script[:100]}",
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            
            # Download the image
            img_path = self.output_dir / f"visual_{hash(script)}.png"
            response = requests.get(image_url)
            with open(img_path, 'wb') as f:
                f.write(response.content)
            
            return str(img_path)
        except Exception as e:
            print(f"Error generating visuals: {e}")
            return None

    def generate_voiceover(self, script: str) -> str:
        """Generate voice-over using OpenAI TTS"""
        try:
            # Clean up the script for narration
            narration_script = script.replace('\n', ' ').strip()
            
            # Generate audio file path
            audio_path = str(self.audio_dir / f"voiceover_{hash(script)}.mp3")
            
            # Generate voice-over using OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="nova",
                input=narration_script
            )
            
            # Save the audio file
            response.stream_to_file(audio_path)
            
            return audio_path
        except Exception as e:
            print(f"Error generating voice-over: {e}")
            return None

    def create_video_with_audio(self, image_path: str, audio_path: str) -> str:
        """Create video with voice-over using ffmpeg"""
        try:
            output_path = str(self.output_dir / f"short_{hash(str(image_path))}.mp4")
            
            # Use ffmpeg to create video from image and audio
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', image_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-tune', 'stillimage',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                output_path
            ]
            
            subprocess.run(cmd, check=True)
            return output_path
        except Exception as e:
            print(f"Error creating video: {e}")
            return None

    def create_content(self, prompt: Dict) -> Dict:
        """Main method to create a complete YouTube Short"""
        try:
            # Generate script
            script = self.generate_video_script(prompt)
            if not script:
                raise Exception("Failed to generate script")

            # Generate voice-over
            audio_path = self.generate_voiceover(script)
            if not audio_path:
                raise Exception("Failed to generate voice-over")

            # Generate image
            image_path = self.generate_visuals(script)
            if not image_path:
                raise Exception("Failed to generate visuals")

            # Create video with voice-over
            video_path = self.create_video_with_audio(image_path, audio_path)
            if not video_path:
                raise Exception("Failed to create video")

            return {
                'status': 'success',
                'video_path': video_path,
                'prompt': prompt
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'prompt': prompt
            }