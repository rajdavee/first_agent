# Social Media Content Automation

Automated content creation and distribution pipeline for YouTube Shorts.

## Features

- Trend Detection from multiple sources (Reddit, YouTube, Google Trends)
- AI-powered content generation using Google's Gemini
- Automatic video creation with text-to-speech
- YouTube Shorts upload automation
- Scheduled content publishing

## Setup

1. Clone the repository

```bash
git clone <repository-url>
cd smm
```

2. Create and activate virtual environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Configure API Keys
   Create a `.env` file in the root directory with:

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Google API
YOUTUBE_API_KEY=your_api_key

# Set timezone
TZ=UTC
```

5. Configure YouTube OAuth

- Place your `credentials.json` in the `/config` directory
- Run the script and complete OAuth authentication when prompted

## Security Notes

1. Never commit sensitive credentials to the repository
2. Copy `.env.example` to `.env` and add your credentials
3. Copy `config/credentials.example.json` to `config/credentials.json` and add your Google OAuth credentials
4. Make sure these files are in your .gitignore

## Security Setup

1. Environment Variables:

   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

2. YouTube OAuth:

   ```bash
   cp config/credentials.example.json config/credentials.json
   # Edit credentials.json with your Google OAuth credentials
   ```

3. Never commit sensitive files:
   - .env
   - credentials.json
   - token.json
   - Any files containing API keys or secrets

## Usage

Run the main script:

```bash
python src/main.py
```

The script will:

1. Fetch trending topics
2. Generate content
3. Create video with voiceover
4. Upload to YouTube as a Short
5. Repeat on schedule (default: every 2 hours)

## Project Structure

```
smm/
├── config/
│   └── credentials.json
├── data/
│   ├── content/
│   └── audio/
├── src/
│   ├── trend_detection/
│   ├── prompt_generation/
│   ├── content_creation/
│   └── uploading/
├── .env
├── .gitignore
└── requirements.txt
```

## Requirements

- Python 3.11+
- FFmpeg (for video processing)
- API keys for:
  - Reddit
  - YouTube
- Google Cloud OAuth 2.0 credentials

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
