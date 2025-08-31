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

@router.callback_query(F.data == "new_goal")
async def new_goal_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddGoal.entering_description)
    await callback.message.edit_text(
        "Введите описание цели (например: 'Пробежать 50 км'):",
        reply_markup=back_button()
    )
    await callback.answer()


@router.callback_query(F.data == "list_goals")
async def list_goals(callback: CallbackQuery, goal_service: GoalService, user_service: UserService):
    user = await user_service.get_user(callback.from_user.id)
    goals = await goal_service.get_user_goals(user.id, telegram_id=callback.from_user.id)

    if not goals:
        await callback.message.edit_text(
            "У вас пока нет целей. Создайте первую цель!",
            reply_markup=goals_management()
        )
        return

    goals_text = ""
    for goal in goals:
        progress_percent = (goal.current_value / goal.target_value * 100) if goal.target_value > 0 else 0
        status = "✅" if goal.is_completed else "⏳"
        goals_text += (
            f"{status} {goal.description}\n"
            f"Прогресс: {goal.current_value:.1f}/{goal.target_value:.1f} "
            f"({progress_percent:.0f}%)\n"
            f"Срок: {goal.target_date.strftime('%d.%m.%Y')}\n"
        )
        if goal.workout_type:
            goals_text += f"Тип: {goal.workout_type}\n"
        goals_text += "\n"

    await callback.message.edit_text(
        f"Ваши цели:\n\n{goals_text}",
        reply_markup=goals_management()
    )
    await callback.answer()


@router.message(AddGoal.entering_description)
async def goal_description_entered(message: Message, state: FSMContext):
    description = message.text.strip()
    if len(description) < 5:
        await message.answer("Описание должно содержать минимум 5 символов")
        return

    await state.update_data(description=description)
    await state.set_state(AddGoal.selecting_type)
    await message.answer(
        "Выберите тип активности для цели (или пропустите для общей цели):",
        reply_markup=workout_types()
    )