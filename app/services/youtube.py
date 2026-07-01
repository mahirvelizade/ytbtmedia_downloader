import asyncio
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

import yt_dlp


class YouTubeService:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._url_pattern = re.compile(
            r"^(https?://)?([a-zA-Z0-9-]+\.)?(youtube\.com|youtu\.be)/"
        )

    def is_valid_url(self, url: str) -> bool:
        return bool(self._url_pattern.match(url.strip()))

    async def get_info(self, url: str) -> Optional[Dict]:
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                self._executor,
                self._extract_info,
                url,
            )
        except Exception:
            return None

    def _extract_info(self, url: str) -> Dict:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            },
            "extractor_args": {"youtube": {"skip": ["webpage", "dash", "hls"], "player_client": ["android"]}},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)
