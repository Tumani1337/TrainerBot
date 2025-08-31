from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta

from config import WORKOUT_TYPES
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


@router.message(AddGoal.selecting_type)
async def goal_type_selected(message: Message, state: FSMContext):
    workout_type = message.text.strip()
    if workout_type.lower() == "пропустить":
        workout_type = None
    elif workout_type not in WORKOUT_TYPES:
        await message.answer("Пожалуйста, выберите тип из предложенных вариантов")
        return

    await state.update_data(workout_type=workout_type)
    await state.set_state(AddGoal.entering_target)

    data = await state.get_data()
    description = data['description']

    if any(word in description.lower() for word in ['км', 'километр', 'дистанц']):
        unit = "км"
    elif any(word in description.lower() for word in ['мин', 'время', 'длительн']):
        unit = "минут"
    else:
        unit = "раз"

    await state.update_data(unit=unit)
    await message.answer(
        f"Введите целевое значение (в {unit}):",
        reply_markup=back_button()
    )


@router.message(AddGoal.entering_target)
async def goal_target_entered(message: Message, state: FSMContext):
    try:
        target_value = float(message.text.strip())
        if target_value <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите положительное число")
        return

    await state.update_data(target_value=target_value)
    await state.set_state(AddGoal.selecting_period)

    await message.answer(
        "Выберите срок для цели:\n"
        "1 - неделя\n"
        "2 - месяц\n"
        "3 - 3 месяца\n"
        "4 - год",
        reply_markup=back_button()
    )


@router.message(AddGoal.selecting_period)
async def goal_period_selected(message: Message, state: FSMContext):
    period_choice = message.text.strip()
    today = datetime.now()

    if period_choice == "1":
        target_date = today + timedelta(weeks=1)
        period_text = "неделю"
    elif period_choice == "2":
        target_date = today + timedelta(days=30)
        period_text = "месяц"
    elif period_choice == "3":
        target_date = today + timedelta(days=90)
        period_text = "3 месяца"
    elif period_choice == "4":
        target_date = today + timedelta(days=365)
        period_text = "год"
    else:
        await message.answer("Пожалуйста, выберите вариант из предложенных (1-4)")
        return

    await state.update_data(target_date=target_date, period_text=period_text)
    await state.set_state(AddGoal.confirmation)

    data = await state.get_data()

    goal_info = (
        "Проверьте данные цели:\n\n"
        f"Описание: {data['description']}\n"
        f"Тип активности: {data.get('workout_type', 'любая')}\n"
        f"Целевое значение: {data['target_value']} {data['unit']}\n"
        f"Срок: {period_text} (до {target_date.strftime('%d.%m.%Y')})\n\n"
        "Всё верно?"
    )

    await message.answer(
        goal_info,
        reply_markup=confirm_cancel()
    )


@router.message(AddGoal.confirmation, F.text.in_(("✅ Подтвердить", "❌ Отменить")))
async def goal_confirmation(message: Message, state: FSMContext,
                            goal_service: GoalService, user_service: UserService):
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Создание цели отменено", reply_markup=main_menu())
        return

    data = await state.get_data()
    user = await user_service.get_user(message.from_user.id)

    try:
        goal = await goal_service.add_goal(
            user_id=user.id,
            description=data['description'],
            target_value=data['target_value'],
            target_date=data['target_date'],
            workout_type=data.get('workout_type')
        )

        await message.answer(
            "✅ Цель успешно установлена! Вы получите уведомление при её достижении.",
            reply_markup=main_menu()
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при создании цели: {e}",
            reply_markup=main_menu()
        )
    finally:
        await state.clear()