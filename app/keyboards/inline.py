from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_format_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎵 MP3", callback_data="format:mp3")
    builder.button(text="🎬 MP4", callback_data="format:mp4")
    builder.adjust(2)
    return builder.as_markup()


def get_mp3_quality_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for quality in ["32", "48", "64", "96", "128"]:
        builder.button(
            text=f"{quality} kbps",
            callback_data=f"quality:mp3:{quality}",
        )
    builder.adjust(2)
    return builder.as_markup()


def get_mp4_quality_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for quality in ["360", "480", "720", "1080"]:
        builder.button(
            text=f"{quality}p",
            callback_data=f"quality:mp4:{quality}",
        )
    builder.adjust(2)
    return builder.as_markup()
