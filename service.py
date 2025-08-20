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

    async def get_workout_statistics(self, user_id: int, period: str,
                                     workout_type: Optional[str] = None) -> dict:
        workouts = await self.get_workouts(user_id, period, workout_type)

        if not workouts:
            return {
                "total_workouts": 0,
                "total_distance": 0,
                "total_duration": 0,
                "total_calories": 0,
                "avg_distance": 0,
                "avg_duration": 0,
                "avg_calories": 0
            }

        total_distance = sum(w.distance or 0 for w in workouts)
        total_duration = sum(w.duration or 0 for w in workouts)
        total_calories = sum(w.calories or 0 for w in workouts)

        return {
            "total_workouts": len(workouts),
            "total_distance": total_distance,
            "total_duration": total_duration,
            "total_calories": total_calories,
            "avg_distance": total_distance / len(workouts),
            "avg_duration": total_duration / len(workouts),
            "avg_calories": total_calories / len(workouts) if total_calories else 0
        }

class GoalService:
    def __init__(self, goal_repo: GoalRepo):
        self.goal_repo = goal_repo

    async def add_goal(self, user_id: int, description: str, target_value: float,
                       target_date: datetime, workout_type: Optional[str] = None) -> Goal:
        return await self.goal_repo.add_goal(
            user_id, description, target_value, target_date, workout_type
        )

    async def get_user_goals(self, user_id: int, include_completed: bool = False) -> List[Goal]:
        goals = await self.goal_repo.get_user_goals(user_id, include_completed)

        for goal in goals:
            if not goal.is_completed and goal.current_value >= goal.target_value:
                goal.is_completed = True

        return goals

    async def get_completed_goals(self, user_id: int) -> List[Goal]:
        return await self.goal_repo.get_user_goals(user_id, include_completed=True)

class ReminderService:
    def __init__(self, reminder_repo: ReminderRepo):
            self.reminder_repo = reminder_repo

    async def add_reminder(self, user_id: int, days_of_week: List[int], time: str) -> Reminder:
        days_str = ",".join(map(str, days_of_week))
        return await self.reminder_repo.add_reminder(user_id, days_str, time)

    async def get_user_reminders(self, user_id: int) -> List[Reminder]:
        return await self.reminder_repo.get_user_reminders(user_id)

    async def toggle_reminder(self, reminder_id: int, is_active: bool):
        await self.reminder_repo.toggle_reminder(reminder_id, is_active)

    async def get_active_reminders(self) -> List[Reminder]:
        return await self.reminder_repo.get_active_reminders()

    async def get_reminders_for_time(self, target_time: str) -> List[Reminder]:
        # Получаем напоминания, которые должны сработать в указанное время
        all_active = await self.get_active_reminders()
        return [r for r in all_active if r.time == target_time]

    async def get_todays_reminders(self) -> List[Reminder]:
        # Получаем напоминания, которые должны сработать сегодня
        from datetime import datetime
        today_weekday = str(datetime.now().weekday())  # 0-6 (пн-вс)
        all_active = await self.get_active_reminders()

        todays_reminders = []
        for reminder in all_active:
            days = reminder.days_of_week.split(',')
            if today_weekday in days:
                todays_reminders.append(reminder)

        return todays_reminders


class StatsService:
    def __init__(self, workout_repo: WorkoutRepo, reminder_repo: ReminderRepo):
        self.workout_repo = workout_repo
        self.reminder_repo = reminder_repo

    async def compare_periods(self, user_id: int, period: str) -> dict:
        if period not in ["week", "month"]:
            raise ValueError("Invalid period for comparison")

        current_workouts = await self.workout_repo.get_workouts_by_user(
            user_id, period
        )
        previous_workouts = await self.workout_repo.get_workouts_by_user(
            user_id, f"previous_{period}"
        )

        def calculate_stats(workouts):
            return {
                "count": len(workouts),
                "distance": sum(w.distance or 0 for w in workouts),
                "duration": sum(w.duration or 0 for w in workouts),
                "calories": sum(w.calories or 0 for w in workouts)
            }

        current_stats = calculate_stats(current_workouts)
        previous_stats = calculate_stats(previous_workouts)

        return {
            "current": current_stats,
            "previous": previous_stats,
            "difference": {
                "count": current_stats["count"] - previous_stats["count"],
                "distance": current_stats["distance"] - previous_stats["distance"],
                "duration": current_stats["duration"] - previous_stats["duration"],
                "calories": current_stats["calories"] - previous_stats["calories"]
            }
        }

    async def get_reminders_stats(self, user_id: int) -> dict:
        reminders = await self.reminder_repo.get_user_reminders(user_id)
        active = sum(1 for r in reminders if r.is_active)
        inactive = len(reminders) - active

        next_reminder = None
        now = datetime.now().time()

        for r in reminders:
            if r.is_active:
                reminder_time = datetime.strptime(r.time, "%H:%M").time()
                if reminder_time > now:
                    next_reminder = r
                    break

        return {
            "total": len(reminders),
            "active": active,
            "inactive": inactive,
            "next_reminder": next_reminder
        }

