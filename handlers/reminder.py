from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from keyboards import (
    main_menu,
    reminders_management,
    days_of_week_keyboard,
    back_button,
    confirm_cancel
)
from service import ReminderService, UserService
from models import Reminder

router = Router()

class AddReminder(StatesGroup):
    selecting_days = State()
    entering_time = State()
    confirmation = State()

@router.message(F.text.in_(("⏰ Напоминания", "/reminder")))
@router.message(Command("reminder"))
async def reminders_menu(message: Message):
    await message.answer(
        "Управление напоминаниями:",
        reply_markup=reminders_management()
    )

@router.callback_query(F.data == "new_reminder")
async def new_reminder_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddReminder.selecting_days)
    await callback.message.edit_text(
        "Выберите дни недели для напоминаний:",
        reply_markup=days_of_week_keyboard()
    )
    await callback.answer()