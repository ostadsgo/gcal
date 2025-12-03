# models.py
from dataclasses import dataclass
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db"
DB_FILE = DB_PATH / "data.db"


class Record:
    """Proxy object that makes dict keys accessible as attributes."""

    def __init__(self, data: dict):
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"No attribute '{name}'")

    def __repr__(self):
        return f"Record({self._data})"

    def to_dict(self):
        return self._data.copy()


class CalendarModel:
    def __init__(self, db):
        self.db = db

    def get_calendars_by_usage(self) -> list[Record]:
        """Get calendars sorted by total duration (most used first)."""
        query = """
            SELECT 
                c.id AS calendar_id,
                c.name AS calendar_name,  
                c.color AS calendar_color,  
                COALESCE(SUM(e.duration), 0) AS total_duration, 
                COUNT(e.id) AS total_events,
                COUNT(DISTINCT a.id) AS distinct_areas,
                COUNT(DISTINCT t.id) AS distinct_types,
                COUNT(DISTINCT p.id) AS distinct_projects
            FROM calendars c
            LEFT JOIN events e ON e.calendar_id = c.id
            LEFT JOIN areas a ON a.id = e.area_id
            LEFT JOIN types t ON t.id = e.type_id
            LEFT JOIN projects p ON p.id = e.project_id
            GROUP BY c.id, c.name, c.color
            ORDER BY total_duration DESC;
            """
        rows = self.db.fetch_all(query)
        return [Record(row) for row in rows]

    def get_calendars_alphabetically(self) -> list[Record]:
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
        return [Record(row) for row in rows]

    def get_top_areas(self, calendar_id: int = 1, limit: int = 10) -> list[Record]:
        """Get top areas by total hours."""
        query = """
            SELECT 
                c.name as calendar_name,
                a.id AS area_id,
                a.name as area_name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN areas a ON e.area_id = a.id
            WHERE c.id = ?
            GROUP BY c.name, a.name
            ORDER BY total_hours DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (calendar_id, limit))
        return [Record(row) for row in rows]

    def get_top_types(self, calendar_id: int = 1, limit: int = 10) -> list[Record]:
        """Get top projects by total hours."""
        query = """
            SELECT 
                c.id as calendar_id, 
                c.name as calendar_name,
                t.id AS type_id,
                t.name as type_name,
                a.name as area_name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN types t ON e.id = t.typjjjjjjjjjj
            LEFT JOIN areas a ON p.area_id = a.id
            WHERE c.id = ?
            GROUP BY c.name, p.name, a.name
            ORDER BY total_hours DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (calendar_id, limit))
        return [Record(row) for row in rows]

    def get_top_projects(self, calendar_id: int = 1, limit: int = 10) -> list[Record]:
        """Get top projects by total hours."""
        query = """
            SELECT 
                c.id as calendar_id, 
                c.name as calendar_name,
                p.id AS project_id,
                p.name as project_name,
                a.name as area_name,
                COUNT(e.id) as event_count,
                SUM(e.duration) as total_hours
            FROM calendars c
            JOIN events e ON c.id = e.calendar_id
            JOIN projects p ON e.project_id = p.id
            LEFT JOIN areas a ON p.area_id = a.id
            WHERE c.id = ?
            GROUP BY c.name, p.name, a.name
            ORDER BY total_hours DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (calendar_id, limit))
        return [Record(row) for row in rows]

    def distinct_area(self, calendar_id):
        query = """
            SELECT DISTINCT t.name
            FROM events e
            JOIN areas t ON e.area_id = t.id
            WHERE e.calendar_id = ?
            ORDER BY t.name;
        """
        rows = self.db.fetch_all(query, (calendar_id, ))
        return [Record(row) for row in rows]

    def distinct_types(self, calendar_id):
        query = """
            SELECT DISTINCT t.name
            FROM events e
            JOIN types t ON e.type_id = t.id
            WHERE e.calendar_id = ?
            ORDER BY t.name;
        """
        rows = self.db.fetch_all(query, (calendar_id, ))
        return [Record(row) for row in rows]

    def distinct_projects(self, calendar_id):
        query = """
            SELECT DISTINCT t.name
            FROM events e
            JOIN projects t ON e.project_id = t.id
            WHERE e.calendar_id = ?
            ORDER BY t.name;
        """
        rows = self.db.fetch_all(query, (calendar_id, ))
        return [Record(row) for row in rows]


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

        self.model = CalendarModel(self)

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
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, query, params=()):
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


db = DatabaseManager()
