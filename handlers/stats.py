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

stats_router = Router()

@stats_router.message(F.text.in_(("📊 Статистика", "/statistics")))
@stats_router.message(Command("statistics"))
async def statistics_menu(message: Message):
    await message.answer(
        "Выберите период для статистики:",
        reply_markup=periods_keyboard()
    )


@stats_router.callback_query(F.data.startswith("period_"))
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

    await callback.message.answer(
        stats_text,
        reply_markup=back_button()
    )
    await callback.answer()


@stats_router.message(Command("compare"))
async def compare_stats(message: Message, stats_service: StatsService, user_service: UserService):
    user = await user_service.get_user(message.from_user.id)

    try:
        comparison = await stats_service.compare_periods(user.id, "week")

        diff = comparison['difference']
        diff_text = ""

        for metric, value in diff.items():
            if value > 0:
                diff_text += f"📈 {metric}: +{value}\n"
            elif value < 0:
                diff_text += f"📉 {metric}: {value}\n"
            else:
                diff_text += f"➡️ {metric}: без изменений\n"

        response = (
            "Сравнение текущей недели с предыдущей:\n\n"
            f"{diff_text}"
        )

        await message.answer(response)

    except Exception as e:
        await message.answer(f"Ошибка при сравнении статистики: {e}")


@stats_router.message(Command("export_data"))
async def export_data(message: Message, workout_service: WorkoutService, user_service: UserService):
    user = await user_service.get_user(message.from_user.id)
    workouts = await workout_service.get_workouts(user.id)

    if not workouts:
        await message.answer("У вас пока нет тренировок для экспорта")
        return

    csv_data = "Дата,Тип,Длительность (мин),Дистанция (км),Калории,Заметки\n"
    for workout in workouts:
        csv_data += (
            f"{workout.date.strftime('%Y-%m-%d')},"
            f"{workout.workout_type},"
            f"{workout.duration or ''},"
            f"{workout.distance or ''},"
            f"{workout.calories or ''},"
            f"\"{workout.notes or ''}\"\n"
        )

    await message.answer(
        f"Данные для экспорта ({len(workouts)} тренировок):\n\n"
        "Формат CSV:\n"
        f"{csv_data[:500]}..." if len(csv_data) > 500 else csv_data
    )

@stats_router.callback_query(F.data == "back")
async def back_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню",
        reply_markup=main_menu()
    )
    await callback.answer()