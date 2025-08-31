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
