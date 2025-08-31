from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from keyboards import (
    main_menu,
    goals_management,
    workout_types,
    back_button,
    confirm_cancel
)
from service import GoalService, UserService
from models import Goal

router = Router()

class AddGoal(StatesGroup):
    entering_description = State()
    selecting_type = State()
    entering_target = State()
    selecting_period = State()
    confirmation = State()

@router.message(F.text.in_(("🎯 Мои цели", "/set_goal", "/view_goals")))
@router.message(Command("set_goal", "view_goals"))
async def goals_menu(message: Message):
    await message.answer(
        "Управление целями:",
        reply_markup=goals_management()
    )