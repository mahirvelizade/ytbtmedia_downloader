import logging
import time
from typing import Dict, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from app.keyboards.inline import (
    get_format_keyboard,
    get_mp3_quality_keyboard,
    get_mp4_quality_keyboard,
)
from app.services.youtube import YouTubeService
from app.services.downloader import downloader_service
from app.utils.file_utils import cleanup_file

logger = logging.getLogger(__name__)

router = Router()
youtube_service = YouTubeService()
user_data: Dict[int, dict] = {}

URL_PATTERN = (
    r"^(https?://)?([a-zA-Z0-9-]+\.)?(youtube\.com|youtu\.be)/"
)

SESSION_TIMEOUT = 300


@router.message(F.text.regexp(URL_PATTERN))
async def handle_youtube_url(message: Message) -> None:
    url = message.text.strip()
    user_id = message.from_user.id

    if downloader_service.is_active(user_id):
        await message.answer(
            "Please wait until your current download finishes."
        )
        return

    if not youtube_service.is_valid_url(url):
        await message.answer("This is not a valid YouTube URL.")
        return

    try:
        info = await youtube_service.get_info(url)
    except Exception:
        logger.exception(f"Failed to extract info for URL: {url}")
        await message.answer("Something went wrong.\n\nPlease try again later.")
        return

    title = info.get("title", "Unknown")
    duration = info.get("duration", 0)
    minutes, seconds = divmod(duration, 60)

    user_data[user_id] = {
        "url": url,
        "timestamp": time.time(),
    }

    await message.answer(
        f"📹 {title}\n"
        f"⏱ {minutes}:{seconds:02d}\n\n"
        "Choose format:",
        reply_markup=get_format_keyboard(),
    )


@router.callback_query(F.data == "format:mp3")
async def choose_mp3(callback: CallbackQuery) -> None:
    await _handle_format_choice(callback, "mp3")


@router.callback_query(F.data == "format:mp4")
async def choose_mp4(callback: CallbackQuery) -> None:
    await _handle_format_choice(callback, "mp4")


async def _handle_format_choice(callback: CallbackQuery, fmt: str) -> None:
    user_id = callback.from_user.id
    data = user_data.get(user_id)

    if not data or time.time() - data["timestamp"] > SESSION_TIMEOUT:
        await callback.message.edit_text(
            "Session expired. Please send the URL again."
        )
        await callback.answer()
        return

    data["format"] = fmt

    if fmt == "mp3":
        keyboard = get_mp3_quality_keyboard()
        text = "Choose quality:"
    else:
        keyboard = get_mp4_quality_keyboard()
        text = "Choose quality:"

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("quality:"))
async def start_download(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    data = user_data.get(user_id)

    if not data or time.time() - data["timestamp"] > SESSION_TIMEOUT:
        await callback.message.edit_text(
            "Session expired. Please send the URL again."
        )
        await callback.answer()
        return

    parts = callback.data.split(":")
    fmt = parts[1]
    quality = parts[2]
    url = data["url"]

    await callback.answer()

    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    bot = callback.bot

    await bot.edit_message_text("⬇ Downloading...", chat_id=chat_id, message_id=message_id)

    try:
        if fmt == "mp3":
            file_path = await downloader_service.download_mp3(
                url=url,
                quality=quality,
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                bot=bot,
            )
        else:
            file_path = await downloader_service.download_mp4(
                url=url,
                quality=quality,
                user_id=user_id,
                chat_id=chat_id,
                message_id=message_id,
                bot=bot,
            )

        await bot.edit_message_text("📤 Uploading...", chat_id=chat_id, message_id=message_id)

        input_file = FSInputFile(file_path)

        if fmt == "mp3":
            await callback.message.answer_audio(input_file)
        else:
            await callback.message.answer_video(input_file)

        await bot.delete_message(chat_id, message_id)

    except Exception:
        logger.exception(f"Download failed for user {user_id}")
        try:
            await bot.edit_message_text(
                "Something went wrong.\n\nPlease try again later.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            await callback.message.answer(
                "Something went wrong.\n\nPlease try again later."
            )
    finally:
        user_data.pop(user_id, None)
        if "file_path" in locals():
            cleanup_file(file_path)
