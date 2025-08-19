from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    telegram_id: int
    name: str
    registration_date: datetime
    last_activity: datetime

@dataclass
class Workout:
    id: int
    user_id: int
    workout_type: str
    date: datetime
    duration: Optional[float] = None  # в минутах
    distance: Optional[float] = None  # в км
    calories: Optional[int] = None
    notes: Optional[str] = None

@dataclass
class Goal:
    id: int
    user_id: int
    description: str
    target_value: float
    current_value: float
    target_date: datetime
    is_completed: bool
    workout_type: Optional[str] = None

@dataclass
class Reminder:
    id: int
    user_id: int
    days_of_week: str  # например: "1,3,5" для пн, ср, пт
    time: str  # в формате "HH:MM"
    is_active: bool