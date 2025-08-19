import aiosqlite
from datetime import datetime
from typing import List, Optional
from models import User, Workout, Goal, Reminder

class UserRepo:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    name TEXT,
                    registration_date TEXT,
                    last_activity TEXT
                )
            """)
            await db.commit()

    async def add_user(self, telegram_id: int, name: str) -> User:
        registration_date = datetime.now().isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO users (telegram_id, name, registration_date, last_activity)
                VALUES (?, ?, ?, ?)
            """, (telegram_id, name, registration_date, registration_date))
            await db.commit()
            return User(
                id=cursor.lastrowid,
                telegram_id=telegram_id,
                name=name,
                registration_date=datetime.fromisoformat(registration_date),
                last_activity=datetime.fromisoformat(registration_date)
            )

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, telegram_id, name, registration_date, last_activity
                FROM users WHERE telegram_id = ?
            """, (telegram_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        telegram_id=row[1],
                        name=row[2],
                        registration_date=datetime.fromisoformat(row[3]),
                        last_activity=datetime.fromisoformat(row[4])
                    )
                return None

    async def update_user_activity(self, telegram_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE users SET last_activity = ? WHERE telegram_id = ?
            """, (datetime.now().isoformat(), telegram_id))
            await db.commit()

class WorkoutRepo:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_table(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS workouts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    workout_type TEXT,
                    date TEXT,
                    duration REAL,
                    distance REAL,
                    calories INTEGER,
                    notes TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            await db.commit()

    async def add_workout(self, user_id: int, workout_type: str, date: datetime,
                          duration: Optional[float] = None,
                          distance: Optional[float] = None,
                          calories: Optional[int] = None,
                          notes: Optional[str] = None) -> Workout:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO workouts (user_id, workout_type, date, duration, distance, calories, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, workout_type, date.isoformat(), duration, distance, calories, notes))
            await db.commit()
            return Workout(
                id=cursor.lastrowid,
                user_id=user_id,
                workout_type=workout_type,
                date=date,
                duration=duration,
                distance=distance,
                calories=calories,
                notes=notes
            )