# models.py
from dataclasses import dataclass
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db"
DB_FILE = DB_PATH / "data.db"


# Domain objects (data classes)
@dataclass
class Calendar:
    """Calendar with statistics."""

    name: str
    color: str
    total_duration: float
    total_events: int

    def format_duration(self) -> str:
        """Format duration as human-readable string."""
        hours = int(self.total_duration)
        minutes = int((self.total_duration - hours) * 60)
        return f"{hours}h {minutes}m"


@dataclass
class Area:
    """Area with statistics."""

    calendar_name: str
    name: str
    event_count: int
    total_hours: float


@dataclass
class Project:
    """Project with statistics."""

    calendar_name: str
    name: str
    area_name: str
    event_count: int
    total_hours: float


# Models
class CalendarModel:
    def __init__(self, db):
        self.db = db

    def get_calendars_by_usage(self) -> list[Calendar]:
        """Get calendars sorted by total duration (most used first)."""
        query = """
            SELECT 
                c.name,  
                c.color,  
                COALESCE(SUM(e.duration), 0) AS total_duration, 
                COUNT(e.id) AS total_events
            FROM calendars c
            LEFT JOIN events e ON e.calendar_id = c.id
            GROUP BY c.id, c.name, c.color
            ORDER BY total_duration DESC 
            """
        rows = self.db.fetch_all(query)
        return [Calendar(**row) for row in rows]

    def get_calendars_alphabetically(self) -> list[Calendar]:
        """Get calendars sorted alphabetically by name."""
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
        return [Calendar(**row) for row in rows]


class AreaModel:
    def __init__(self, db):
        self.db = db

    def get_top_areas(self, limit: int = 10) -> list[Area]:
        """Get top areas by total hours."""
        query = """
            SELECT 
                c.name as calendar_name,
                a.name as name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN areas a ON e.area_id = a.id
            GROUP BY c.name, a.name
            ORDER BY total_hours DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (limit,))
        return [Area(**row) for row in rows]


class ProjectModel:
    def __init__(self, db):
        self.db = db

    def get_top_projects(self, limit: int = 10) -> list[Project]:
        """Get top projects by total hours."""
        query = """
            SELECT 
                c.name as calendar_name,
                p.name as name,
                a.name as area_name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN projects p ON e.project_id = p.id
            LEFT JOIN areas a ON p.area_id = a.id
            GROUP BY c.name, p.name, a.name
            ORDER BY total_hours DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (limit,))
        return [Project(**row) for row in rows]


class DatabaseManager:
    def __init__(self):
        self.db_path = Path(DB_FILE)
        self.conn = None
        self.calendar_model = None
        self.area_model = None
        self.project_model = None
        self._init_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.conn.execute("PRAGMA foreign_keys = ON")

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
            print(f"Database error: {e}")
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
