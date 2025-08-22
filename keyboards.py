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

def goals_management() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="➕ Новая цель",
            callback_data="new_goal"
        ),
        InlineKeyboardButton(
            text="📋 Мои цели",
            callback_data="list_goals"
        )
    )
    return builder.as_markup()

def reminders_management() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="➕ Новое напоминание",
            callback_data="new_reminder"
        ),
        InlineKeyboardButton(
            text="📋 Мои напоминания",
            callback_data="list_reminders"
        )
    )
    return builder.as_markup()

def confirm_cancel() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Подтвердить"),
        KeyboardButton(text="❌ Отменить")
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def days_of_week_keyboard() -> InlineKeyboardMarkup:
    days = [
        ("Пн", "1"), ("Вт", "2"), ("Ср", "3"),
        ("Чт", "4"), ("Пт", "5"), ("Сб", "6"), ("Вс", "7")
    ]
    builder = InlineKeyboardBuilder()
    for day, num in days:
        builder.add(InlineKeyboardButton(
            text=day,
            callback_data=f"reminder_day_{num}"
        ))
    builder.adjust(7)
    return builder.as_markup()