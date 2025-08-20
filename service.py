from datetime import datetime, timedelta
from typing import List, Optional
from models import User, Workout, Goal, Reminder
from repo import UserRepo, WorkoutRepo, GoalRepo, ReminderRepo
import config

class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    async def register_user(self, telegram_id: int, name: str) -> User:
        existing_user = await self.user_repo.get_user_by_telegram_id(telegram_id)
        if existing_user:
            return existing_user
        return await self.user_repo.add_user(telegram_id, name)
