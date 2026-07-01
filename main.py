import asyncio
import logging

from app.bot import bot, dp
from app.handlers import start, download
from app.middlewares.throttling import ThrottlingMiddleware
from app.logger import setup_logger

logger = logging.getLogger(__name__)


async def main() -> None:
    setup_logger()

    dp.include_router(start.router)
    dp.include_router(download.router)

    dp.message.middleware(ThrottlingMiddleware())

    logger.info("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
