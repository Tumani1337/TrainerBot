from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import WORKOUT_TYPES
from keyboards import (
    workout_types,
    periods_keyboard,
    confirm_cancel,
    back_button
)
from service import WorkoutService, UserService
from models import Workout
from datetime import datetime
import re

router = Router()

class AddWorkout(StatesGroup):
    selecting_type = State()
    entering_date = State()
    entering_duration = State()
    entering_distance = State()
    entering_calories = State()
    entering_notes = State()
    confirmation = State()

@router.message(F.text.in_(("➕ Добавить тренировку", "/add_workout")))
@router.message(Command("add_workout"))
async def add_workout_start(message: Message, state: FSMContext):
    await state.set_state(AddWorkout.selecting_type)
    await message.answer(
        "Выберите тип тренировки:",
        reply_markup=workout_types()
    )

@router.message(AddWorkout.selecting_type, F.text.in_(WORKOUT_TYPES))
async def workout_type_selected(message: Message, state: FSMContext):
    await state.update_data(workout_type=message.text)
    await state.set_state(AddWorkout.entering_date)
    await message.answer(
        "Введите дату тренировки (ДД.ММ.ГГГГ или 'сегодня'):",
        reply_markup=back_button()
    )
