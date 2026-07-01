import logging
import time
from typing import Dict, List, Optional

from aiogram import Router, F
from aiogram.exceptions import TelegramEntityTooLarge
from aiogram.types import Message, CallbackQuery, FSInputFile

from app.keyboards.inline import (
    get_format_keyboard,
    get_mp3_quality_keyboard,
    get_mp4_quality_keyboard,
)
from app.services.youtube import YouTubeService
from app.services.downloader import downloader_service
from app.utils.file_utils import cleanup_file, cleanup_files, split_audio, split_video

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
        if not info:
            await message.answer("Something went wrong.\n\nPlease try again later.")
            return
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

    file_path = None
    parts = []

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
        sent = False

        try:
            if fmt == "mp3":
                await callback.message.answer_audio(input_file)
            else:
                await callback.message.answer_video(input_file)
            sent = True
        except TelegramEntityTooLarge:
            if fmt == "mp3":
                lower_qualities = ["48", "32"]
                current_idx = lower_qualities.index(quality) + 1 if quality in lower_qualities else 0
                retried = False
                for q in lower_qualities[current_idx:]:
                    await bot.edit_message_text(
                        f"⬇ Retrying at {q}kbps (smaller file)...",
                        chat_id=chat_id, message_id=message_id,
                    )
                    cleanup_file(file_path)
                    file_path = await downloader_service.download_mp3(
                        url=url, quality=q,
                        user_id=user_id, chat_id=chat_id,
                        message_id=message_id, bot=bot,
                    )
                    input_file = FSInputFile(file_path)
                    try:
                        if fmt == "mp3":
                            await callback.message.answer_audio(input_file)
                        else:
                            await callback.message.answer_video(input_file)
                        retried = True
                        sent = True
                        break
                    except TelegramEntityTooLarge:
                        continue
                if retried:
                    await bot.delete_message(chat_id, message_id)
                    return

            await bot.edit_message_text(
                "📤 Splitting file into parts...",
                chat_id=chat_id, message_id=message_id,
            )
            if fmt == "mp3":
                parts = await split_audio(file_path)
            else:
                parts = await split_video(file_path)

            total = len(parts)
            for i, part in enumerate(parts, 1):
                await bot.edit_message_text(
                    f"📤 Uploading part {i}/{total}...",
                    chat_id=chat_id, message_id=message_id,
                )
                input_part = FSInputFile(part)
                if fmt == "mp3":
                    await callback.message.answer_audio(
                        input_part, caption=f"Part {i}/{total}"
                    )
                else:
                    await callback.message.answer_video(
                        input_part, caption=f"Part {i}/{total}"
                    )
            sent = True

        if sent:
            await bot.delete_message(chat_id, message_id)

    except TelegramEntityTooLarge:
        logger.warning(f"File too large for user {user_id}")
        try:
            await bot.edit_message_text(
                "File is too large (max 50MB). Try a shorter video or lower quality.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except Exception:
            await callback.message.answer(
                "File is too large (max 50MB). Try a shorter video or lower quality."
            )
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
        if parts:
            cleanup_files(parts)
        elif file_path:
            cleanup_file(file_path)
