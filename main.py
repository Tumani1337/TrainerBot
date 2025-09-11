import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DB_PATH
from repo import UserRepo, WorkoutRepo, GoalRepo, ReminderRepo
from service import UserService, WorkoutService, GoalService, ReminderService, StatsService
from keyboards import main_menu
from handlers.__init__ import main_router


async def main():
    bot = Bot(BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    user_repo = UserRepo(DB_PATH)
    workout_repo = WorkoutRepo(DB_PATH)
    goal_repo = GoalRepo(DB_PATH)
    reminder_repo = ReminderRepo(DB_PATH)

    user_service = UserService(user_repo)
    goal_service = GoalService(goal_repo, bot)
    workout_service = WorkoutService(workout_repo, goal_repo)
    reminder_service = ReminderService(reminder_repo)
    stats_service = StatsService(workout_repo)

    await user_repo.create_table()
    await workout_repo.create_table()
    await goal_repo.create_table()
    await reminder_repo.create_table()

    dp.workflow_data.update(
        user_service=user_service,
        workout_service=workout_service,
        goal_service=goal_service,
        reminder_service=reminder_service,
        stats_service=stats_service)

    dp.include_router(main_router)

    print("Бот запущен!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())