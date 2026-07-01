import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    MAX_DOWNLOAD_SIZE_GB: int = int(os.getenv("MAX_DOWNLOAD_SIZE_GB", "2"))
    DOWNLOAD_PATH: Path = Path(os.getenv("DOWNLOAD_PATH", "downloads"))
    TEMP_PATH: Path = Path(os.getenv("TEMP_PATH", "temp"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = Config()
