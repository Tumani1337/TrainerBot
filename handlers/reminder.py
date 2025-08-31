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


@router.callback_query(F.data == "list_reminders")
async def list_reminders(callback: CallbackQuery, reminder_service: ReminderService, user_service: UserService):
    user = await user_service.get_user(callback.from_user.id)
    reminders = await reminder_service.get_user_reminders(user.id)

    if not reminders:
        await callback.message.edit_text(
            "У вас пока нет напоминаний.",
            reply_markup=reminders_management()
        )
        return

    reminders_text = "Ваши напоминания:\n\n"
    for reminder in reminders:
        status = "✅" if reminder.is_active else "❌"
        days_names = []
        days_map = {"1": "Пн", "2": "Вт", "3": "Ср", "4": "Чт", "5": "Пт", "6": "Сб", "7": "Вс"}

        for day in reminder.days_of_week.split(','):
            days_names.append(days_map.get(day, day))

        reminders_text += (
            f"{status} {reminder.time} - {', '.join(days_names)}\n"
            f"ID: {reminder.id} | Статус: {'активно' if reminder.is_active else 'неактивно'}\n\n"
        )

    reminders_text += "Используйте /toggle_reminder <ID> для включения/выключения"

    await callback.message.edit_text(
        reminders_text,
        reply_markup=reminders_management()
    )
    await callback.answer()