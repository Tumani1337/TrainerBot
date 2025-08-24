from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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
