import re

from aiogram.filters import BaseFilter
from aiogram.types import Message


class YouTubeURLFilter(BaseFilter):
    def __init__(self) -> None:
        self._pattern = re.compile(
            r"^(https?://)?([a-zA-Z0-9-]+\.)?(youtube\.com|youtu\.be)/"
        )

    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        return bool(self._pattern.match(message.text.strip()))
