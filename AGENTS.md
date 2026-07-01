# YouTube Downloader Bot (ytbtmedia_bot)

## 🔑 Credentials & Tokens (stored in env vars / locally only)
- **Bot Token**: `BOT_TOKEN` env var (set in Railway dashboard + local `.env`)
- **Bot Username**: @ytbtmedia_bot
- **GitHub PAT**: stored in AGENTS.md locally only (not committed)
- **Hugging Face Token**: stored locally for FLUX.1-schnell image gen
- **Railway**: Logged in as `Mahir (mahirveliyev@gmail.com)` via CLI

## ⚙️ Project Setup
- **Path**: `~/Projects/youtube_downloader_bot` (moved from Desktop due to macOS TCC sandbox)
- **Language**: Azerbaijani (bot replies in AZ)
- **Python**: 3.9 (system default on macOS)
- **FFmpeg**: 8.1.2 at `~/.local/bin/ffmpeg` (PATH in `~/.zshrc`)
- **Deps**: aiogram 3.22.0, yt-dlp 2025.10.14, aiofiles, mutagen

## 🚀 Quick Start
```bash
cd /Users/mahirvliyev/Projects/youtube_downloader_bot
python3 main.py
```

## 🐙 GitHub
- **Repo**: `https://github.com/mahirvelizade/ytbtmedia_downloader`
- **Remote**: `origin` → `main`
- **Push**: `git push origin main`
- **PAT for pushing**: stored locally in AGENTS.md (use `ghp_...` value)
- Command: `git remote set-url origin https://<PAT>@github.com/mahirvelizade/ytbtmedia_downloader.git && git push origin main && git remote set-url origin https://github.com/mahirvelizade/ytbtmedia_downloader.git`

## 🏠 Local Dev
### Shell Aliases (in ~/.zshrc)
- `ytbt` — cd to project
- `ytbt-start` — start bot
- `ytbt-logs` — watch logs
- `ytbt-status` — check if running

### launchd Auto-start
- **Service**: `com.ytbt.bot`
- **Plist**: `~/Library/LaunchAgents/com.ytbt.bot.plist`
- **Load**: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ytbt.bot.plist`
- **Unload**: `launchctl bootout gui/$(id -u)/com.ytbt.bot`
- **Kill**: `pkill -f main.py`
- **Note**: Plist must point to `~/Projects/`, NOT `~/Desktop/` (TCC blocks launchd from Desktop)

## ☁️ Railway Deployment (PRODUCTION)
### Connection
- **CLI**: `$HOME/.railway/bin/railway`
- **Login**: Already logged in as `mahirveliyev@gmail.com`
- **Project**: `YTBT-Bot` (ID: `904a5acc-eb50-4f25-832a-3aa331ca0486`)
- **Service**: `ytbt-bot` / `YTBT-Bot` (ID: `576a8c08-3167-417b-a0f9-85dc5eaa7a45`)
- **Deploy**: `railway up --service YTBT-Bot` (from project dir)
- **Redeploy**: `railway redeploy --yes`
- **Logs**: `railway logs --service ytbt-bot`
- **Build logs**: `railway logs --deployment`
- **Status**: `railway status`

### Architecture
- **Builder**: Docker (Dockerfile in root)
- **Base**: `python:3.11-slim` with FFmpeg installed via apt
- **Health check**: Disabled (bot is a long-polling process, not a web server)
- **Env vars**: `BOT_TOKEN=8875369464:AAHNSVu9Ye5bIHeIetYeQVKY4EKyOpMIKHo` (set via Railway dashboard)

### Deployment History
1. **First deploy** — nixpacks auto-detected Python, bot connected at 06:57:40
2. **Second deploy** — added `nixpacks.toml` → broke build (healthcheck failed)
3. **Third deploy** — Dockerfile + removed healthcheck → success, bot online
4. **Fourth deploy** — added `cookies.txt` for YouTube bot bypass

### Important Commands
- `BOT_TOKEN=... railway up` — deploy with env var
- `railway down` — remove all deployments (WARNING: says "No deployments found" even if service exists)
- `railway service list` — list services
- Railway auto-detects Dockerfile; Nixpacks also works without config

## 🤖 Bot Behavior
### Commands
- `/start` — welcome message with language selection
- Send YouTube URL → choose MP3 or MP4 → choose quality → download

### Error Handling
- `Something went wrong. Please try again later.` — generic error
- Files >50MB: `TelegramEntityTooLarge` → friendly "too large" message instead of crash

### Known YouTube Fixes Applied
1. `player_client`: `["android", "ios"]` (YouTube 403 bypass)
2. `http_headers`: spoofed Chrome UA + Accept-Language
3. `extractor_retries`: 3
4. `socket_timeout`: 30s
5. `throttledratelimit`: 100Mbps
6. URL regex: supports youtube.com, youtu.be, m.youtube.com, music.youtube.com, etc.
7. **Cookies**: `cookies.txt` in project root (extracted from browser) passed via `cookiefile`

### YouTube Bot Detection
- Railway (datacenter IP) triggers "Sign in to confirm you're not a bot"
- Fix: pass `cookies.txt` from a real browser session via `cookiefile` option
- Cookies must be refreshed periodically (they expire)

## 🖼️ Image Generation
- **Model**: FLUX.1-schnell via Hugging Face Inference API
- **Endpoint**: `https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell`
- **Output path**: `~/Desktop/Generated/`
- **Aspect ratio**: Pass `"parameters": {"width": W, "height": H}` in payload (16:9 = 1344x768)
- **Limits**: Fair use (~30-100 req/min)
- **Video gen**: NOT supported (Intel Core i5 too slow for local, HF free tier doesn't support video)

## 🧱 Project Structure
```
youtube_downloader_bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # entry point
│   ├── config.py            # env vars, paths
│   ├── filters/             # aiogram filters
│   ├── handlers/
│   │   ├── start.py         # /start command
│   │   └── download.py      # URL handler, quality selection
│   ├── keyboards/
│   │   └── inline.py        # inline keyboards
│   ├── middlewares/
│   │   └── throttling.py    # rate limiting
│   ├── services/
│   │   ├── downloader.py    # yt-dlp async wrapper
│   │   └── youtube.py       # URL validation, info extraction
│   └── utils/
│       └── __init__.py
├── cookies.txt              # YouTube session cookies (git-tracked)
├── Dockerfile               # python:3.11-slim + ffmpeg
├── railway.json             # Railway config (restartPolicy: always)
├── .dockerignore
├── requirements.txt
└── AGENTS.md                # this file
```

## ⚠️ Limits & Constraints
- Telegram file size limit: 50MB
- yt-dlp bot detection requires cookies (refreshed periodically)
- macOS TCC blocks launchd from accessing `~/Desktop/`
- Intel Core i5 (not Apple Silicon) — local AI/image tasks are limited

## 📝 To Reopen Later
```bash
cd /Users/mahirvliyev/Projects/youtube_downloader_bot
# Everything is connected. Start locally with:
python3 main.py
# Or check Railway:
export PATH="$HOME/.railway/bin:$PATH"
railway logs --service ytbt-bot
```
