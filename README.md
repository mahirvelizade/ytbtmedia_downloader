# YouTube Downloader Bot

A production-ready Telegram bot for downloading YouTube videos as MP3 or MP4.

Built with Python 3.12, aiogram 3, yt-dlp, and FFmpeg.

## Features

- Download YouTube videos as MP3 (64-160 kbps) or MP4 (360p-1080p)
- Real-time download progress with speed and ETA
- Automatic audio/video merging via FFmpeg
- URL validation and metadata extraction
- Rate limiting and concurrent download prevention
- Automatic file cleanup after sending
- Comprehensive logging
- Docker support

## Prerequisites

- Python 3.12+
- FFmpeg (for audio extraction and video merging)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### FFmpeg Installation

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram Bot Token | (required) |
| `MAX_DOWNLOAD_SIZE_GB` | Max download size limit | `2` |
| `DOWNLOAD_PATH` | Download directory | `downloads` |
| `TEMP_PATH` | Temporary files directory | `temp` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Installation

### Local

```bash
# Clone and enter the project
cd youtube_downloader_bot

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your BOT_TOKEN

# Run the bot
python main.py
```

### Docker

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Usage

1. Start the bot: `/start`
2. Send a YouTube URL
3. Choose format (MP3 or MP4)
4. Choose quality
5. Wait for download and processing
6. Receive the file

## Project Structure

```
youtube_downloader_bot/
├── app/
│   ├── handlers/       # Telegram message handlers
│   ├── keyboards/      # Inline keyboard builders
│   ├── services/       # Business logic (YouTube, downloader)
│   ├── middlewares/    # Middleware (throttling)
│   ├── filters/        # Custom filters
│   ├── utils/          # Utility functions
│   ├── config.py       # Configuration
│   ├── logger.py       # Logging setup
│   └── bot.py          # Bot and dispatcher instances
├── downloads/          # Downloaded files (auto-cleaned)
├── temp/               # Temporary processing files
├── logs/               # Log files
├── main.py             # Entry point
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Troubleshooting

**FFmpeg not found:** Install FFmpeg and ensure it's in your PATH.

**Download fails:** The video might be age-restricted, private, or removed.

**File too large:** Telegram has a 50MB upload limit. The bot logs the error.

**Bot not responding:** Check logs in `logs/bot.log`.
