import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    safe = re.sub(r'[<>:"/\\|?*]', "", filename)
    safe = safe.strip().replace("\n", " ").replace("\r", "")
    return safe[:max_length]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def cleanup_file(file_path: Optional[Path]) -> None:
    if not file_path:
        return
    try:
        if file_path.exists():
            file_path.unlink()
            logger.debug(f"Deleted file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")
