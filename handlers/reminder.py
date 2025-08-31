from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
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


@router.callback_query(AddReminder.selecting_days, F.data.startswith("reminder_day_"))
async def reminder_days_selected(callback: CallbackQuery, state: FSMContext):
    selected_day = callback.data.split("_")[2]

    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if selected_day in selected_days:
        selected_days.remove(selected_day)
    else:
        selected_days.append(selected_day)

    await state.update_data(selected_days=selected_days)

    days_map = {"1": "Пн", "2": "Вт", "3": "Ср", "4": "Чт", "5": "Пт", "6": "Сб", "7": "Вс"}
    selected_days_names = [days_map.get(day, day) for day in selected_days]

    if selected_days:
        text = f"Выбраны дни: {', '.join(selected_days_names)}\n\nНажмите '✅ Готово' когда закончите выбор"
    else:
        text = "Выберите дни недели для напоминаний:"

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()

    days = [
        ("Пн", "1"), ("Вт", "2"), ("Ср", "3"),
        ("Чт", "4"), ("Пт", "5"), ("Сб", "6"), ("Вс", "7")
    ]

    for day, num in days:
        emoji = "✅" if num in selected_days else "⚪"
        builder.add(InlineKeyboardButton(
            text=f"{emoji} {day}",
            callback_data=f"reminder_day_{num}"
        ))

    builder.adjust(7)

    if selected_days:
        builder.row(InlineKeyboardButton(
            text="✅ Готово",
            callback_data="reminder_days_done"
        ))

    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_reminders"
    ))

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(AddReminder.selecting_days, F.data == "reminder_days_done")
async def reminder_days_done(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get('selected_days', [])

    if not selected_days:
        await callback.answer("Выберите хотя бы один день")
        return

    await state.set_state(AddReminder.entering_time)
    await callback.message.edit_text(
        "Введите время напоминания в формате ЧЧ:MM (например, 09:00):",
        reply_markup=back_button()
    )
    await callback.answer()


@router.message(AddReminder.entering_time)
async def reminder_time_entered(message: Message, state: FSMContext):
    time_str = message.text.strip()

    try:
        datetime.strptime(time_str, "%H:%M")
    except ValueError:
        await message.answer("Неверный формат времени. Используйте ЧЧ:MM (например, 09:00)")
        return

    await state.update_data(time=time_str)
    await state.set_state(AddReminder.confirmation)

    data = await state.get_data()
    selected_days = data['selected_days']

    days_map = {"1": "Пн", "2": "Вт", "3": "Ср", "4": "Чт", "5": "Пт", "6": "Сб", "7": "Вс"}
    selected_days_names = [days_map.get(day, day) for day in selected_days]

    reminder_info = (
        "Проверьте данные напоминания:\n\n"
        f"Дни: {', '.join(selected_days_names)}\n"
        f"Время: {time_str}\n\n"
        "Всё верно?"
    )

    await message.answer(
        reminder_info,
        reply_markup=confirm_cancel()
    )
