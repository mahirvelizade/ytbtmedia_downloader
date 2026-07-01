import time
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5) -> None:
        self.rate_limit = rate_limit
        self.last_time: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            now = time.time()
            last = self.last_time.get(user_id, 0.0)
            if now - last < self.rate_limit:
                return
            self.last_time[user_id] = now

        return await handler(event, data)
