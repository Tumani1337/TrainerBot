from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from keyboards import (
    main_menu,
    periods_keyboard,
    workout_types,
    back_button
)
from service import WorkoutService, UserService, StatsService

router = Router()

@router.message(F.text.in_(("📊 Статистика", "/statistics")))
@router.message(Command("statistics"))
async def statistics_menu(message: Message):
    await message.answer(
        "Выберите период для статистики:",
        reply_markup=periods_keyboard()
    )

    