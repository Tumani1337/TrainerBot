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

@router.message(F.text.in_(("📊 Статистика", "/statistics")))
@router.message(Command("statistics"))
async def statistics_menu(message: Message):
    await message.answer(
        "Выберите период для статистики:",
        reply_markup=periods_keyboard()
    )


@router.callback_query(F.data.startswith("period_"))
async def stats_period_selected(callback: CallbackQuery,
                                workout_service: WorkoutService,
                                user_service: UserService):
    period = callback.data.split("_")[1]
    user = await user_service.get_user(callback.from_user.id)

    stats = await workout_service.get_workout_statistics(user.id, period)

    stats_text = (
        f"📊 Статистика за {period}:\n\n"
        f"Количество тренировок: {stats['total_workouts']}\n"
        f"Общая дистанция: {stats['total_distance']:.1f} км\n"
        f"Общее время: {stats['total_duration']:.0f} мин\n"
        f"Сожжено калорий: {stats['total_calories'] or 0}\n\n"
        f"Средняя дистанция: {stats['avg_distance']:.1f} км/тренировка\n"
        f"Среднее время: {stats['avg_duration']:.0f} мин/тренировка\n"
        f"Средние калории: {stats['avg_calories']:.0f}/тренировка"
    )

    await callback.message.edit_text(
        stats_text,
        reply_markup=back_button()
    )
    await callback.answer()

