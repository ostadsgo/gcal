"""`model.py` - modules for CRUD operation on the data of the app."""

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db"
DB_FILE = DB_PATH / "data.db"


class CalendarModel:
    def __init__(self, db):
        self.db = db

    def get_calendars(self):
        query = """
            SELECT 
                c.id AS calendar_id,
                c.name AS calendar_name,
                c.color AS calendar_color,
                COALESCE(SUM(e.duration), 0) AS total_duration, 
                COUNT(e.id) AS total_events
            FROM calendars c
            LEFT JOIN events e ON e.calendar_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name
        """
        rows = self.db.fetch_all(query)
        return [
            {
                "calendar_name": row["calendar_name"],
                "calendar_color": row["calendar_color"],
                "total_duration": row["total_duration"],
                "total_events": row["total_events"],
            }
            for row in rows
        ]

class AreaModel:
    def __init__(self, db):
        self.db = db

    def get_areas(self):
        query = """
            SELECT 
                c.name as calendar_name,
                a.name as area_name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN areas a ON e.area_id = a.id
            GROUP BY c.name, a.name
            ORDER BY c.name, total_hours DESC;
        """
        rows = self.db.fetch_all(query)
        return [
            {
                "calendar_name": row["calendar_name"],
                "area_name": row["area_name"],
                "event_count": row["event_count"],
                "total_hours": row["total_hours"],
            }
            for row in rows
        ]


class ProjectModel:
    def __init__(self, db):
        self.db = db

    def get_projects(self):
        query = """
            SELECT 
                c.name as calendar_name,
                p.name as project_name,
                a.name as area_name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN projects p ON e.project_id = p.id
            LEFT JOIN areas a ON p.area_id = a.id
            GROUP BY c.name, p.name, a.name
            ORDER BY total_hours DESC;
        """
        rows = self.db.fetch_all(query)
        return [
            {
                "calendar_name": row["calendar_name"],
                "project_name": row["project_name"],
                "event_count": row["event_count"],
                "total_hours": row["total_hours"],
            }
            for row in rows
        ]

class DatabaseManager:

    def __init__(self):
        self.db_path = Path(DB_FILE)
        self.conn = None
        self.calendar_model = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Model objects to access in app.py to send to controllers.
        self.calendar_model = CalendarModel(self)
        self.area_model = AreaModel(self)
        self.project_model = ProjectModel(self)

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

