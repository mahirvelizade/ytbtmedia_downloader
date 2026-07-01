# YouTube Downloader Bot (ytbtmedia_bot)

## Quick Start
```bash
cd /Users/mahirvliyev/Desktop/YTBT/youtube_downloader_bot
export PATH="$HOME/.local/bin:$PATH"
python3 main.py
```
Docker: `docker compose up -d`

## GitHub
- Repo: `https://github.com/mahirvelizade/ytbtmedia_downloader`
- Remote: `origin` → `main`
- Push: `git push origin main`

## Bot
- Username: @ytbtmedia_bot
- Token: 8875369464:AAHNSVu9Ye5bIHeIetYeQVKY4EKyOpMIKHo
- PID (running): `ps aux | grep main.py | grep -v grep`

## Fixes Applied
1. `edit_message_text` keyword args (aiogram 3.22 compat)
2. `player_client`: android + ios (YouTube 403 bypass)
3. `http_headers`: spoofed browser UA
4. `extractor_retries`: 3
5. `socket_timeout`: 30s
6. `throttledratelimit` bypass
7. `None` check after `get_info`
8. URL pattern: supports subdomains (m., music., etc.)

## Dependencies
- Python 3.12+ (installed: 3.9)
- FFmpeg: `~/.local/bin/ffmpeg` (8.1.2)
- yt-dlp 2025.10.14, aiogram 3.22.0

## Files
- Config: `app/config.py`
- Handlers: `app/handlers/start.py`, `app/handlers/download.py`
- Downloader: `app/services/downloader.py`
- YouTube: `app/services/youtube.py`
- Keyboards: `app/keyboards/inline.py`
- Middleware: `app/middlewares/throttling.py`

## Logs
- `logs/bot.log` — bot activity
- `bot_output.log` — stdout/stderr

## To reopen later
```bash
cd /Users/mahirvliyev/Desktop/YTBT/youtube_downloader_bot
# Everything is already connected — just start the bot
```
