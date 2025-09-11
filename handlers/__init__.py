from aiogram import Router

main_router = Router()

from .start import start_router as start_router
from .workouts import workouts_router as workouts_router
from .goals import goals_router as goals_router
from .reminder import reminder_router as reminders_router
from .stats import stats_router as stats_router
from .help import help_router as help_router

main_router.include_router(start_router)
main_router.include_router(workouts_router)
main_router.include_router(goals_router)
main_router.include_router(reminders_router)
main_router.include_router(stats_router)
main_router.include_router(help_router)