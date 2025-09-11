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