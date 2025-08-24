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


@router.message(AddWorkout.entering_date)
async def workout_date_entered(message: Message, state: FSMContext):
    date_str = message.text.strip().lower()

    if date_str == "сегодня":
        date = datetime.now()
    else:
        try:
            date = datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ или 'сегодня'")
            return

    await state.update_data(date=date)
    await state.set_state(AddWorkout.entering_duration)
    await message.answer(
        "Введите продолжительность тренировки в минутах (или пропустите):",
        reply_markup=back_button()
    )


@router.message(AddWorkout.entering_duration)
async def workout_duration_entered(message: Message, state: FSMContext):
    duration = message.text.strip()

    if duration.lower() == "пропустить":
        await state.update_data(duration=None)
    else:
        try:
            duration = float(duration)
            if duration <= 0:
                raise ValueError
            await state.update_data(duration=duration)
        except ValueError:
            await message.answer("Пожалуйста, введите число больше 0 (или 'пропустить')")
            return

    await state.set_state(AddWorkout.entering_distance)
    await message.answer(
        "Введите дистанцию в км (или пропустите):",
        reply_markup=back_button()
    )


@router.message(AddWorkout.entering_distance)
async def workout_distance_entered(message: Message, state: FSMContext):
    distance = message.text.strip()

    if distance.lower() == "пропустить":
        await state.update_data(distance=None)
    else:
        try:
            distance = float(distance)
            if distance <= 0:
                raise ValueError
            await state.update_data(distance=distance)
        except ValueError:
            await message.answer("Пожалуйста, введите число больше 0 (или 'пропустить')")
            return

    await state.set_state(AddWorkout.entering_calories)
    await message.answer(
        "Введите количество калорий (или пропустите):",
        reply_markup=back_button()
    )


@router.message(AddWorkout.entering_calories)
async def workout_calories_entered(message: Message, state: FSMContext):
    calories = message.text.strip()

    if calories.lower() == "пропустить":
        await state.update_data(calories=None)
    else:
        try:
            calories = int(calories)
            if calories <= 0:
                raise ValueError
            await state.update_data(calories=calories)
        except ValueError:
            await message.answer("Пожалуйста, введите целое число больше 0 (или 'пропустить')")
            return

    await state.set_state(AddWorkout.entering_notes)
    await message.answer(
        "Добавьте заметки к тренировке (или пропустите):",
        reply_markup=back_button()
    )


@router.message(AddWorkout.entering_notes)
async def workout_notes_entered(message: Message, state: FSMContext):
    notes = message.text.strip()
    if notes.lower() == "пропустить":
        notes = None

    await state.update_data(notes=notes)
    await state.set_state(AddWorkout.confirmation)

    data = await state.get_data()

    workout_info = (
        "Проверьте данные тренировки:\n\n"
        f"Тип: {data['workout_type']}\n"
        f"Дата: {data['date'].strftime('%d.%m.%Y')}\n"
        f"Длительность: {data.get('duration', 'не указано')} мин\n"
        f"Дистанция: {data.get('distance', 'не указано')} км\n"
        f"Калории: {data.get('calories', 'не указано')}\n"
        f"Коментарий: {data.get('notes', 'не указано')}\n\n"
        "Всё верно?"
    )

    await message.answer(
        workout_info,
        reply_markup=confirm_cancel()
    )