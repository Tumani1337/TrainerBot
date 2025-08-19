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