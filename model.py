""" `model.py` - modules for CRUD operation on the data of the app."""

import sqlite3
import os
from pathlib import Path

import icalendar

BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"
DB_PATH = BASE_DIR / "data.db"

SECONDS_PER_HOUR = 3600

class CalendarModel:
    def __init__(self, db):
        self.db = db


    def get_id_by_name(self, name):
        sql = "SELECT id FROM calendars WHERE name = ?"
        result = self.db.fetch_one(sql, (name,))
        return result['id'] if result else None

    def exists(self, name):
        return self.get_id_by_name(name) is not None



class EventModel:
    def __init__(self, db):
        self.db = db
   


class TagModel:
    def __init__(self, db):
        self.db = db

    


class DatabaseManager:
    is_table_created = False

    def __init__(self):
        self.db_path = Path(DB_PATH)
        self.conn = None
        self.calendar = None
        self.event = None
        self.tag = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")

        self.calendar = CalendarModel(self)
        self.event = EventModel(self)
        self.tag = TagModel(self)

        if not DatabaseManager.is_table_created:
            self.create_tables()
            DatabaseManager.is_table_created = True

    def create_tables(self):
        self.calendar.create()
        self.event.create()
        self.tag.create()


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


