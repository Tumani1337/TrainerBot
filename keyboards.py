from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import WORKOUT_TYPES, STAT_PERIODS

def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Добавить тренировку"),
        KeyboardButton(text="📊 Статистика")
    )
    builder.row(
        KeyboardButton(text="🎯 Мои цели"),
        KeyboardButton(text="⏰ Напоминания")
    )
    builder.row(
        KeyboardButton(text="ℹ️ Помощь")
    )
    return builder.as_markup(resize_keyboard=True)

def workout_types() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for workout_type in WORKOUT_TYPES:
        builder.add(KeyboardButton(text=workout_type))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def periods_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for period in STAT_PERIODS:
        builder.add(InlineKeyboardButton(
            text=period.capitalize(),
            callback_data=f"period_{period}")
        )
    builder.adjust(2)
    return builder.as_markup()