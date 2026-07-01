import asyncio
import logging
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional, Set

import yt_dlp

from app.config import config

logger = logging.getLogger(__name__)


class ProgressInfo:
    def __init__(self) -> None:
        self.percent: str = "0%"
        self.speed: str = "N/A"
        self.eta: str = "N/A"
        self.status: str = "downloading"
        self._lock = threading.Lock()

    def update(self, percent: str, speed: str, eta: str) -> None:
        with self._lock:
            self.percent = percent
            self.speed = speed
            self.eta = eta

    def set_status(self, status: str) -> None:
        with self._lock:
            self.status = status

    def get_progress(self) -> dict:
        with self._lock:
            return {
                "percent": self.percent,
                "speed": self.speed,
                "eta": self.eta,
                "status": self.status,
            }


class DownloaderService:
    def __init__(self) -> None:
        self._active: Set[int] = set()
        self._executor = ThreadPoolExecutor(max_workers=3)

    def is_active(self, user_id: int) -> bool:
        return user_id in self._active

    def add_active(self, user_id: int) -> None:
        self._active.add(user_id)

    def remove_active(self, user_id: int) -> None:
        self._active.discard(user_id)

    async def download_mp3(
        self,
        url: str,
        quality: str,
        user_id: int,
        chat_id: int,
        message_id: int,
        bot,
    ) -> Path:
        config.TEMP_PATH.mkdir(parents=True, exist_ok=True)
        progress = ProgressInfo()
        self.add_active(user_id)

        output_template = str(config.TEMP_PATH / "%(id)s.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": quality,
                }
            ],
            "progress_hooks": [self._make_progress_hook(progress)],
            "quiet": True,
            "no_warnings": True,
        }

        update_task = asyncio.create_task(
            self._update_progress(progress, chat_id, message_id, bot, "mp3")
        )

        try:
            video_id, title = await self._run_download(ydl_opts, url, progress)
            progress.set_status("done")

            safe_title = re.sub(r'[<>:"/\\|?*]', "", title)[:200]
            temp_file = config.TEMP_PATH / f"{video_id}.mp3"

            if temp_file.exists():
                return temp_file

            files = sorted(
                config.TEMP_PATH.glob("*.mp3"), key=os.path.getmtime, reverse=True
            )
            if files:
                return files[0]

            raise FileNotFoundError(
                f"Downloaded MP3 file not found for video {video_id}"
            )
        except Exception:
            progress.set_status("error")
            raise
        finally:
            try:
                await asyncio.wait_for(update_task, timeout=5)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                update_task.cancel()
            self.remove_active(user_id)

    async def download_mp4(
        self,
        url: str,
        quality: str,
        user_id: int,
        chat_id: int,
        message_id: int,
        bot,
    ) -> Path:
        config.TEMP_PATH.mkdir(parents=True, exist_ok=True)
        progress = ProgressInfo()
        self.add_active(user_id)

        output_template = str(config.TEMP_PATH / "%(id)s.%(ext)s")
        format_str = f"bestvideo[height<={quality}]+bestaudio/best"

        ydl_opts = {
            "format": format_str,
            "outtmpl": output_template,
            "merge_output_format": "mp4",
            "progress_hooks": [self._make_progress_hook(progress)],
            "quiet": True,
            "no_warnings": True,
        }

        update_task = asyncio.create_task(
            self._update_progress(progress, chat_id, message_id, bot, "mp4")
        )

        try:
            video_id, title = await self._run_download(ydl_opts, url, progress)
            progress.set_status("done")

            safe_title = re.sub(r'[<>:"/\\|?*]', "", title)[:200]
            temp_file = config.TEMP_PATH / f"{video_id}.mp4"

            if temp_file.exists():
                return temp_file

            files = sorted(
                config.TEMP_PATH.glob("*.mp4"), key=os.path.getmtime, reverse=True
            )
            if files:
                return files[0]

            raise FileNotFoundError(
                f"Downloaded MP4 file not found for video {video_id}"
            )
        except Exception:
            progress.set_status("error")
            raise
        finally:
            try:
                await asyncio.wait_for(update_task, timeout=5)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                update_task.cancel()
            self.remove_active(user_id)

    async def _run_download(
        self, ydl_opts: dict, url: str, progress: ProgressInfo
    ) -> tuple:
        loop = asyncio.get_event_loop()
        ydl_opts["url"] = url
        return await loop.run_in_executor(
            self._executor,
            self._sync_download,
            ydl_opts,
            progress,
        )

    def _sync_download(self, ydl_opts: dict, progress: ProgressInfo) -> tuple:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(ydl_opts["url"], download=True)
        video_id = info.get("id", "unknown")
        title = info.get("title", "unknown")
        return video_id, title

    def _make_progress_hook(self, progress: ProgressInfo):
        def hook(d: dict) -> None:
            if d["status"] == "downloading":
                progress.update(
                    d.get("_percent_str", "0%").strip(),
                    d.get("_speed_str", "N/A").strip(),
                    d.get("_eta_str", "N/A").strip(),
                )
            elif d["status"] == "finished":
                progress.set_status("processing")

        return hook

    async def _update_progress(
        self,
        progress: ProgressInfo,
        chat_id: int,
        message_id: int,
        bot,
        download_type: str,
    ) -> None:
        last_update = 0.0
        processing_updated = False
        converting_emoji = "🎵" if download_type == "mp3" else "🎬"
        converting_text = "Converting..." if download_type == "mp3" else "Merging streams..."

        while True:
            info = progress.get_progress()
            if info["status"] in ("done", "error"):
                break

            now = time.time()
            if now - last_update >= 2:
                try:
                    if info["status"] == "downloading":
                        bar = self._render_progress_bar(info["percent"])
                        text = (
                            f"⬇ Downloading...\n\n"
                            f"{bar} {info['percent']}\n\n"
                            f"Speed: {info['speed']}\n\n"
                            f"ETA: {info['eta']}"
                        )
                        await bot.edit_message_text(text, chat_id, message_id)
                    elif info["status"] == "processing" and not processing_updated:
                        text = f"{converting_emoji} {converting_text}"
                        try:
                            await bot.edit_message_text(text, chat_id, message_id)
                        except Exception:
                            pass
                        processing_updated = True
                except Exception:
                    pass
                last_update = now

            await asyncio.sleep(1)

    @staticmethod
    def _render_progress_bar(percent_str: str) -> str:
        try:
            percent = float(percent_str.strip("%%"))
        except (ValueError, AttributeError):
            percent = 0.0
        filled = int(percent / 5)
        return "█" * filled + "░" * (20 - filled)


downloader_service = DownloaderService()
