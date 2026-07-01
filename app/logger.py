import logging
import sys
from pathlib import Path

from app.config import config


def setup_logger() -> logging.Logger:
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path / "bot.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)
