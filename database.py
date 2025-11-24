""" module for CRUD operation on the data of the app."""

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.db"

class CalendarTable:
    def __init__(self, db):
        self.db = db

    def create(self):
        sql = """ CREATE TABLE IF NOT EXISTS calendars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color text default '#FF0000'
        );
        """
        print("Table :: calendar")
        self.db.execute(sql)

    def insert(self, name, color):
        sql = """ 
            INSERT INTO calendars (name, color)
            VALUES (?, ?);
        """
        self.db.execute(sql, (name, color))
        return self.get_id_by_name(name)

    def get_id_by_name(self, name):
        sql = "SELECT id FROM calendars WHERE name = ?"
        result = self.db.fetch_one(sql, (name,))
        return result['id'] if result else None

    def update(self):
        pass

    def delete(self):
        pass

    def read(self):
        pass


class EventTable:
    def __init__(self, db):
        self.db = db

    def create(self):
        sql = """ CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calendar_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            dtstart TEXT NOT NULL,
            dtend TEXT NOT NULL,
            duration REAL NOT NULL,
            area TEXT,
            project TEXT,
            difficulty TEXT,
            detail TEXT,
            FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE
        );
        """
        print("Table :: events")
        self.db.execute(sql)

    def insert(self):
        pass

    def update(self):
        pass

    def get(self):
        pass

    def getall(self):
        pass



class TagTable:
    def __init__(self, db):
        self.db = db

    def create(self):
        sql = """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
        self.db.execute(sql)
        print("Table :: tags")
        
        sql = """
        CREATE TABLE IF NOT EXISTS event_tags (
            event_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (event_id, tag_id),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """
        self.db.execute(sql)
        print("Table :: event_tags")




class CalendarDB:
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

        self.calendar = CalendarTable(self)
        self.event = EventTable(self)
        self.tag = TagTable(self)

        if not CalendarDB.is_table_created:
            self.create_tables()
            CalendarDB.is_table_created = True

    def create_tables(self):
        self.calendar.create()
        self.event.create()
        self.tag.create()


    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

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

