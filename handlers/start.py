from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message, user_service):
    user = await user_service.register_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name
    )

    welcome_text = (
        "🏋️‍♂️ Добро пожаловать в FitnessTrackerBot!\n\n"
        "Я помогу вам отслеживать ваши тренировки, ставить цели "
        "и следить за прогрессом.\n\n"
        "Используйте кнопки ниже для навигации:"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=main_menu()
    )