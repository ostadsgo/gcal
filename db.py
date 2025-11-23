""" module for CRUD operation on the data of the app."""

import sqlite3
from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data.db"


class CalendarDB:
    def __init__(self):
        self.db_path = Path(DB_PATH)
        self.conn = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # calendar table
        calendar_table_sql = """
        CREATE TABLE IF NOT EXISTS calendars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color text default '#FF0000'
        )
        """
        event_table_sql = """
        CREATE TABLE IF NOT EXISTS events (
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

        )
        """
        tags_table_sql = """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        """
        
        event_tags_table_sql = """
        CREATE TABLE IF NOT EXISTS event_tags (
            event_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (event_id, tag_id),
            FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """
        self.execute(calendar_table_sql)
        self.execute(event_table_sql)
        self.execute(tags_table_sql)
        self.execute(event_tags_table_sql)


    def close(self):
        if self.conn:
            self.conn.close()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()


if __name__ == "__main__":
    db = CalendarDB()
    print(f"Database created at: {db.db_path}")
    print("Tables and indexes created successfully.")
    db.close()
