""" `model.py` - modules for CRUD operation on the data of the app."""

import sqlite3
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db"
DB_FILE = DB_PATH / "data.db"


class CalendarModel:
    def __init__(self, db):
        self.db = db

    def get_calendars(self):
        sql_cmd = """ SELECT id, name FROM calendars;"""
        rows = self.db.fetch_all(sql_cmd)
        return rows

    
class DatabaseManager:

    def __init__(self):
        self.db_path = Path(DB_FILE)
        self.conn = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def execute(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Data base error {e}")
            self.conn.rollback()
            raise

    def fetch_one(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

