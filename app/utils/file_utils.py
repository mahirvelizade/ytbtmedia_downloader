import asyncio
import logging
import os
import re
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 48 * 1024 * 1024


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', "", filename)
    safe = safe.strip().replace("\n", " ").replace("\r", "")
    return safe[:max_length]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


async def split_audio(file_path: Path) -> List[Path]:
    file_size = os.path.getsize(file_path)
    if file_size <= MAX_FILE_SIZE:
        return [file_path]

    stem = file_path.stem
    ext = file_path.suffix
    parent = file_path.parent

    import subprocess as sp

    probe = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(file_path),
        stdout=sp.PIPE, stderr=sp.PIPE,
    )
    stdout, _ = await probe.communicate()
    duration = float(stdout.decode().strip())

    num_parts = (file_size // MAX_FILE_SIZE) + 1
    segment_time = duration / num_parts

    if num_parts == 1:
        return [file_path]

    for i in range(num_parts):
        start = i * segment_time
        out_path = parent / f"{stem}_part{i+1:02d}{ext}"
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(file_path),
            "-t", str(segment_time),
            "-c", "copy",
            str(out_path),
            stdout=sp.DEVNULL, stderr=sp.DEVNULL,
        )
        await proc.wait()

    parts = sorted(parent.glob(f"{stem}_part*{ext}"))
    return parts


async def split_video(file_path: Path) -> List[Path]:
    file_size = os.path.getsize(file_path)
    if file_size <= MAX_FILE_SIZE:
        return [file_path]

    stem = file_path.stem
    ext = file_path.suffix
    parent = file_path.parent

    import subprocess as sp

    probe = await asyncio.create_subprocess_exec(
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(file_path),
        stdout=sp.PIPE, stderr=sp.PIPE,
    )
    stdout, _ = await probe.communicate()
    duration = float(stdout.decode().strip())

    num_parts = (file_size // MAX_FILE_SIZE) + 1
    segment_time = duration / num_parts

    if num_parts == 1:
        return [file_path]

    for i in range(num_parts):
        start = i * segment_time
        out_path = parent / f"{stem}_part{i+1:02d}{ext}"
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y",
            "-ss", str(start),
            "-i", str(file_path),
            "-t", str(segment_time),
            "-c", "copy",
            str(out_path),
            stdout=sp.DEVNULL, stderr=sp.DEVNULL,
        )
        await proc.wait()

    parts = sorted(parent.glob(f"{stem}_part*{ext}"))
    return parts


def cleanup_file(file_path: Optional[Path]) -> None:
    if not file_path:
        return
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")


def cleanup_files(file_paths: List[Path]) -> None:
    for fp in file_paths:
        cleanup_file(fp)
