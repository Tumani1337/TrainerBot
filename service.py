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

    async def get_user(self, telegram_id: int) -> Optional[User]:
        return await self.user_repo.get_user_by_telegram_id(telegram_id)

    async def update_user_activity(self, telegram_id: int):
        await self.user_repo.update_user_activity(telegram_id)


class WorkoutService:
    def __init__(self, workout_repo: WorkoutRepo, goal_repo: GoalRepo):
        self.workout_repo = workout_repo
        self.goal_repo = goal_repo

    async def add_workout(self, user_id: int, workout_type: str, date: datetime,
                          duration: Optional[float] = None,
                          distance: Optional[float] = None,
                          calories: Optional[int] = None,
                          notes: Optional[str] = None) -> Workout:
        workout = await self.workout_repo.add_workout(
            user_id, workout_type, date, duration, distance, calories, notes
        )
        await self._update_goals_progress(user_id, workout_type, duration, distance)
        return workout

    async def _update_goals_progress(self, user_id: int, workout_type: str,
                                     duration: Optional[float], distance: Optional[float]):
        goals = await self.goal_repo.get_user_goals(user_id, include_completed=False)

        for goal in goals:
            if goal.workout_type and goal.workout_type != workout_type:
                continue

            if "дистанция" in goal.description.lower() and distance:
                new_value = goal.current_value + distance
                await self.goal_repo.update_goal_progress(goal.id, new_value)

            elif "время" in goal.description.lower() and duration:
                new_value = goal.current_value + duration
                await self.goal_repo.update_goal_progress(goal.id, new_value)

            elif "количество" in goal.description.lower():
                new_value = goal.current_value + 1
                await self.goal_repo.update_goal_progress(goal.id, new_value)

    async def get_workouts(self, user_id: int, period: Optional[str] = None,
                           workout_type: Optional[str] = None) -> List[Workout]:
        return await self.workout_repo.get_workouts_by_user(user_id, period, workout_type)




