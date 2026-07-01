from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start_command(message: Message) -> None:
    await message.answer(
        "Welcome!\n\nSend a YouTube link.\nI'll convert it into MP3 or MP4."
    )
