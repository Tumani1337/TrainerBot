import asyncio

from aiogram import Bot,Dispatcher
from config import BOT_TOKEN
from handlers.start import start_router
from handlers.workouts import workouts_router
from handlers.goals import goals_router
from handlers.reminder import reminder_router
from handlers.start import start_router
from handlers.help import help_router

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(start_router,workouts_router,goals_router,reminder_router,help_router,start_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())