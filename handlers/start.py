from aiogram import Router, F
from aiogram.filters import command
from aiogram.types import Message
from keyboards import main_menu
from service import UserService

router = Router()


@router.message(command.CommandStart())
async def cmd_start(message: Message, user_service: UserService):
    user = await user_service.register_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name
    )

    welcome_text = (
        "🏋️‍♂️ Добро пожаловать в TrainerBot!\n\n"
        "Я помогу вам отслеживать ваши тренировки, ставить цели "
        "и следить за прогрессом.\n\n"
        "Используйте кнопки ниже для навигации:"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=main_menu()
    )