from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from keyboards import main_menu

help_router = Router()

@help_router.message(F.text.in_(("ℹ️ Помощь")))
@help_router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "🤖 FitnessTrackerBot - Помощь\n\n"
        "Основные команды:\n"
        "➕ Добавить тренировку - Записать новую тренировку\n"
        "📊 Статистика - Посмотреть статистику тренировок\n"
        "🎯 Мои цели - Управление спортивными целями\n"
        "⏰ Напоминания - Настройка напоминаний о тренировках\n\n"
        "Текстовые команды:\n"
        "/start - Начать работу с ботом\n"
        "/add_workout - Добавить тренировку\n"
        "/view_workouts - Посмотреть историю тренировок\n"
        "/set_goal - Установить новую цель\n"
        "/view_goals - Посмотреть текущие цели\n"
        "/progress - Посмотреть прогресс по целям\n"
        "/reminder - Управление напоминаниями\n"
        "/statistics - Просмотр статистики\n"
        "/compare - Сравнение периодов\n"
        "/export_data - Экспорт данных\n"
        "/help - Эта справка\n\n"
        "Для начала просто нажмите на кнопку в меню! 🏃‍♂️"
    )

    await message.answer(help_text, reply_markup=main_menu())